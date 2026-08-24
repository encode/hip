# Development Scripts

Here's our project scripts, styled after GitHub's [Scripts to Rule Them All](https://github.com/github/scripts-to-rule-them-all) pattern...

* Setup
    * [`install`](install) - Sync the development environment with uv.
* Testing
    * [`test`](test) - Run the tests.
    * [`coverage`](coverage) - Check the test coverage.
    * [`lint`](lint) - Lint and format the source and test files.
* Packaging
    * [`build`](build) - Build the installable package.
    * [`deploy`](deploy) - Upload the installable package to PyPI.
* Documentation
    * [`docs`](docs) - Build or serve the project docs.

Run in local development...

```shell
$ ./scripts/install
$ ./scripts/test && ./scripts/coverage
```

The scripts require [uv](https://docs.astral.sh/uv/) and run commands in the project's `.venv` environment.

Or from the project workflows...

[`.github/workflows/test.yml`](../.github/workflows/test.yml)
