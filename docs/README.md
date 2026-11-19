<p align="center">
  <img width="350" height="208" src="https://www.encode.io/hip/img/butterfly.png" alt="hip">
</p>

# [hip](https://www.encode.io/hip/)

<p align="center">
  <a href="https://github.com/encode/hip/actions/workflows/test.yml">
    <img src="https://github.com/encode/hip/actions/workflows/test.yml/badge.svg?branch=main" alt="Test Suite">
  </a>
  <a href="https://pypi.org/project/hip/">
    <img src="https://img.shields.io/pypi/v/hip" alt="Package version">
  </a>
</p>

Engineered for simplicity, `hip` provides a complete Python web suite&hellip;

* Supports both client and server functionality.
* Presents a clear, simple, and tightly constrained API.
* A minimal, easily readable implementation.

...we're currently in early stages design, and would love for you to get involved.

## Installation

hip requires Python 3.11 or later.

```shell
pip install hip
```

See the [installation guide](https://www.encode.io/hip/installation/) for more options.

## Client

Send an HTTP request:

```python
import hip

with hip.Client() as client:
    response = client.get("https://www.example.com/")
    print(response)
```

```text
<Response [200 OK]>
```

## Server

Run a local HTTP server:

```python
import hip


def app(request):
    return hip.Response(200, content=hip.Text("Hello, world!"))


with hip.Server(app, port=8000) as server:
    server.until_interrupt()
```

Open http://127.0.0.1:8000/ to see `Hello, world!`. Press Ctrl+C to stop the server.

## Documentation

See the [documentation](https://www.encode.io/hip/) for the full guides:

* [Client](https://www.encode.io/hip/client/): making requests.
* [Server](https://www.encode.io/hip/server/): running a server.
* [Core](https://www.encode.io/hip/core/): shared HTTP models and content types.

## Motivation

A clean modern design, with a focused API and an exceptionally light installation footprint.

For comparison, see `hip` <small>vs</small> `requests`&hellip;

```shell
$ uv add hip
$ uv tree --show-sizes --package hip
hip v0.2 (33.5KiB)
└── truststore v0.10.0 (17.8KiB)
```

<p></p>

```shell
$ uv add requests
$ uv tree --show-sizes --package requests
requests v2.33.1 (63.4KiB)
├── certifi v2026.2.25 (150.1KiB)
├── charset-normalizer v3.4.7 (302.4KiB)
├── idna v3.11 (69.3KiB)
└── urllib3 v2.6.3 (128.5KiB)
```

## Contribution

See [Contributing](https://www.encode.io/hip/contributing/) to get involved.

---

<p align="center">
<a href="https://www.encode.io/hip/license/">MIT Licensed</a>.<br/>Designed & Built with Love.
</p>

<p align="center">&mdash; 💖 &mdash;</p>
