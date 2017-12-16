"""A way to get your best Instagram images of the year without logging in
into shaddy websites!
"""

import base64
import json
import time
import webbrowser
import zlib

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
            endpoint_name="authorization_redirect",
            response=Response(
                Instagram.__decompress_html(self.__internal_token_send_html)
            )
        )
        auth_server.add_endpoint(
            endpoint="/result/",
            endpoint_name="authorization_success",
            handler=self._handle_instagram_token,
            response=Response(
                Instagram.__decompress_html(self.__success_html)
            )
        )
        auth_server.run()
        webbrowser.open(Instagram.__build_oauth_url(client_id))

        while not self._is_authorized():
            time.sleep(1)

        auth_server.shutdown()


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


    @staticmethod
    def __decompress_html(html):
        return zlib.decompress(base64.b64decode(html)).decode('utf-8')


    __settings = 'instagram_settings.json'
    __auth = 'instagram_auth.json'

    __auth_url = 'https://api.instagram.com/oauth/authorize/?client_id={}&redirect_uri={}&response_type=token'
    __redirect_uri = 'http://localhost:5000'

    __internal_token_send_html = b'eJyVVlGP2zYMfs+vUFUMSYBzfEGBokjjDLf0DiiwrX24ARuKYlAk2hZOljyJThoU999HOckl9rkbTg+JKJEf+VEkk+WrD5/W9399vmUlVmY1Wp6+QKjViNFaVoCCyVL4AJjxBvPkHWfp5WWJWCfwT6O3Gf8z+eMmWbuqFqg3BjiTziJYsvx4m4EqgB8tUaOB1S8QkLmcYQlsD8Iv08P5BboVFWR8q2FXO48XgDutsMwUbLWEpBWumLYatTBJkMJANj85M9o+MA8m4wH3BkIJQEilhzzjMfqwSNOccMOscK4wIGodZtJVqQzh51xU2uyz3+I9eC/whNpiHfZxbZzas+9PYnsk5EPhXWNVIp1xfsFe3919mN/N33fUouvk4GbBxmdH4ysWhA0JSTo/mzyOnrZKb2e5pwzd9zy3+Viw+fX1T11ftVBK22LBrrvnSofaCPKPgt6te1eCLkocRHOBEu7sgolNcKbBniW6+pknAzk+O6yEL7TtHA/SXPd4/ojOFjxqKoJEGF0QbqWV6tPqUk4kGPPSoI7FOJz8t9fX9bcfIDLRoOvlCr7hKVxJoOAv3cbPZXosuWV6aNBlW3POGidUxqWosfFw7x7ATqZUpccylV7XeK7TvLEyvhnr6vc4bIVnQkoI4W+MCiwjWla53cw4KaL9LPbPjFKoccJf8+mX+deTlLXS+1G/VnAyTj2ExmBKtf2dtciLrp/HKzYuAMfToZw/xd6C0ZChnq8FVUa4YjQtSqeGeOTOVxS/crKpKLEz6UEg3BqI0oTHaz7tt6SvZjTxbhC93lBdT/gBnz85+l8D0YbKY4RYTnvZIP1JjO0B9jS1jiT6wcel88nhclaK8GlnP3tXU3HvJ2Q5HTI4sS6p5MHeaTDqP8hrWzfYZ39aFxA9brivgZjxg8bL7eNUJ/vI4aWmW2Ea4Kd3/0IQX/vJ7TyKqGuwal1qoyYXqAN+H0ddqTstTgmMPdcBjV4Gq6HZVNQN04E2PrbkQaRBwqQRIWT8MOT4uVmfX64vbvsax3HU02i1yvnqpm0zVnhBWuoVDZH5kOKb1e9ux/auoQFh6VeTZoSlTo0nnq1//Uh2b3ohpBTDRcxn8bhdpjFp7dyK/y/+BR9DTnw='
    __success_html = b'eJyVVF1vmzAUfe+vuGWa+lJCUKVpYpCpSxup0r4eOml7dOwLWDU2sy9Jo2n/fSaQBkj6MD+AfT/OOfdyTXp59235+Ov7PZRUqcVFenghE4sL8CutkBjwklmHlAUN5eH7AKKhsySqQ/zdyE0W/Ax/3IZLU9WM5FphANxoQu0zH+4zFAUGfSZJUrj4hI7A5EAlwg6ZTaPOPkDXrMIs2Ejc1sbSAHArBZWZwI3kGO4P1yC1JMlU6DhTmMUHMiX1E1hUWeBop9CViB6ptJhnQaveJVGUe1w3K4wpFLJauhk3VcSd+5izSqpd9qX1o7WMDqh7rG7frrURO/jzctybGH8qrGm0CLlRxibwZrW6i1fxh1FYSx12NAlcHYmursEx7UJ/kvkx5e/Fy1bIzSy3vkOPE+Z9PxKI5/O3Y66aCSF1kcB8bBfS1Yp5fmL+u419JcqipLNoxvmGG50AWzujGppkkqlPmBTmdGKsmC2kHpnPlrmc1PlaORu0JP0QhEzJwuNWUohpWeOSQ45K/a+ofhjPN//dfF4/v4IIrCEz6RU+00Eu96Boh7TtM436kUuj7oKm7cz10+jlAFfMuSzoWhUcR/PUuRx4pxF9UZOIfVQZL245R+egsMxHiUsvJT4XeLP4arawMw1wpv3do8ZqPw6txcLy84PPu5lIiLyGgebjsd+mUVeuT23/Uv8A/z1DHw=='

    __login_endpoint = "/"


class FlaskAppWrapper(object):
    """Flask server to handle Instagram authentication process."""

    app = None
    instagram = None
    server = None

    def __init__(self):
        self.app = Flask(FlaskAppWrapper.__name)


    def run(self):
        """Starts the Flask server."""
        self.server = _ServerThread(self.app)
        self.server.start()


    def shutdown(self):
        """Shuts down the Flask server."""
        self.server.shutdown()


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
        self.srv.shutdown()


class _EndpointAction(object):
    """Represents an action to be executed when an endpoint is hit."""

    def __init__(self, action, response):
        self.action = action
        self.response = response


    def execute(self, *args):
        """Executes the action when a request comes in, and returns the Response."""
        if self.action is not None:
            self.action(request.args)

        return self.response


if __name__ == '__main__':
    instagram = Instagram()
    instagram.authenticate()
