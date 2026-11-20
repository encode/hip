# Making requests

Use `hip.Client` to send HTTP requests and read responses.

Before you begin, please follow the [installation guide](INSTALLATION.md).

## Send your first request

### Using a context manager (recommended)

Send a GET request:

```python
import hip

with hip.Client() as client:
    response = client.get("https://www.example.com/")
    print(response)
```

With a successful response from example.com, the output is:

```text
<Response [200 OK]>
```

`client.get()` sends a GET request and returns a
[Response](CORE.md#response).

The `with` block closes the client and its connections when it ends.

### Closing the client explicitly

If you create a client without a `with` block, close it when you are done:

```python
import hip

client = hip.Client()

try:
    response = client.get("https://www.example.com/")
    print(response)
finally:
    client.close()
```

```text
<Response [200 OK]>
```

The `finally` block closes the client even if the request raises an exception.

## Read the response

A response provides a status code, headers, parsed content, and a body as bytes:

```python
import hip

with hip.Client() as client:
    response = client.get("https://www.example.com/")

    print("Status:", response.status_code)
    print("Success:", response.status_code.is_2xx_success())
    print("Content type:", response.headers.get("Content-Type"))
    print("Body:")
    print(response.body)
```

For a successful HTML response, the output starts with:

```text
Status: 200 OK
Success: True
Content type: text/html; charset='utf-8'
Body:
```

* `response.status_code` is the HTTP status.
* `is_2xx_success()` checks for a 2xx response.
* `response.headers` contains the response headers.
* `response.content` is the parsed content, like `hip.HTML`, `hip.JSON`, or `hip.Binary`.
* `response.body` returns the content as bytes.

See [StatusCode](CORE.md#statuscode) and [Headers](CORE.md#headers) for more details.

## Query parameters

Pass query parameters to `hip.URL` using `params`. hip encodes them in the URL.
The following examples use [httpbin](https://httpbin.org/), which echoes requests
back as JSON.

```python
import hip

url = hip.URL(
    "https://httpbin.org/get",
    params={"search": "python http", "page": "1"},
)

with hip.Client() as client:
    response = client.get(url)
    print(response.content["args"]["search"])
```

```text
python http
```

## Request headers

Use `headers` to add headers to an individual request:

```python
import hip

with hip.Client() as client:
    response = client.get(
        "https://httpbin.org/get",
        headers={"Accept": "application/json"},
    )
    print(response.content["headers"]["Accept"])
```

```text
application/json
```

For a JSON response, `response.content` is a `hip.JSON` object that supports
access by key.

## Sending JSON

Wrap your data in `hip.JSON` and pass it as `content`:

```python
import hip

with hip.Client() as client:
    response = client.post(
        "https://httpbin.org/post",
        content=hip.JSON({"title": "Hello", "published": False}),
    )
    print(response.content["json"]["title"])
```

```text
Hello
```

hip sets the `Content-Type` header to `application/json`.

## Sending form data

Use `hip.Form` to send URL-encoded form data:

```python
import hip

with hip.Client() as client:
    response = client.post(
        "https://httpbin.org/post",
        content=hip.Form({"name": "Hip", "message": "Hello"}),
    )
    print(response.content["form"]["name"])
```

```text
Hip
```

hip sets the `Content-Type` header to `application/x-www-form-urlencoded`.

## Uploading files

Use `hip.MultiPart` to send files and form fields in the same request:

```python
import hip

content = hip.MultiPart(
    form={"description": "Example upload"},
    files={"file": hip.File("example.txt")},
)

with hip.Client() as client:
    response = client.post("https://httpbin.org/post", content=content)
    print(response)
    print(response.content["form"]["description"])
```

```text
<Response [200 OK]>
Example upload
```

`example.txt` must exist at the given path. The `file` key is the form field name;
`hip.File` provides the file content.

hip sets the multipart `Content-Type` header and boundary automatically.

## Other HTTP methods

PUT and PATCH accept content in the same way as POST:

```python
import hip

with hip.Client() as client:
    response = client.put(
        "https://httpbin.org/put",
        content=hip.JSON({"title": "Hello", "published": True}),
    )
    print(response)

    response = client.patch(
        "https://httpbin.org/patch",
        content=hip.JSON({"published": False}),
    )
    print(response)

    response = client.delete("https://httpbin.org/delete")
    print(response)
```

```text
<Response [200 OK]>
<Response [200 OK]>
<Response [200 OK]>
```

## HEAD requests

HEAD requests return response headers without a response body.

```python
import hip

with hip.Client() as client:
    response = client.head("https://www.example.com/")
    print(response)
```

Expected response:

```text
<Response [200 OK]>
```

## Timeouts

Use `hip.backends.timeout()` to set a time limit, in seconds, for network operations
inside the block:

```python
import hip

with hip.Client() as client:
    try:
        with hip.backends.timeout(5):
            response = client.get("https://www.example.com/")
            print(response)
    except TimeoutError:
        print("The request timed out.")
```

A successful request prints:

```text
<Response [200 OK]>
```
If the time limit is reached, `TimeoutError` is raised.
Without a timeout block, hip does not set a network timeout.

## Reusing a client

Use one client for multiple requests so connections can be reused. You can also
set a base URL when creating the client:

```python
import hip

with hip.Client("https://httpbin.org") as client:
    first = client.get("/get")
    second = client.get("/get")
    print(first)
    print(second)
```

```text
<Response [200 OK]>
<Response [200 OK]>
```
