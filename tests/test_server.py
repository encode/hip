import httpx


def app(request):
    return httpx.Response(200)


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
