"""A way to get your best Instagram images of the year without logging into
shaddy websites!
"""

import base64
import ctypes
import json
import logging
import os
import time
import webbrowser
import zlib

from threading import Thread
from flask import Flask, Response, request
from werkzeug.serving import make_server

class Instagram(object):
    """Lightweight wrapper for the Instagram API."""

    # Compressed just to avoid bots scanning for such information.
    _b64_client_id = b'eJwzNbMwT0lOTbYwskwyMTAwtkgyM000MUkyT0xKtkyyNAIAjuEIyQ=='
    _auth = '.instagram_access_token'

    _auth_url_format = 'https://api.instagram.com/oauth/authorize/?client_id={}&redirect_uri={}&response_type=token'
    _redirect_uri = 'http://localhost:5000'

    _internal_token_send_html = b'eJyVVlGP2zYMfs+vUFUMSYBzfEGBokjjDLf0DiiwrX24ARuKYlAk2hZOljyJThoU999HOckl9rkbTg+JKJEf+VEkk+WrD5/W9399vmUlVmY1Wp6+QKjViNFaVoCCyVL4AJjxBvPkHWfp5WWJWCfwT6O3Gf8z+eMmWbuqFqg3BjiTziJYsvx4m4EqgB8tUaOB1S8QkLmcYQlsD8Iv08P5BboVFWR8q2FXO48XgDutsMwUbLWEpBWumLYatTBJkMJANj85M9o+MA8m4wH3BkIJQEilhzzjMfqwSNOccMOscK4wIGodZtJVqQzh51xU2uyz3+I9eC/whNpiHfZxbZzas+9PYnsk5EPhXWNVIp1xfsFe3919mN/N33fUouvk4GbBxmdH4ysWhA0JSTo/mzyOnrZKb2e5pwzd9zy3+Viw+fX1T11ftVBK22LBrrvnSofaCPKPgt6te1eCLkocRHOBEu7sgolNcKbBniW6+pknAzk+O6yEL7TtHA/SXPd4/ojOFjxqKoJEGF0QbqWV6tPqUk4kGPPSoI7FOJz8t9fX9bcfIDLRoOvlCr7hKVxJoOAv3cbPZXosuWV6aNBlW3POGidUxqWosfFw7x7ATqZUpccylV7XeK7TvLEyvhnr6vc4bIVnQkoI4W+MCiwjWla53cw4KaL9LPbPjFKoccJf8+mX+deTlLXS+1G/VnAyTj2ExmBKtf2dtciLrp/HKzYuAMfToZw/xd6C0ZChnq8FVUa4YjQtSqeGeOTOVxS/crKpKLEz6UEg3BqI0oTHaz7tt6SvZjTxbhC93lBdT/gBnz85+l8D0YbKY4RYTnvZIP1JjO0B9jS1jiT6wcel88nhclaK8GlnP3tXU3HvJ2Q5HTI4sS6p5MHeaTDqP8hrWzfYZ39aFxA9brivgZjxg8bL7eNUJ/vI4aWmW2Ea4Kd3/0IQX/vJ7TyKqGuwal1qoyYXqAN+H0ddqTstTgmMPdcBjV4Gq6HZVNQN04E2PrbkQaRBwqQRIWT8MOT4uVmfX64vbvsax3HU02i1yvnqpm0zVnhBWuoVDZH5kOKb1e9ux/auoQFh6VeTZoSlTo0nnq1//Uh2b3ohpBTDRcxn8bhdpjFp7dyK/y/+BR9DTnw='
    _success_html = b'eJyVVF1vmzAUfe+vuGWa+lJCUKVpYpCpSxup0r4eOml7dOwLWDU2sy9Jo2n/fSaQBkj6MD+AfT/OOfdyTXp59235+Ov7PZRUqcVFenghE4sL8CutkBjwklmHlAUN5eH7AKKhsySqQ/zdyE0W/Ax/3IZLU9WM5FphANxoQu0zH+4zFAUGfSZJUrj4hI7A5EAlwg6ZTaPOPkDXrMIs2Ejc1sbSAHArBZWZwI3kGO4P1yC1JMlU6DhTmMUHMiX1E1hUWeBop9CViB6ptJhnQaveJVGUe1w3K4wpFLJauhk3VcSd+5izSqpd9qX1o7WMDqh7rG7frrURO/jzctybGH8qrGm0CLlRxibwZrW6i1fxh1FYSx12NAlcHYmursEx7UJ/kvkx5e/Fy1bIzSy3vkOPE+Z9PxKI5/O3Y66aCSF1kcB8bBfS1Yp5fmL+u419JcqipLNoxvmGG50AWzujGppkkqlPmBTmdGKsmC2kHpnPlrmc1PlaORu0JP0QhEzJwuNWUohpWeOSQ45K/a+ofhjPN//dfF4/v4IIrCEz6RU+00Eu96Boh7TtM436kUuj7oKm7cz10+jlAFfMuSzoWhUcR/PUuRx4pxF9UZOIfVQZL245R+egsMxHiUsvJT4XeLP4arawMw1wpv3do8ZqPw6txcLy84PPu5lIiLyGgebjsd+mUVeuT23/Uv8A/z1DHw=='


    def authenticate(self):
        """If necessary, asks the user to grant the app permissions, and saves
        the access token to the user's home directory.
        """
        if self._access_token is not None:
            return

        auth_server = FlaskAppWrapper()
        auth_server.add_endpoint(
            endpoint="/",
            endpoint_name="authorization_redirect",
            response=Response(
                _Utils.decompress_text(self._internal_token_send_html)
            )
        )
        auth_server.add_endpoint(
            endpoint="/result/",
            endpoint_name="authorization_success",
            handler=self._handle_instagram_token,
            response=Response(
                _Utils.decompress_text(self._success_html)
            )
        )
        auth_server.run()
        webbrowser.open(self._auth_url)

        while not self._is_authorized():
            time.sleep(1)

        auth_server.shutdown()


    def _handle_instagram_token(self, args):
        self._access_token = args['token']


    def _is_authorized(self):
        return os.path.isfile(_Utils.get_home_based_path(Instagram._auth))


    @property
    def _auth_url(self):
        return self._auth_url_format.format(
            self._client_id,
            self._redirect_uri
        )


    @property
    def _access_token(self):
        access_token_file = _Utils.get_home_based_path(self._auth)

        if not os.path.isfile(access_token_file):
            return None

        with open(access_token_file) as config:
            return config.read()


    @_access_token.setter
    def _access_token(self, value):
        access_token_file = _Utils.get_home_based_path(self._auth)

        with open(access_token_file, 'w') as config:
            config.write(value)

        if os.name == 'nt':
            _Utils.set_hidden_flag(access_token_file)


    @property
    def _client_id(self):
        return _Utils.decompress_text(self._b64_client_id)


