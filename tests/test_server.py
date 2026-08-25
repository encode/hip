import httpx


def app(request):
    content = httpx.HTML('<html><body>¡Hola, mundo!</body></html>')
    return httpx.Response(200, content=content)


def test_server_defaults():
    server = httpx.Server(app)

    assert server.host == '127.0.0.1'
    assert server.port == 8080
    assert server.url == 'http://127.0.0.1:8080/'


def test_server_custom_host_and_port():
    server = httpx.Server(app, host='0.0.0.0', port=8000)

    assert server.host == '0.0.0.0'
    assert server.port == 8000
    assert server.url == 'http://0.0.0.0:8000/'


def test_server_defaults_headers():
    with httpx.Server(app) as server:
        with httpx.Client() as client:
            response = client.get(server.url)
            assert response.headers['Server'] == 'httpx/dev'
            assert response.headers['Connection'] == 'keep-alive'
            assert response.headers['Date'].endswith('GMT')
