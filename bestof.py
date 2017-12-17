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
import requests

from threading import Thread
from flask import Flask, Response, request
from werkzeug.serving import make_server

class Instagram(object):
    """Lightweight wrapper for the Instagram API."""

    # Compressed just to avoid bots scanning for such information.
    _b64_client_id = b'eJwzNbMwT0lOTbYwskwyMTAwtkgyM000MUkyT0xKtkyyNAIAjuEIyQ=='
    _auth = '.instagram_access_token'

    _auth_url_format = (
        """https://api.instagram.com/oauth/authorize/"""
        """?client_id={}&redirect_uri={}&response_type=token"""
    )

    _redirect_uri = 'http://localhost:5000'

    _auth_first_stage = (
        b'eJyVVlGL2zgQft9foVMpcWBtJxTKkYtT2nQX7uHoUvbgjlIORRrHYmXLlcZJQ9n/fiM'
        b'72cRe947VQ+KRZr6ZbzQz9vKXj5/W93/f3bACS7O6Wp7+QKjVFaO1LAEFk4VwHjDjDe'
        b'bxr5yll4cFYh3Dt0bvMv5X/Of7eG3LWqDeGOBM2gqhIsvfbzJQW+BHS9RoYPUBPDKbM'
        b'yyAHUC4ZdrtX6BXooSM7zTsa+vwAnCvFRaZgp2WELfCNdOVRi1M7KUwkM1PzoyuHpgD'
        b'k3GPBwO+ACCkwkGe8RC9X6RpTrg+2Vq7NSBq7RNpy1R6/y4XpTaH7I9wDs4JPKG2WN1'
        b'zWBurDuzHk9huCfmwdbapVCytsW7BXt3efpzfzn/rqQXXcedmwSZnR5Nr5kXlY5J0fj'
        b'Z5vHp6VHqX5I4ydD/w3OZjweaz2eu+r1oopavtgs36+0r72gjyj4LurX9WgN4WOIpmP'
        b'SXcVgsmNt6aBgeWaOtnngzk+GyzFG6rq972KM31gOfP6OzAoaYiiIXRW8IttVJDWn3K'
        b'sQRjXhrUsRjHk/92Nqu//wSRiQbtIFfwHU/hSgIFd+k2/C7TY8kt065Bl23N2cpYoTI'
        b'uRY2Ng3v7AFU0pSo9lql0usZzneZNJcOdsb7+gMNOOCakBO//waDAMqJVKbtPjJUi2C'
        b'ehfxJKocaIv+LTL/OvJylrpWelgtEkdeAbgymV9g/WAi/6bh6v2WQLOJmOpfwp9BaMZ'
        b'gy1fC2oMPw1o2FRWDVGI7eupPCVlU1JeU2kA4FwYyBIEQ/HfDrsSFcmNPDeIzq9obKO'
        b'eIfPnxz9r4FoQ+UhQixIfagfhdge4EBD60hiGHxYOo+6w6QQ/tO+unO2pto+RGQ5HTM'
        b'4sS6o4qG61WDUf5DXVd3gkP1pXUAMuOGhBmLGO42X24ehTvaBw0tNd8I0wE/3/oUgvg'
        b'6T27sUUddQqXWhjYouUEf8Pl71pf6wOCUwtFwPNHgZrYZmU1IzTEe6+NiRnUhzhEkjv'
        b'M94N+P4uVefH64vTocax2k00Gi1ivnqM3iKmYZl+7btug1tKxAdo7uuptEyH7N/s7qj'
        b'96IHthcakyQhvTeDSFIK5SL0s3h8XKYhd+30Cl8Z/wLciVFf'
    )

    _auth_second_stage = (
        b'eJyVVF1vmzAUfe+vuGWa+lJCUKVpYpCpSxup0r4eOml7dOwLWDU2sy9Jo2n/fSaQBkj'
        b'6MD+AfT/OOfdyTXp59235+Ov7PZRUqcVFenghE4sL8CutkBjwklmHlAUN5eH7AKKhsy'
        b'SqQ/zdyE0W/Ax/3IZLU9WM5FphANxoQu0zH+4zFAUGfSZJUrj4hI7A5EAlwg6ZTaPOP'
        b'kDXrMIs2Ejc1sbSAHArBZWZwI3kGO4P1yC1JMlU6DhTmMUHMiX1E1hUWeBop9CViB6p'
        b'tJhnQaveJVGUe1w3K4wpFLJauhk3VcSd+5izSqpd9qX1o7WMDqh7rG7frrURO/jzcty'
        b'bGH8qrGm0CLlRxibwZrW6i1fxh1FYSx12NAlcHYmursEx7UJ/kvkx5e/Fy1bIzSy3vk'
        b'OPE+Z9PxKI5/O3Y66aCSF1kcB8bBfS1Yp5fmL+u419JcqipLNoxvmGG50AWzujGppkk'
        b'qlPmBTmdGKsmC2kHpnPlrmc1PlaORu0JP0QhEzJwuNWUohpWeOSQ45K/a+ofhjPN//d'
        b'fF4/v4IIrCEz6RU+00Eu96Boh7TtM436kUuj7oKm7cz10+jlAFfMuSzoWhUcR/PUuRx'
        b'4pxF9UZOIfVQZL245R+egsMxHiUsvJT4XeLP4arawMw1wpv3do8ZqPw6txcLy84PPu5'
        b'lIiLyGgebjsd+mUVeuT23/Uv8A/z1DHw=='
    )


    def authenticate(self):
        """If necessary, asks the user to grant the app permissions, and saves
        the access token to the user's home directory.
        """
        if self._access_token is not None:
            return

        auth_server = _FlaskAppWrapper()
        auth_server.add_endpoint(
            endpoint="/",
            endpoint_name="authorization_redirect",
            response=Response(
                _Utils.decompress_text(self._auth_first_stage)
            )
        )
        auth_server.add_endpoint(
            endpoint="/result/",
            endpoint_name="authorization_success",
            handler=self._handle_instagram_token,
            response=Response(
                _Utils.decompress_text(self._auth_second_stage)
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


class _Api(object):
    """Wrapper class to handle Instagram API endpoinst."""

    _base_url = 'https://api.instagram.com/v1'

    _users = '/users/{}/'
    _users_media_recent = '/users/{}/media/recent/'

    def __init__(self, access_token):
        self.access_token = access_token


    def get_user(self, user_id='self'):
        """Returns a dictionary with the response to the /users/{user_id}/
        endpoint if the request succeeded, None otherwise.
        """
        url_params = {'access_token': self.access_token}
        url = self._base_url + self._users.format(user_id)

        response = requests.get(url, params=url_params)
        if not response.ok or response.status_code is not 200:
            return None

        return json.loads(response.content)


    def get_user_media_recent(self, user_id='self', max_id=None, min_id=None, count=None):
        """Returns a dictionary with the response to the
        /users/{user-id}/media/recent/ endpoint if the request succeeded, None
        otherwise.
        """
        url = self._base_url + self._users_media_recent.format(user_id)
        url_params = {
            'access_token': self.access_token,
            'max_id': max_id,
            'min_id': min_id,
            'count': count
        }

        response = requests.get(url, params=url_params)
        if not response.ok or response.status_code is not 200:
            return None

        return json.loads(response.content)


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


class _FlaskAppWrapper(object):
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