# Installation

hip requires Python 3.11 or later.

## Using uv

To try hip in a new project:

```shell
uv init hip-example
cd hip-example
uv add hip
```

For an existing uv project, run `uv add hip` from the project directory.

Create a file named `main.py`:

```python
import hip

url = hip.URL("https://example.com/search?q=python")
print(url.host)
print(url.path)
```

Run the file in the project's environment:

```shell
uv run main.py
```

Expected output:

```text
example.com
/search
```

This example checks that hip is installed without making a network request.

## Using pip

Alternatively, create and activate a virtual environment:

```shell
python3 -m venv .venv
```

On macOS and Linux:

```shell
source .venv/bin/activate
```

On Windows PowerShell:

```shell
.venv\Scripts\Activate.ps1
```

Install hip from PyPI:

```shell
python -m pip install hip
```

Save the same example above as `main.py`, then run:

```shell
python main.py
```

## Checking the installed version

Use Python's package metadata to check which version is installed:

```python
from importlib.metadata import version

print(version("hip"))
```

For hip 0.4, this prints:

```text
0.4
```

See the [changelog](CHANGELOG.md) for release notes.

## Next steps

* [Client](CLIENT.md): send an HTTP request.
* [Server](SERVER.md): run an HTTP server.
* [Core](CORE.md): explore the shared HTTP models.

For work on hip itself, see [Contributing](CONTRIBUTING.md) and the repository's
[development scripts](https://github.com/encode/hip/blob/main/scripts/README.md).
