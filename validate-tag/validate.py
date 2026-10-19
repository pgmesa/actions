"""Check that a release tag (vX.Y.Z) matches the __version__ of the code.

Both are compared as PEP 440 versions, the way pip and PyPI see them: tag
v0.2.0rc1 matches "0.2.0rc1" and "0.2.0-rc.1", which normalize to the same
version. The normalized version is written to the step outputs.
"""
import os
import ast
import sys
import argparse
from pathlib import Path

from packaging.version import Version, InvalidVersion


def error(message):
    print(f"::error::{message}")
    sys.exit(1)


def extract_version(version_file):
    tree = ast.parse(version_file.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign):
            targets = node.targets
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            targets = [node.target]
        else:
            continue
        if any(getattr(target, "id", None) == "__version__" for target in targets):
            return ast.literal_eval(node.value)
    raise RuntimeError(f"__version__ not found in {version_file}")


def parse_version(version, source):
    try:
        parsed = Version(version)
    except InvalidVersion:
        error(f"{source} is not a valid PEP 440 version: {version}")
    if parsed.local is not None:
        error(f"{source} has a local version label, which PyPI rejects: {version}")
    return parsed


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--tag", required=True)
    parser.add_argument("--version-file", required=True, type=Path)
    args = parser.parse_args()

    if not args.tag.startswith("v"):
        error(f"tag must start with 'v' (e.g. v1.2.3): {args.tag}")
    tag_version = parse_version(args.tag[1:], "tag")

    if not args.version_file.is_file():
        error(f"version file not found: {args.version_file}")
    try:
        code_version = parse_version(extract_version(args.version_file), args.version_file)
    except Exception as e:
        error(f"failed to read __version__: {e}")

    if tag_version != code_version:
        error(f"version mismatch: tag {args.tag}, {args.version_file} {code_version}")

    print(f"OK: {args.tag} matches {args.version_file} ({code_version})")
    if "GITHUB_OUTPUT" in os.environ:
        with open(os.environ["GITHUB_OUTPUT"], "a") as f:
            f.write(f"version={code_version}\n")


if __name__ == "__main__":
    main()
