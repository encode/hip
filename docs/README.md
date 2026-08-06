<p align="center">
  <img width="350" height="208" src="https://raw.githubusercontent.com/encode/httpx/master/docs/img/butterfly.png" alt='hx'>
</p>

# [hx](README.md)

<p style="text-align: center">An HTTP toolkit for folks who give a damn.</p>

<br/>

Engineered for simplicity, `hx` provides a complete Python web suite&hellip;

* Supports both client and server functionality.
* Presents a clear, simple, and tightly constrained API.
* A miminal, easily readable implementation.

## Installation

Install the package from PyPI&hellip;

```bash
$ uv add hx
```

## Client

Sending HTTP requests&hellip;

```python
>>> import hx

>>> cli = hx.Client()
>>> r = cli.get('https://www.example.com/')
>>> r
<Response [200 OK]>
```

## Server

Creating web apps&hellip;

```python
>>> import hx

>>> def app(request):
...     content = hx.HTML('<html><body>¡Hola, mundo!</body></html>')
...     return hx.Response(200, content=content)

>>> s = hx.Server(app)
>>> s.serve()
```

---

## Motivation

A clean modern design, with [a focused API](API.md) and an exceptionally light installation footprint.

For comparison, see `hx` <small>vs</small> `requests`&hellip;

```bash
$ uv add hx
$ uv tree --show-sizes --package hx
hx v1.0.0 (33.5KiB)
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
