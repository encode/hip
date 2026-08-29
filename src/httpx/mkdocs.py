
class MkDocs():
    def __init__(self, md, env, config):
        self.md = md
        self.env = env
        self.config = config

    def render(self, page: Resource):
        pass

    def build(self, pages: list[Resource], statics: list[Resource]):
        for page in pages:
            ...
        for static in statics:
            ...

    def serve(self):
        ...


def load_config():
    ...


def default_md():
    ...


def default_env():
    ...


def build(pages, statics, md, env, config):
    for page in pages:
        ...
    for static in statics:
        ...


def serve(pages, statics, md, env, config)