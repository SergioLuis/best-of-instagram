"""A way to get your best Instagram images of the year without logging in
into shaddy websites!
"""

import json
import webbrowser

from os import path
from threading import Thread
from flask import Flask, Response, request
from werkzeug.serving import make_server

class Instagram(object):
    """Lightweight wrapper for the Instagram API."""

    def authenticate(self):
        """Asks the user to gran the app permissions, and grabs the access token."""
        if Instagram.__load_access_token() is not None:
            return

        auth_server = FlaskAppWrapper()
        auth_server.add_endpoint(
            endpoint="/",
            handler=self.__save_access_token,
            response=Response("OK!", status=200, content_type="text/plain")
        )
        auth_server.run()
        webbrowser.open("https://instagram.com")


    def _handle_instagram_redirect(self, args):
        Instagram.__save_access_token(args['access_token'])


    @staticmethod
    def __save_access_token(access_token):
        setting = { 'access_token' : access_token }
        with open(Instagram.__auth) as config:
            json.dump(setting, config)


    @staticmethod
    def __load_access_token():
        if not path.isfile(Instagram.__auth):
            return None

        with open(Instagram.__auth) as config:
            return json.load(config).get('access_token', None)


    __settings = 'instagram_settings.json'
    __auth = 'instagram_auth.json'

    __login_endpoint = "/"


class FlaskAppWrapper(object):
    """Flask server to handle Instagram authentication process."""

    app = None
    instagram = None

    def __init__(self):
        self.app = Flask(FlaskAppWrapper.__name)


    def run(self):
        """Starts the Flask server."""
        global server
        server = _ServerThread(self.app)
        server.start()


    def shutdown(self):
        """Shuts down the Flask server."""
        global server
        server.shutdown()


    def add_endpoint(self, endpoint=None, endpoint_name=None, handler=None, response=None):
        """Adds an endpoint handler."""
        self.app.add_url_rule(
            endpoint,
            endpoint_name,
            _EndpointAction(handler, response).execute
        )

    __name = 'FlaskAuthenticationServer'


class _ServerThread(Thread):
    """A way to run a Flask instance in another thread."""

    def __init__(self, app):
        Thread.__init__(self)
        self.srv = make_server('localhost', 5000, app)
        self.ctx = app.app_context()
        self.ctx.push()


    def run(self):
        """Starts the server."""
        self.srv.serve_forever()


    def shutdown(self):
        """Shuts down the server."""
        self.srv.shutdown_signal()


class _EndpointAction(object):
    """Represents an action to be executed when an endpoint is hit."""

    def __init__(self, action, response):
        self.action = action
        self.response = response

    def execute(self, *args):
        self.action(request.args)
        return self.response


if __name__ == '__main__':
    instagram = Instagram()
    instagram.authenticate()