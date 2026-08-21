# Development Scripts

Here's our project scripts, styled after GitHub's [Scripts to Rule Them All](https://github.com/github/scripts-to-rule-them-all) pattern...

* Setup
    * [`install`](install) - Install the development dependencies.
* Testing
    * [`test`](test) - Run the tests.
    * [`coverage`](coverage) - Check the test coverage.
* Packaging
    * [`butild`](build) - Build the installable package.
    * [`deploy`](deploy) - Upload the installable package to PyPI.
* Documentation
    * [`docs`](docs) - Build or serve the project docs.

Run in local development...

```shell
$ ./scripts/install
$ ./scripts/test && ./scripts/coverage
```

Or from the project workflows...

[`.github/workflows/test.yml`](../.github/workflows/test.yml)
