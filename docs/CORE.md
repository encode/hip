# Core

The [client](CLIENT.md) and [server](SERVER.md) use the same HTTP models.
These examples work locally without sending requests.

## Request

`hip.Request` represents an HTTP request. Pass a method and URL, with optional
headers and content:

```python
import hip

request = hip.Request(
    "POST",
    "https://example.com/messages",
    headers={"Accept": "application/json"},
    content=hip.JSON({"message": "Hello"}),
)

print(request.method)
print(request.url)
print(request.headers["Accept"])
print(request.content["message"])
print(request.body)
```

```text
POST
https://example.com/messages
application/json
Hello
b'{"message":"Hello"}'
```

* `method` is a `hip.Method` instance.
* `url` is a `hip.URL` instance.
* `headers` contains the request headers.
* `content` holds the content object.
* `body` returns the content as bytes.

Constructing a Request does not send it. See [Making requests](CLIENT.md) for
client usage and [Running a server](SERVER.md) for incoming requests.

## Response

`hip.Response` represents an HTTP response. Pass a status code, with optional
headers and content:

```python
import hip

response = hip.Response(
    200,
    headers={"X-Example": "hip"},
    content=hip.JSON({"message": "Hello"}),
)

print(response)
print(response.headers["X-Example"])
print(response.content["message"])
print(response.body)
```

```text
<Response [200 OK]>
hip
Hello
b'{"message":"Hello"}'
```

* `status_code` is a `hip.StatusCode` instance.
* `headers` contains the response headers.
* `content` holds the content object.
* `body` returns the content as bytes.

Request and Response include the headers supplied by their content, such as
`Content-Type` and `Content-Length` for JSON.

## Method

`hip.Method` represents an HTTP method and normalizes its name to uppercase:

```python
import hip

method = hip.Method("get")
print(str(method))
print(method == "GET")
```

```text
GET
True
```

Standard method names are checked by default; an unknown method raises
`ValueError`.

## StatusCode

`hip.StatusCode` provides the numeric status and its reason phrase:

```python
import hip

status = hip.StatusCode(200)
print(status.value)
print(status.reason_phrase)
print(str(status))
print(status == 200)
```

```text
200
OK
200 OK
True
```

Use these helpers to check the status class:

```python
import hip

status = hip.StatusCode(200)
print(status.is_1xx_informational())
print(status.is_2xx_success())
print(status.is_3xx_redirect())
print(status.is_4xx_client_error())
print(status.is_5xx_server_error())
```

```text
False
True
False
False
False
```

## Headers

`hip.Headers` stores HTTP headers and supports case-insensitive lookup:

```python
import hip

headers = hip.Headers({"Content-Type": "application/json"})
print(headers["Content-Type"])
print(headers.get("content-type"))
print(headers.get("X-Missing"))
```

```text
application/json
application/json
None
```

Indexing a missing header raises `KeyError`; `get()` returns `None` or a supplied
default. Use `items()` to iterate over the header names and values.

### Updating headers

The `copy_*` methods return a new Headers object, leaving the original unchanged:

```python
import hip

headers = hip.Headers({"Accept": "text/plain", "X-Example": "hip"})
updated = headers.copy_set("Accept", "application/json")
updated = updated.copy_update({"User-Agent": "hip-example"})
updated = updated.copy_remove("X-Example")

print(headers["Accept"])
print(updated["Accept"])
print(updated["User-Agent"])
print("X-Example" in updated)
```

```text
text/plain
application/json
hip-example
False
```

## URL

`hip.URL` represents a URL and its components:

```python
import hip

url = hip.URL("https://example.com:8443/search?q=python#results")
print(url.scheme)
print(url.host)
print(url.port)
print(url.path)
print(url.query)
print(url.fragment)
print(url.netloc)
print(url.target)
```

```text
https
example.com
8443
/search
b'q=python'
results
example.com:8443
/search?q=python
```

* `query` is the encoded query string as bytes, without the leading `?`.
* `netloc` contains the host and optional port, as used in a Host header.
* `target` contains the encoded path and query string, without the fragment.

URLs can also be compared with strings:

```python
import hip

url = hip.URL("https://example.com/search")
print(url == "https://example.com/search")
```

```text
True
```

### Query parameters

Use `params` to build a query string, and `url.params` to read it:

```python
import hip

url = hip.URL("https://example.com/search", params={"q": "python http"})
print(url)
print(url.params["q"])
```

```text
https://example.com/search?q=python+http
python http
```

### Building and updating URLs

Build a URL from components and use `copy_with()` to change a copy:

