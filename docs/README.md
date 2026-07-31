<p align="center">
  <img width="350" height="208" src="https://raw.githubusercontent.com/encode/httpx/master/docs/img/butterfly.png" alt='HTTPX'>
</p>

# [hip](README.md)

<p style="text-align: center">An HTTP toolkit for folks who give a damn.</p>

<br/>

Engineered for simplicity, `hip` provides a complete Python web suite&hellip;

* Supports both client and server functionality.
* Presents a clear, simple, and tightly constrained API.
* A miminal, easily readable implementation.

## Installation

Install the package from PyPI&hellip;

```bash
$ uv add hip
```

## Client

Sending HTTP requests&hellip;

```python
>>> import hip

>>> cli = hip.Client()
>>> r = cli.get('https://www.example.com/')
>>> r
<Response [200 OK]>
```

## Server

Creating web apps&hellip;

```python
>>> import hip

>>> def app(request):
...     content = hip.HTML('<html><body>¡Hola, mundo!</body></html>')
...     return hip.Response(200, content=content)

>>> s = hip.Server(app)
>>> s.serve()
```

---

## Motivation

A clean modern design, with [a focused API](API.md) and an exceptionally light installation footprint.

For comparison, see `hip` <small>vs</small> `requests`&hellip;

```bash
$ uv add hip
$ uv tree --show-sizes --package hip
hip v1.0.0 (33.5KiB)
└── truststore v0.10.0 (17.8KiB)
```

<p></p>

```bash
$ uv add requests
$ uv tree --show-sizes --package requests
requests v2.33.1 (63.4KiB)
├── certifi v2026.2.25 (150.1KiB)
├── charset-normalizer v3.4.7 (302.4KiB)
├── idna v3.11 (69.3KiB)
└── urllib3 v2.6.3 (128.5KiB)
```

## Contribution

We have a transparent development model, and welcome feedback.

Pull requests are restricted to team members only.

---

<p align="center">
<a href="LICENSE.md">MIT Licensed</a>.<br/>Designed & Built with Love.
</p>

<p align="center">&mdash; 💖 &mdash;</p>
