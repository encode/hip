import hip


def app(request):
    content = hip.HTML("<html><body>¡Hola, mundo!</body></html>")
    return hip.Response(200, content=content)


def test_server_defaults():
    server = hip.Server(app)

    assert server.host == "127.0.0.1"
    assert server.port == 8080
    assert server.url == "http://127.0.0.1:8080/"


def test_server_custom_host_and_port():
    server = hip.Server(app, host="0.0.0.0", port=8000)

    assert server.host == "0.0.0.0"
    assert server.port == 8000
    assert server.url == "http://0.0.0.0:8000/"


def test_server_defaults_headers():
    with hip.Server(app) as server, hip.Client() as client:
        response = client.get(server.url)
        assert response.headers["Server"] == "hip/dev"
        assert response.headers["Connection"] == "keep-alive"
        assert response.headers["Date"].endswith("GMT")
