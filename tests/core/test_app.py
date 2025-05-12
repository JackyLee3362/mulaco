from pprint import pprint

from mulaco.core.app import App


def test_app(app: App):
    pprint(app.config)
