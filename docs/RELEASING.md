# Releasing

Hip releases are published to PyPI by GitHub Actions.

1. Open a release PR with the version bump in `pyproject.toml` and the release
   notes in `docs/CHANGELOG.md`. Move the changes being released out of
   `Unreleased` and add a heading for the new version.
2. Merge the PR.
3. Create a [GitHub Release](https://github.com/encode/hip/releases/new) for
   the merged commit. Use the version as the tag (for example, `0.2.1`), set
   the title to `Version 0.2.1`, and use the changelog entry as the release
   description.
4. Publish the GitHub Release. The `Publish` workflow builds the distributions
   and uploads them to PyPI. Check the workflow run in GitHub Actions to confirm
   it succeeded.
