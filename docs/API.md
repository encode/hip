<h1 style="border: none"><a href="/">hip</a></h1>

## Client

*Explicit open / close... (recommended)*

```python
>>> with hip.Client() as c:
>>>     ...
```

*Simple usage...*

```python
>>> c = hip.Client()
>>> c.close()
```

*Requests...*

```python
>>> c = hip.Client()
>>> r = c.get('https://www.example.com/')
>>> r
<Response [200 OK]>
```

```python
>>> c = hip.Client()
>>> u = hip.URL('https://www.example.com/', params={'search': '...'})
>>> r = c.get(u)
>>> r
<Response [200 OK]>
```

```python
>>> f = hip.Form({'email': '...', 'message': '...'})
>>> r = c.post('https://www.example.com/', content=f)
>>> r
<Response [200 OK]>
```

```python
>>> j = hip.JSON({'title': ..., 'rating': ...})
>>> r = c.put('https://www.example.com/', content=j)
>>> r
<Response [200 OK]>
```

```python
>>> j = hip.JSON({'title': ..., 'rating': ...})
>>> r = c.patch('https://www.example.com/', content=j)
>>> r
<Response [200 OK]>
```

```python
>>> c = hip.Client()
>>> r = c.delete('https://www.example.com/')
>>> r
<Response [200 OK]>
```

```python
>>> c = hip.Client()
>>> r = c.head('https://www.example.com/')
>>> r
<Response [200 OK]>
```

## Server

*Context-managed server...*

```python
>>> with hip.Server(app) as server:
...     print(server.url)
...     server.until_interrupt()
```

The context manager starts the server on entry and shuts it down on exit.

*Address...*

```python
>>> # Serve locally on a fixed port.
>>> with hip.Server(app, host='127.0.0.1', port=8000) as server:
...     print(server.url)
...     server.until_interrupt()
```

```python
>>> # Serve on all interfaces on a fixed port.
>>> with hip.Server(app, host='0.0.0.0', port=8000) as server:
...     print(server.url)
...     server.until_interrupt()
```

---

## Request

```python
>>> r = hip.Request(method, url, headers=..., content=...)
```

*Attributes...*

```python
>>> r = hip.Request('GET', 'https://www.example.com')
>>> r.method
>>> r.url
>>> r.headers
>>> r.content
```

## Response

```python
>>> r = hip.Response(status_code, headers=..., content=...)
```

*Attributes...*

```python
>>> r = hip.Response(200, content=hip.JSON({'message': 'hello, world'}))
>>> r.status_code
>>> r.headers
>>> r.content
```

---

## Method

```python
>>> m = hip.Method('GET')
>>> m == 'GET'
True
>>> str(m)
'GET'
```

## StatusCode

```python
>>> s = hip.StatusCode(200)
>>> s.value, s.reason
(200, 'OK')
>>> s == 200
True
```

*Status classes...*

```python
>>> s = hip.StatusCode(200)
>>> s.is_1xx_informational()
False
>>> s.is_2xx_success()
True
>>> s.is_3xx_redirect()
False
>>> s.is_4xx_client_error()
False
>>> s.is_5xx_server_error()
False
```

## Headers

```python
>>> h = hip.Headers({...})
>>> h['Content-Type']
...
>>> h.get('content-type')
...
```

*Multi-dict...*

```python
>>> h.get_all('set-cookie')
>>> h.multi_items()
```

*Updates...*

```python
>>> h = h.copy_set(...)
>>> h = h.copy_append('set-cookie', 'session_id=...')
>>> h = h.copy_remove(...)
>>> h = h.copy_update(...)
```

## URL

```python
>>> u = hip.URL('...')
>>> u == '...'
True
```

*Query parameters...*

```python
>>> u = hip.URL('...', params={'search': ...})
>>> u.params
<QueryParams ...>
```

*Components...*

```python
>>> u.scheme
>>> u.host
>>> u.port
>>> u.path
>>> u.query
```

```python
>>> u.netloc  # 'example.com:8080'  (HTTP request Host header)
>>> u.target  # '/path?query'       (HTTP request target)
```

*Instantiate from components...*

```python
>>> u = hip.URL(scheme='https', host='www.example.com', path='/')
```

*Updates...*

```python
>>> u = u.copy_with(scheme='https')
```

*Joins...*

```python
>>> u = hip.URL('https://www.example.com/location')
>>> u = u.join('/redirect')
```

## QueryParams

```python
>>> q = hip.QueryParams("...")
>>> q['...']
>>> q.get('...')
```

*Multi-dict...*

```python
>>> q.get_all()
...
>>> q.multi_items()
...
```

*Updates...*

```python
>>> q = q.copy_set('search', '...')
>>> q = q.copy_append('color', 'red')
>>> q = q.copy_remove('ordering')
>>> q = q.copy_update({...})
```

## Content

A `Content` object represents an HTTP message body. Choose one based on the format you
want to send or return.

### Request bodies

Use Form for URL-encoded fields, JSON for JSON data, and MultiPart for form fields
with uploaded files.

```python
client = hip.Client()
content = hip.Form({'email': 'ada@example.com', 'message': 'Hello'})
response = client.post('https://www.example.com/contact', content=content)
```

```python
content = hip.JSON({'title': 'A short guide', 'published': True})
response = client.post('https://www.example.com/articles', content=content)
```

```python
upload = hip.MultiPart(
      form={'description': 'A butterfly'},
      files={'image': hip.File('image.png')},
)
response = client.post('https://www.example.com/images', content=upload)
```

### Response bodies

Use HTML or Text for text, JSON for structured data, and File to send a file’s
contents.

```python
html_content = hip.HTML('<html><body>¡Hola, mundo!</body></html>')
```

```python
text_content = hip.Text('hello, world')
```

```python
json_content = hip.JSON({'message': 'hello, world'})
```

```python
file_content = hip.File('image.png')
response = hip.Response(200, content=file_content)
```

### The Content interface

`Content` describes an HTTP request or response body. Its two core methods are:

* `headers()` returns the body's HTTP headers.
* `open()` returns a `Stream` for reading the body's bytes.

Each call to `open()` creates a new stream. Use a context manager so the stream
is closed when you finish with it, including when an error occurs:

```python
content = hip.JSON({'message': 'hello, world'})
headers = content.headers()

with content.open() as stream:
    body = stream.read()
```

The client or server normally opens content while sending it. Application code
can open it directly when it needs to inspect or transform the bytes.

## Stream

`Stream` is the byte-reading and byte-writing interface used by content and
connections:

```python
stream.read(size: int = -1) -> bytes
stream.write(data: bytes) -> None
stream.close() -> None
```

The Stream interface is public API, although the implementation classes themselves
are private.

### Reading

For `read(size)` with `size > 0`, the result contains at most `size`
bytes. A read may return fewer bytes than requested while more data is still
arriving. A short read does not by itself mean the stream has ended. When the
stream ends, a positive-size read returns b''.

For a content stream or an HTTP response body stream, `read()` or `read(-1)` read
the remaining body.

```python
with content.open() as content_stream:
    body = content_stream.read()
```

To read the body in chunks, keep reading until a positive-size read returns `b''`:

```python
chunks = []
with content.open() as content_stream:
    while chunk := content_stream.read(64 * 1024):
        chunks.append(chunk)

body = b''.join(chunks)
```

### Writing

Content streams returned by `Content.open()` are read-only. Calling `write()` on
one raises `NotImplementedError`.

### Closing

`close()` releases the resource owned by the stream. A stream can also be used
as a context manager; leaving the `with` block calls `close()`, even if the
block raises an exception.

<p align="center">&mdash; 💖 &mdash;</p>
