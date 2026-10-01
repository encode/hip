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

*Explicit open / close... (recommended)*

```python
>>> with hip.Server(app) as s:
...     # Serve until Ctrl-C, non-blocking
...     print(s.url)
```

*Simple usage...*

```python
>>> s = hip.Server(app)
>>> s.serve()  # Serve until Ctrl-C
```

*Address...*

```python
>>> # Serve locally on a fixed port.
>>> s = hip.Server(app, host='127.0.0.1', port=8000)
```

```python
>>> # Serve on all interfaces on a fixed port.
>>> s = hip.Server(app, host='0.0.0.0', port=8000)
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

*Content types for requests...*

```python
>>> j = hip.JSON(...)
```

```python
>>> f = hip.Form(...)
```

```python
>>> m = hip.MultiPart(...)
```

*Content types for responses...*

```python
>>> h = hip.HTML('<html><body>¡Hola, mundo!</body></html>')
```

```python
>>> t = hip.Text('hello, world')
```

```python
>>> j = hip.JSON({'content': ...})
```

```python
>>> f = hip.File('image.png')
```

<p align="center">&mdash; 💖 &mdash;</p>
