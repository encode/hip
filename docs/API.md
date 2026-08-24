<h1 style="border: none"><a href="/">httpx</a></h1>

---

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

## Client

*Explicit open / close... (recommended)*

```python
>>> with httpx.Client() as c:
>>>     ...
```

*Simple usage...*

```python
>>> c = httpx.Client()
>>> c.close()
```

*Requests...*

```python
>>> c = httpx.Client()
>>> r = c.get('https://www.example.com/')
>>> r
<Response [200 OK]>
```

```python
>>> c = httpx.Client()
>>> u = httpx.URL('https://www.example.com/', params={'search': '...'})
>>> r = c.get(u)
>>> r
<Response [200 OK]>
```

```python
>>> f = httpx.Form({'email': '...', 'message': '...'})
>>> r = c.post('https://www.example.com/', content=f)
>>> r
<Response [200 OK]>
```

```python
>>> j = httpx.JSON({'title': ..., 'rating': ...})
>>> r = c.put('https://www.example.com/', content=j)
>>> r
<Response [200 OK]>
```

```python
>>> j = httpx.JSON({'title': ..., 'rating': ...})
>>> r = c.patch('https://www.example.com/', content=j)
>>> r
<Response [200 OK]>
```

```python
>>> c = httpx.Client()
>>> r = c.delete('https://www.example.com/')
>>> r
<Response [200 OK]>
```

```python
>>> c = httpx.Client()
>>> r = c.head('https://www.example.com/')
>>> r
<Response [200 OK]>
```

## Server

*Explicit open / close... (recommended)*

```python
>>> with httpx.Server(app) as s:
...     # Serve until Ctrl-C, non-blocking
...     print(s.url)
```

*Simple usage...*

```python
>>> s = httpx.Server(app)
>>> s.serve()  # Serve until Ctrl-C
```

*Address...*

```python
>>> # Serve locally on a fixed port.
>>> s = httpx.Server(app, host='127.0.0.1', port=8000)
```

```python
>>> # Serve on all interfaces on a fixed port.
>>> s = httpx.Server(app, host='0.0.0.0', port=8000)
```

---

## Request

```python
>>> r = httpx.Request(method, url, headers=..., content=...)
```

*Attributes...*

```python
>>> r = httpx.Request('GET', 'https://www.example.com')
>>> r.method
>>> r.url
>>> r.headers
>>> r.content
```

## Response

```python
>>> r = httpx.Response(status_code, headers=..., content=...)
```

*Attributes...*

```python
>>> r = httpx.Response(200, content=httpx.JSON({'message': 'hello, world'}))
>>> r.status_code
>>> r.headers
>>> r.content
```

---

## Method

```python
>>> m = httpx.Method('GET')
>>> m == 'GET'
True
>>> str(m)
'GET'
```

## StatusCode

```python
>>> s = httpx.StatusCode(200)
>>> s.value, s.reason
(200, 'OK')
>>> s == 200
True
```

*Status classes...*

```python
>>> s = httpx.StatusCode(200)
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
>>> h = httpx.Headers({...})
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
>>> u = httpx.URL('...')
>>> u == '...'
True
```

*Query parameters...*

```python
>>> u = httpx.URL('...', params={'search': ...})
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
>>> u = httpx.URL(scheme='https', host='www.example.com', path='/')
```

*Updates...*

```python
>>> u = u.copy_with(scheme='https')
```

*Joins...*

```python
>>> u = httpx.URL('https://www.example.com/location')
>>> u = u.join('/redirect')
```

## QueryParams

```python
>>> q = httpx.QueryParams("...")
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
>>> j = httpx.JSON(...)
```

```python
>>> f = httpx.Form(...)
```

```python
>>> m = httpx.MultiPart(...)
```

*Content types for responses...*

```python
>>> h = httpx.HTML('<html><body>¡Hola, mundo!</body></html>')
```

```python
>>> t = httpx.Text('hello, world')
```

```python
>>> j = httpx.JSON({'content': ...})
```

```python
>>> f = httpx.File('image.png')
```

<p align="center">&mdash; 💖 &mdash;</p>
