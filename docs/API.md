<h1 style="border: none"><a href="/">hipx</a></h1>

## Client

*Explicit open / close... (recommended)*

```python
>>> with hipx.Client() as c:
>>>     ...
```

*Simple usage...*

```python
>>> c = hipx.Client()
>>> c.close()
```

*Requests...*

```python
>>> c = hipx.Client()
>>> r = c.get('https://www.example.com/')
>>> r
<Response [200 OK]>
```

```python
>>> c = hipx.Client()
>>> u = hipx.URL('https://www.example.com/', params={'search': '...'})
>>> r = c.get(u)
>>> r
<Response [200 OK]>
```

```python
>>> f = hipx.Form({'email': '...', 'message': '...'})
>>> r = c.post('https://www.example.com/', content=f)
>>> r
<Response [200 OK]>
```

```python
>>> j = hipx.JSON({'title': ..., 'rating': ...})
>>> r = c.put('https://www.example.com/', content=j)
>>> r
<Response [200 OK]>
```

```python
>>> j = hipx.JSON({'title': ..., 'rating': ...})
>>> r = c.patch('https://www.example.com/', content=j)
>>> r
<Response [200 OK]>
```

```python
>>> c = hipx.Client()
>>> r = c.delete('https://www.example.com/')
>>> r
<Response [200 OK]>
```

```python
>>> c = hipx.Client()
>>> r = c.head('https://www.example.com/')
>>> r
<Response [200 OK]>
```

## Server

*Explicit open / close... (recommended)*

```python
>>> with hipx.Server(app) as s:
...     # Serve until Ctrl-C, non-blocking
...     print(s.url)
```

*Simple usage...*

```python
>>> s = hipx.Server(app)
>>> s.serve()  # Serve until Ctrl-C
```

*Address...*

```python
>>> # Serve locally on a fixed port.
>>> s = hipx.Server(app, host='127.0.0.1', port=8000)
```

```python
>>> # Serve on all interfaces on a fixed port.
>>> s = hipx.Server(app, host='0.0.0.0', port=8000)
```

---

## Request

```python
>>> r = hipx.Request(method, url, headers=..., content=...)
```

*Attributes...*

```python
>>> r = hipx.Request('GET', 'https://www.example.com')
>>> r.method
>>> r.url
>>> r.headers
>>> r.content
```

## Response

```python
>>> r = hipx.Response(status_code, headers=..., content=...)
```

*Attributes...*

```python
>>> r = hipx.Response(200, content=httpx.JSON({'message': 'hello, world'}))
>>> r.status_code
>>> r.headers
>>> r.content
```

---

## Method

```python
>>> m = hipx.Method('GET')
>>> m == 'GET'
True
>>> str(m)
'GET'
```

## StatusCode

```python
>>> s = hipx.StatusCode(200)
>>> s.value, s.reason
(200, 'OK')
>>> s == 200
True
```

*Status classes...*

```python
>>> s = hipx.StatusCode(200)
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
>>> h = hipx.Headers({...})
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
>>> u = hipx.URL('...')
>>> u == '...'
True
```

*Query parameters...*

```python
>>> u = hipx.URL('...', params={'search': ...})
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
>>> u = hipx.URL(scheme='https', host='www.example.com', path='/')
```

*Updates...*

```python
>>> u = u.copy_with(scheme='https')
```

*Joins...*

```python
>>> u = hipx.URL('https://www.example.com/location')
>>> u = u.join('/redirect')
```

## QueryParams

```python
>>> q = hipx.QueryParams("...")
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

*Content types for requests...*

```python
>>> j = hipx.JSON(...)
```

```python
>>> f = hipx.Form(...)
```

```python
>>> m = hipx.MultiPart(...)
```

*Content types for responses...*

```python
>>> h = hipx.HTML('<html><body>¡Hola, mundo!</body></html>')
```

```python
>>> t = hipx.Text('hello, world')
```

```python
>>> j = hipx.JSON({'content': ...})
```

```python
>>> f = hipx.File('image.png')
```

<p align="center">&mdash; 💖 &mdash;</p>
