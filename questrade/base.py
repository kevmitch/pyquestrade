import os
import requests

def secret_fd_trunc(filename):
    """
    Create an empty file descriptor guaranteed to have 600 permisions.

    The file is first destroyed if it exists.
    """
    try:
        os.remove(filename)
    except OSError:
        pass

    umask_save = os.umask(0)
    try:
        fd = os.open(filename, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    finally:
        os.umask(umask_save)

    return fd

class Auth(dict):
    """
    Questrade Authorization data.

    On initialization, read the refresh token from refresh_token_path, which is
    used to request an access token and other parameters from access_url as
    documented at

    http://www.questrade.com/api/documentation/security

    The parameters, access token as well as a new refresh token will be stored
    in the resulting instance as dict entries.

    The initial refresh token can be obtained from

    https://login.questrade.com/APIAccess/UserApps.aspx

    by creating registering a personal app, adding a new device and generating a
    new token. Paste the resulting string into a file at refresh_token_path.
    """
    default_refresh_token_path = '~/.config/pyquestrade/refresh_token'
    default_access_url = 'https://login.questrade.com/oauth2/token'

    def __init__(self, access_url=default_access_url,
                 refresh_token_path=default_refresh_token_path):
        self.access_url = access_url
        self.refresh_token_path = os.path.expanduser(refresh_token_path)
        self.refresh()

    def refresh(self):
        """
        Redeem the refresh token for a new access token and access parameters.

        The refresh token is read from the file at refresh_token_path and used
        to query the Questrade server. The instance is updated with the response
        and the new refresh token is written back the the file at
        refresh_token_path.
        """
        with open(self.refresh_token_path) as f:
            refresh_token = f.read().strip()

        response = requests.post(
            self.access_url,
            params={
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token,
            }
        )
        response.raise_for_status()
        self.update(response.json())
        with os.fdopen(secret_fd_trunc(self.refresh_token_path), 'w') as f:
            f.write(self['refresh_token'])

        # Remove "/" so that it can be explicitly added when adding to the url
        self['api_server'] = self['api_server'].rstrip('/')

    @property
    def headers(self):
        """
        HTML headers containing the access token.
        """
        return {'Authorization': '{token_type} {access_token}'.format(**self)}

class ApiABC(object):
    """
    Abstract Base Class for Questrade API.
    """
    api_version = 'v1'

    def __init__(self, auth=None):
        self.auth = auth or Auth()

    def url(self, operation):
        """
        Construct a URL for the authorized user and provided operation.
        """
        return '{api_server}/{api_version}/{operation}'.format(
            operation=operation,
            api_version=self.api_version,
            **self.auth
        )

    def get(self, operation, params=None):
        """
        Send an authorized GET request for the given operation and parameters.

        The return value is the parsed JSON response.
        """
        response = requests.get(
            self.url(operation),
            headers=self.auth.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()