```python
import hip

url = hip.URL(scheme="https", host="example.com", path="/messages")
updated = url.copy_with(path="/users")
print(url)
print(updated)
```

```text
https://example.com/messages
https://example.com/users
```

Use `join()` to resolve another URL against a base URL:

```python
import hip

url = hip.URL("https://example.com/messages/")
print(url.join("/users"))
```

```text
https://example.com/users
```

## QueryParams

`hip.QueryParams` stores query parameters, including repeated keys:

```python
import hip

params = hip.QueryParams("color=red&color=blue&page=1")
print(params["color"])
print(params.get("missing"))
print(params.get_list("color"))
print(params.multi_items())
```

```text
red
None
['red', 'blue']
[('color', 'red'), ('color', 'blue'), ('page', '1')]
```

Indexing or `get()` returns the first value for a key. `get_list()` returns all
its values, and `multi_items()` returns every key-value pair. `items()` returns
one pair per key, using the first value.

### Updating query parameters

The `copy_*` methods return a new QueryParams object without changing the original.

* `copy_set()` sets a key to a single value.
* `copy_append()` adds another value for a key.
* `copy_remove()` removes a key and its values.
* `copy_update()` merges parameters, replacing values for matching keys.

```python
import hip

params = hip.QueryParams("color=red&page=1")

updated = params.copy_set("page", "2")
print(updated)

updated = updated.copy_append("color", "blue")
print(updated)

updated = updated.copy_remove("page")
print(updated)

updated = updated.copy_update({"search": "python"})
print(updated)

print(params)
```

```text
color=red&page=2
color=red&color=blue&page=2
color=red&color=blue
color=red&color=blue&search=python
color=red&page=1
```

The last line shows that `params` is unchanged.

## Content

Content objects describe a request or response body and its headers.
Pass them to Request or Response using `content=`.

| Type | Content |
| --- | --- |
| `hip.JSON` | JSON data |
| `hip.Text` | UTF-8 text |
| `hip.HTML` | UTF-8 HTML |
| `hip.Binary` | Raw bytes |
| `hip.Form` | URL-encoded form fields |
| `hip.File` | A file on disk |
| `hip.Files` | File fields for a multipart upload |
| `hip.MultiPart` | Form fields and files in a multipart body |

### JSON

`hip.JSON` encodes Python data as JSON. Access values by key, or use `.value`
to get a copy of the underlying data:

```python
import hip

content = hip.JSON({"message": "Hello"})
print(content["message"])
print(content.value)
print(bytes(content))
print(content.headers()["Content-Type"])
```

```text
Hello
{'message': 'Hello'}
b'{"message":"Hello"}'
application/json
```

### Text, HTML, and binary content

Use Text and HTML for strings, or Binary for bytes:

```python
import hip

print(bytes(hip.Text("Hello")))
print(bytes(hip.HTML("<h1>Hello</h1>")))
print(bytes(hip.Binary(b"Hello")))
```

```text
b'Hello'
b'<h1>Hello</h1>'
b'Hello'
```

### Form data

`hip.Form` encodes form fields and supports repeated values:

```python
import hip

content = hip.Form({"name": "Hip", "color": ["red", "blue"]})
print(content["name"])
print(content.get_list("color"))
print(bytes(content))
print(content.headers()["Content-Type"])
```

```text
Hip
['red', 'blue']
b'name=Hip&color=red&color=blue'
application/x-www-form-urlencoded
```

### Files and multipart content

`hip.File` refers to a file on disk. The path must point to an existing file
when reading the content or generating its headers:

```python
import hip

content = hip.File("example.txt")
print(content.name)
with content.open() as stream:
    print(stream.read())
```

For an `example.txt` file containing `Hello from hip!`, the output is:

```text
example.txt
b'Hello from hip!'
```

Use `hip.MultiPart` to combine form fields and files:

```python
import hip

content = hip.MultiPart(
    form={"description": "Example upload"},
    files={"file": hip.File("example.txt")},
)
print(content.form["description"])
print(content.files["file"].name)
```

```text
Example upload
example.txt
```

`hip.Files` can also be passed directly as request content for a files-only
multipart upload. See [Uploading files](CLIENT.md#uploading-files) for a full
request example.

### Content headers and streams

`headers()` returns the content headers. `open()` returns a stream for reading
the content:

```python
import hip

content = hip.Text("Hello")
print(content.headers()["Content-Type"])
with content.open() as stream:
    print(stream.read())
```

```text
text/plain; charset='utf-8'
b'Hello'
```

Some content types, such as multipart content, must be read through `open()`
rather than `bytes()`. Use a `with` block to close the stream when finished.
