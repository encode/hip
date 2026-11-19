# Change Log

Releases to the `hip` project follow [SEMVER](https://semver.org/).

Since we are currently on [an 0.x series](https://semver.org/#spec-item-4) you should pin releases precisely and review release notes on all updates.

At this point in time, only documented functionality should be considered "Public API".

## Unreleased

* Drop Python 3.10 support. Python 3.11 is now the minimum supported version.

## 0.4

* The server closes quietly when a client disconnects between requests, instead of
logging an internal server error. [#94](https://github.com/encode/hip/pull/94)
* `File.name` is now a property. [#109](https://github.com/encode/hip/pull/109)
* Internal layout changes. [#103](https://github.com/encode/hip/pull/103), [#129](https://github.com/encode/hip/pull/129), [#147](https://github.com/encode/hip/pull/147), [#137](https://github.com/encode/hip/pull/137)

## 0.3

Gzip response decompression. [#70](https://github.com/encode/hip/pull/70)

## 0.2

Initial release of Hip.

HTTP client and server support.

## 0.1

Placeholder.
