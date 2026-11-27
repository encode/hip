# Running a server

Use `hip.Server` to accept HTTP requests. Your application receives a
[Request](CORE.md#request) and returns a [Response](CORE.md#response).

## Your first server

Define an application and pass it to the server:

```python
import hip


def app(request):
    return hip.Response(200, content=hip.Text("Hello, world!"))


with hip.Server(app, port=8000) as server:
    print(server.url)
    server.until_interrupt()
```

The server URL is printed alongside the server logs:

```text
http://127.0.0.1:8000/
```

Open this address in a browser to see:

```text
Hello, world!
```

The `with` block starts the server and closes it when the block ends.
`until_interrupt()` keeps it running until you press Ctrl+C.

## Host and port

The default address is `127.0.0.1:8080`. Set `host` and `port` to use another
address:

```python
with hip.Server(app, host="127.0.0.1", port=8000) as server:
    server.until_interrupt()
```

Use `host="0.0.0.0"` to listen on all IPv4 interfaces. Other devices can then
connect using this machine's network address. Also please use an available port,
another server cannot already be listening on it.

*For all examples below, replace the `app` function from the first example and keep the same server block.*

## Reading the request

Read the method, URL, query parameters, and headers from `request`:

```python
def app(request):
    return hip.Response(200, content=hip.JSON({
        "method": str(request.method),
        "path": request.url.path,
        "name": request.url.params.get("name"),
        "accept": request.headers.get("Accept"),
    }))
```

For a GET request to `/hello?name=Hip` with `Accept: application/json`, the
response body is:

```json
{"method":"GET","path":"/hello","name":"Hip","accept":"application/json"}
```

* `request.method` identifies the HTTP method.
* `request.url.path` contains the path without query parameters.
* `request.url.params` provides the query parameters.
* `request.headers` provides case-insensitive access to headers.

## Reading request content

`request.body` contains the request content as bytes. For JSON content, parse it
with `json.loads()`:

```python
import json


def app(request):
    data = json.loads(request.body)
    return hip.Response(200, content=hip.JSON({"message": data["message"]}))
```

Sending `{"message":"Hello"}` returns:

```json
{"message":"Hello"}
```

This example expects valid JSON with a `message` field. Applications should validate incoming
content before using it.

## Returning responses

Choose a content type when constructing a response. hip sets the corresponding
content headers.

### Text

```python
def app(request):
    return hip.Response(200, content=hip.Text("Hello, world!"))
```

### HTML

```python
def app(request):
    return hip.Response(200, content=hip.HTML("<h1>Hello, world!</h1>"))
```

### JSON

```python
def app(request):
    return hip.Response(200, content=hip.JSON({"message": "Hello, world!"}))
```

### Files

```python
def app(request):
    return hip.Response(200, content=hip.File("example.txt"))
```

hip determines its content type from the file extension,
falling back to `application/octet-stream` for unknown types.

## Response headers and status codes

Pass a status code as the first argument and custom headers using `headers`:

```python
def app(request):
    return hip.Response(
        201,
        headers={"X-Example": "hip"},
        content=hip.JSON({"created": True}),
    )
```

This returns `201 Created`, an `X-Example: hip` header, and the JSON body:

```json
{"created":true}
```

See [Core](CORE.md) for the shared request, response, and content models.
