# hx

```
>>> import hx

>>> cli = hx.Client()
>>> r = cli.get('https://www.example.com/')
>>> r
<Response [200 OK]>
```

```
>>> import hx

>>> def hello_world(request):
...     content = hx.HTML('<body><h1>Hello, world!</h1></body>')
...     return hx.Response(200, content=content)

>>> s = hx.Server(hello_world, addr='http://127.0.0.1:8000/')
>>> s.serve()
```

---

Clients

```python
>>> c = hx.Client()
>>> r = c.get(“https://www.example.com/”)
>>> r
<Response [200 OK]>
```

```python
>>> c = hx.Client()
>>> u = hx.URL(“https://www.example.com/”, params={"search": "..."})
>>> r = c.get(u)
>>> r
<Response [200 OK]>
```

```python
>>> f = hx.Form({"email": "...", "message": "..."})
>>> r = c.post(“https://www.example.com/”, content=f)
>>> r
<Response [200 OK]>
```

```python
>>> j = hx.JSON({"title": ..., "rating": ...})
>>> r = c.put(“https://www.example.com/”, content=j)
>>> r
<Response [200 OK]>
```

```python
>>> j = hx.JSON({"title": ..., "rating": ...})
>>> r = c.patch(“https://www.example.com/”, content=j)
>>> r
<Response [200 OK]>
```

```python
>>> c = hx.Client()
>>> r = c.delete(“https://www.example.com/”)
>>> r
<Response [200 OK]>
```

```python
>>> c = hx.Client()
>>> r = c.head(“https://www.example.com/”)
>>> r
<Response [200 OK]>
>>> r.content
<Empty>
```

*Open / close...*

```
with hx.Client() as c:
    ...
```

```
>>> c = hx.Client()
>>> c.close()
```

Servers

```
>>> s = hx.Server(hello_world)
>>> s.serve(hello_world)  # Serve until Ctrl-C
```

```
>>> with hx.Server(hello_world) as s:
...     # Serve until Ctrl-C, non-blocking
...     print(s.url)
```

*Server address...*

```
>>> # Serve locally, use an unassigned port. 
>>> hx.Server(hello_world, addr='127.0.0.1')
```

```
>>> # Serve locally, use a fixed port.
>>> hx.Server(hello_world, addr='127.0.0.1:8000')
```

```
>>> # Serve globally, use a fixed port.
>>> hx.Server(hello_world, addr='0.0.0.0:8000')
```

```
>>> # Serve globally, enforcing domain name and SSL.
>>> hx.Server(hello_world, addr='https://www.domainname.com')
```

Requests

```
>>> r = hx.Request(method, url, headers=..., content=...)
```

```
>>> r = hx.Request('GET', 'https://www.example.com')
>>> r.method
>>> r.url
>>> r.headers
>>> r.content
```

Responses

```
>>> r = hx.Response(status_code, headers=..., content=...)
```

```
>>> j = hx.JSON({‘message’: ‘hello, world’}
>>> r = hx.Response(200, content=j)
>>> r.status_code
>>> r.headers
>>> r.content
```

Methods

```
>>> m = hx.Method(‘GET’)
>>> m == 'GET'
True
>>> str(m)
'GET'
```

Status Codes

```
>>> s = hx.StatusCode(200)
>>> s.value, s.reason
(200, "OK")
>>> s == 200
True
```

*Classes...*

```
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

Headers

```
>>> h = hx.Headers({...})
>>> h['Content-Type']
...
>>> h.get('content-type')
...
```

*Multi-dict...*

```
>>> h.get_all('set-cookie')
>>> h.multi_items()
```

*Updates...*

```
>>> h.copy_set(...)
>>> h.copy_append('set-cookie', 'session_id=...')
>>> h.copy_remove()
>>> h.copy_update()
```

URLs

```
>>> u = hx.URL('...')
>>> u == '...'
True
```

*Query parameters...*

```
>>> u = hx.URL('...', params={'search': ...})
>>> u.params
<QueryParams ...>
```

*Components...*

```
>>> u.scheme
>>> u.host
>>> u.port
>>> u.path
>>> u.query
```

```
>>> u.netloc  # 'example.com:8080'  (HTTP request Host header)
>>> u.target  # '/path?query'       (HTTP request target)
```

```
>>> hx.URL(scheme='https', host='www.example.com', path='/')
```

*Updates...*

```
>>> u = u.copy_with(scheme='https')
```

*URL joins...*

```
>>> u = hx.URL('https://www.example.com/location')
>>> u = u.join('/redirect')
```

Query Params

```
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

Content Types

*Content Types for Requests...*

```
>>> d = hx.JSON(...)
```

```
>>> f = hx.Form(...)
```

```
>>> m = hx.MultiPart(...)
```

*Content Types for Responses...*

```
>>> h = hx.HTML('<body><h1>Hello, world!</h1></body>')
```

```
>>> t = hx.Text('hello, world')
```

```
>>> j = hx.JSON({'content': ...})
```

```
>>> f = hx.File('image.png')
```
