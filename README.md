<p align="right">en | <a href="es/README.md">es</a> | <a href="fr/README.md">fr</a></p>

# hx

A complete HTTP toolkit.

<br/>

*Making requests with the client...*

```python
>>> import hx

>>> cli = hx.Client()
>>> r = cli.get('https://www.example.com/')
>>> r
<Response [200 OK]>
```

*Serving responses with the server...*

```python
>>> import hx

>>> def app(request):
...     content = hx.HTML('<html><body>¡Hola, mundo!</body></html>')
...     return hx.Response(200, content=content)

>>> s = hx.Server(app, addr='http://127.0.0.1:8000/')
>>> s.serve()
```

---

## API Reference

* [Client](#client)
* [Server](#server)
* [Request](#request)
  * [Method](#method)
  * [URL](#url)
  * [Headers](#headers)
  * [Content](#content)
* [Response](#response)
  * [StatusCode](#statuscode)
  * [Headers](#headers)
  * [Content](#content)

---

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

MIT Licensed. Designed & built with love.

<p align="center">&mdash; 💖 &mdash;</p>
