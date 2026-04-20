<p align="center">
  <img width="350" height="208" src="https://raw.githubusercontent.com/encode/httpx/master/docs/img/butterfly.png" alt='HTTPX'>
</p>

# [hx](README.md)

*Installation...*

```bash
uv add https://wwww.encode.io/hx/releases/hx-0.1.tar.gz
```

*Making requests with [the client](API.md#client)...*

```python
>>> import hx

>>> cli = hx.Client()
>>> r = cli.get('https://www.example.com/')
>>> r
<Response [200 OK]>
```

*Serving responses with [the server](API.md#server)...*

```python
>>> import hx

>>> def app(request):
...     content = hx.HTML('<html><body>¡Hola, mundo!</body></html>')
...     return hx.Response(200, content=content)

>>> s = hx.Server(app, addr='http://127.0.0.1:8000/')
>>> s.serve()
```

---

## Motivation

A smart, simple HTTP toolkit.

* Provides both client and server functionality.
* Exceptionally lightweight.
* A [consistent, minimal API](API.md).

## Package sizes

For comparison...

```bash
$ uv add hx
$ uv tree --show-sizes --package hx
hx v0.9.0 (33.5KiB)
└── truststore v0.10.0 (17.8KiB)
```

```bash
$ uv add requests
$ uv tree --show-sizes --package requests
requests v2.33.1 (63.4KiB)
├── certifi v2026.2.25 (150.1KiB)
├── charset-normalizer v3.4.7 (302.4KiB)
├── idna v3.11 (69.3KiB)
└── urllib3 v2.6.3 (128.5KiB)
```

---

[MIT Licensed](LICENSE.md). Designed & built with love.

<p align="center">&mdash; 💖 &mdash;</p>
