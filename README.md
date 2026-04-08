# hx

A complete HTTP toolkit.

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

*Designed for simplicity.*

---

## Client

```python
>>> c = hx.Client()
>>> r = c.get('https://www.example.com/')
>>> r
<Response [200 OK]>
```

```python
>>> c = hx.Client()
>>> u = hx.URL('https://www.example.com/', params={'search': '...'})
>>> r = c.get(u)
>>> r
<Response [200 OK]>
```

```python
>>> f = hx.Form({'email': '...', 'message': '...'})
>>> r = c.post('https://www.example.com/', content=f)
>>> r
<Response [200 OK]>
```

```python
>>> j = hx.JSON({'title': ..., 'rating': ...})
>>> r = c.put('https://www.example.com/', content=j)
>>> r
<Response [200 OK]>
```

```python
>>> j = hx.JSON({'title': ..., 'rating': ...})
>>> r = c.patch('https://www.example.com/', content=j)
>>> r
<Response [200 OK]>
```

```python
>>> c = hx.Client()
>>> r = c.delete('https://www.example.com/')
>>> r
<Response [200 OK]>
```

```python
>>> c = hx.Client()
>>> r = c.head('https://www.example.com/')
>>> r
<Response [200 OK]>
>>> r.content
<Empty>
```

*Open / Close...*

```python
>>> with hx.Client() as c:
>>>     ...
```

```python
>>> c = hx.Client()
>>> c.close()
```

## Server

```python
>>> s = hx.Server(app)
>>> s.serve()  # Serve until Ctrl-C
```

```python
>>> with hx.Server(app) as s:
...     # Serve until Ctrl-C, non-blocking
...     print(s.url)
```

*Address...*

```python
>>> # Serve locally, use an unassigned port. 
>>> s = hx.Server(app, addr='127.0.0.1')
```

```python
>>> # Serve locally, use a fixed port.
>>> s = hx.Server(app, addr='127.0.0.1:8000')
```

```python
>>> # Serve globally, use a fixed port.
>>> s = hx.Server(app, addr='0.0.0.0:8000')
```

```python
>>> # Serve globally, enforcing domain name and SSL.
>>> s = hx.Server(app, addr='https://www.domainname.com')
```

---

## Requests

```python
>>> r = hx.Request(method, url, headers=..., content=...)
```

*Attributes...*

```python
>>> r = hx.Request('GET', 'https://www.example.com')
>>> r.method
>>> r.url
>>> r.headers
>>> r.content
```

## Responses

```python
>>> r = hx.Response(status_code, headers=..., content=...)
```

*Attributes...*

```python
>>> r = hx.Response(200, content=hx.JSON({'message': 'hello, world'})
>>> r.status_code
>>> r.headers
>>> r.content
```

---

## Methods

```python
>>> m = hx.Method(‘GET’)
>>> m == 'GET'
True
>>> str(m)
'GET'
```

## Status Codes

```python
>>> s = hx.StatusCode(200)
>>> s.value, s.reason
(200, "OK")
>>> s == 200
True
```

*Status classes...*

```python
>>> s = hx.StatusCode(200)
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
>>> h = hx.Headers({...})
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

## URLs

```python
>>> u = hx.URL('...')
>>> u == '...'
True
```

*Query parameters...*

```python
>>> u = hx.URL('...', params={'search': ...})
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
>>> u = hx.URL(scheme='https', host='www.example.com', path='/')
```

*Updates...*

```python
>>> u = u.copy_with(scheme='https')
```

*Joins...*

```python
>>> u = hx.URL('https://www.example.com/location')
>>> u = u.join('/redirect')
```

## Query Params

```python
>>> q = hx.QueryParams("...")
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

## Content Types

*Content types for requests...*

```python
>>> j = hx.JSON(...)
```

```python
>>> f = hx.Form(...)
```

```python
>>> m = hx.MultiPart(...)
```

*Content types for responses...*

```python
>>> h = hx.HTML('<body><h1>Hello, world!</h1></body>')
```

```python
>>> t = hx.Text('hello, world')
```

```python
>>> j = hx.JSON({'content': ...})
```

```python
>>> f = hx.File('image.png')
```

---

## Package sizes

For comparison...

package        |  size  |   SLOC
---------------|--------|-------
`hx`           |  34kB  | ~2,500
`+ truststore` |  19kB  |
 
package                |  size |   SLOC
-----------------------|-------|-------
`requests`             |  64kB | ~3,000
`+ urllib3`            | 131kB | ~6,800
`+ certifi`            | 153kB |
`+ charset_normalizer` | 309kB |
`+ idna`               |  71kB |

package      | size  |   SLOC
-------------|-------|-------
`httpx`      |  73kB | ~5,600
`+ httpcore` |  78kB | ~4,800
`+ h11`      |  37kB | ~3,100
`+ certifi`  | 153kB |
`+ anyio`    | 114kB |
`+ idna`     |  71kB |
