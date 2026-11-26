# Devin Review

## Ignore

Skip `plugins/**`. These files come from release tarballs of `chewcorp/minime-coder` and `chewcorp/minime-agents`. They are reviewed in their source repositories, and **Verify vendored plugins** checks that the vendored files match the release byte for byte. Do not raise findings on files under `plugins/`; fixes belong in the source repository.

## Keep reviewing

Review all other files, including the marketplace catalogs and manifests (`.claude-plugin/`, `.cursor-plugin/`, `.grok-plugin/`, and `package.json`), workflows (`.github/workflows/`), scripts (`vendor.sh` and `install.sh`), `tests/`, and `README.md`.
