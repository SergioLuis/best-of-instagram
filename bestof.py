import requests

from flask import Flask, Response, request

class Instagram(object):
    """Lightweight wrapper for the Instagram API."""

    def authenticate(self):
        """Asks the user to gran the app permissions, and grabs the access token.""" 
        auth_server = FlaskAppWrapper()
        auth_server.add_endpoint(
            endpoint="/",
            handler=self.__save_access_token,
            response=Response("OK!", status=200, content_type="text/plain")
        )


    def __save_access_token(self, args):
        print(args)


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
        """Starts the Flask server. Once started cannot be stoped!"""
        self.app.run("localhost", 5000)


    def add_endpoint(self, endpoint=None, endpoint_name=None, handler=None, response=None):
        """Adds an endpoint handler."""
        self.app.add_url_rule(
            endpoint,
            endpoint_name,
            EndpointAction(handler, response)
        )

    __name = 'FlaskAuthenticationServer'


class EndpointAction(object):
    """Represents an action to be executed when an endpoint is hit."""

    def __init__(self, action, response):
        self.action = action
        self.response = response


    def __call__(self, *args):
        self.action(request.args)
        return self.response