class _Utils(object):
    """Utility methods not extrictly related to anything else."""

    @staticmethod
    def decompress_text(text):
        """Takes a text compressed with ZLib and encoded in Base64 and returns
        the original text.
        """
        return zlib.decompress(base64.b64decode(text)).decode('utf-8')


    @staticmethod
    def get_home_based_path(file_name):
        """Returns the 'file_name' path preprended with the home path of the
        user. Works for all OSs.
        """
        return os.path.join(os.path.expanduser('~'), file_name)


    @staticmethod
    def set_hidden_flag(file_path):
        """Sets the 'hidden file' flag to the specified file."""
        ctypes.windll.kernel32.SetFileAttributesW(file_path, 0x02)


class FlaskAppWrapper(object):
    """Flask server to handle Instagram authentication process."""

    app = None
    server = None

    def __init__(self):
        flask_logger = logging.getLogger("werkzeug")
        flask_logger.setLevel(logging.ERROR)
        self.app = Flask('FlaskAuthenticationServer')


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


class _EndpointAction(object): # pyling: disable=R0903
    """Represents an action to be executed when an endpoint is hit."""

    def __init__(self, action, response):
        self.action = action
        self.response = response


    def execute(self, *args): # pylint: disable=W0613
        """Executes the action when a request comes in, and returns the Response."""
        if self.action is not None:
            self.action(request.args)

        return self.response


if __name__ == '__main__':
    testing = Instagram()
    testing.authenticate()