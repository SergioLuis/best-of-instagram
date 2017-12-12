"""A way to get your best Instagram images of the year without logging in
into shaddy websites!
"""

import json
import sys
import time
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

        client_id = Instagram.__load_client_id()
        if client_id is None:
            raise Exception(
                """You need to save the ClientID in {} as a JSON file as: """
                """     '{{ "client_id" : "the_client_id" }}' """.format(
                    Instagram.__get_file_path(Instagram.__settings)
                )
            )

        auth_server = FlaskAppWrapper()
        auth_server.add_endpoint(
            endpoint="/",
            response=Response(
                self.__authorization_js,
                status=200,
                content_type="text/html")
        )
        auth_server.add_endpoint(
            endpoint="/success",
            handler=self._handle_instagram_redirect,
            response=Response(
                "OK! You can go back now!",
                status=200,
                content_type="text/html"
            )
        )
        auth_server.run()
        webbrowser.open(Instagram.__build_oauth_url(client_id))

        while not self._is_authorized():
            time.sleep(1)

        # FIXME: this throws an exception
        # auth_server.shutdown()


    def _handle_instagram_redirect(self, args):
        pass


    def _is_authorized(self):
        return path.isfile(Instagram.__get_file_path(Instagram.__auth))


    @staticmethod
    def __build_oauth_url(client_id):
        return Instagram.__auth_url.format(
            client_id,
            Instagram.__redirect_uri
        )


    @staticmethod
    def __save_access_token(access_token):
        setting = {'access_token': access_token}
        with open(Instagram.__get_file_path(Instagram.__auth), 'w') as config:
            json.dump(setting, config)


    @staticmethod
    def __load_access_token():
        config_file = Instagram.__get_file_path(Instagram.__auth)
        if not path.isfile(config_file):
            return None

        with open(config_file) as config:
            return json.load(config).get('access_token', None)


    @staticmethod
    def __load_client_id():
        config_file = Instagram.__get_file_path(Instagram.__settings)
        if not path.isfile(config_file):
            return None

        with open(config_file) as config:
            return json.load(config).get('client_id', None)


    @staticmethod
    def __get_file_path(file_name):
        return path.join(path.expanduser('~'), file_name)


    __settings = 'instagram_settings.json'
    __auth = 'instagram_auth.json'

    __auth_url = 'https://api.instagram.com/oauth/authorize/?client_id={}&redirect_uri={}&response_type=token'
    __redirect_uri = 'http://localhost:5000'

    # TODO: some javascript that gets the token and makes another request with it
    __authorization_js = ''

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
        """Executes the action when a request comes in, and returns the Response."""
        self.action(request.args)
        return self.response


if __name__ == '__main__':
    instagram = Instagram()
    instagram.authenticate()
