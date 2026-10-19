# actions

Composite GitHub Actions shared by my projects.

| Action | What it does |
|---|---|
| [`validate-tag`](validate-tag) | Checks that a release tag (`vX.Y.Z`) matches `__version__` in a Python file, as PEP 440 versions |
| [`git-cliff`](git-cliff) | Generates release notes with [git-cliff](https://git-cliff.org), with a default config: the annotated tag's message as intro, then the commits grouped by Conventional Commits type |

## Usage

```yaml
on:
  push:
    tags: ["v*"]

jobs:
  release:
    runs-on: ubuntu-24.04
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v7
        with:
          fetch-depth: 0  # git-cliff needs the history and the tags

      - uses: pgmesa/actions/validate-tag@validate-tag/v1.0.0
        with:
          tag: ${{ github.ref_name }}
          version-file: mypackage/__init__.py

      - id: notes
        uses: pgmesa/actions/git-cliff@git-cliff/v1.0.0
        with:
          args: --latest --strip header

      - run: gh release create "$GITHUB_REF_NAME" --verify-tag --notes-file "${{ steps.notes.outputs.file }}"
        env:
          GH_TOKEN: ${{ github.token }}
```

`validate-tag` outputs the normalized `version` (`v0.2.0-rc.1` -> `0.2.0rc1`).
`git-cliff` takes a `config` of the calling repository instead of
[the default one](git-cliff/cliff.toml) and outputs the generated `file` and
`content`. To give a release an intro, tag it with a message:
`git tag -a v1.2.3 -F notes.md`.

## Versioning

Each action has its own versions, tagged as `<action>/vX.Y.Z`
(`validate-tag/v1.0.0`). Tags are never moved: reference an exact version and
bump it on purpose.
