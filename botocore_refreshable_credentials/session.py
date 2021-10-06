import logging
import typing

from botocore import credentials, session
from botocore import exceptions
from dateutil import parser

LOGGER = logging.getLogger(__name__)


class RefreshableSharedCredentialsProvider(credentials.SharedCredentialProvider
                                           ):
    """
    Implement logic around detecting expiration for IAM STS role based auth

    """
    METHOD = 'refreshable-shared-credentials-file'
    CANONICAL_NAME = 'customRefreshableSharedCredentials'
    EXPIRY_TIME = 'aws_expiration'

    def load(
        self
    ) -> typing.Union[None, credentials.Credentials,
                      credentials.RefreshableCredentials]:
        """Load credentials, checking to see if `expiry_time` is set."""
        config = self._parse_credentials(require_expiry=False)
        if config and config.get('expiry_time'):
            return credentials.RefreshableCredentials(
                config['access_key'], config['secret_key'], config['token'],
                parser.parse(config['expiry_time']), self._refresh,
                self.METHOD)
        elif config:
            return credentials.Credentials(config['access_key'],
                                           config['secret_key'],
                                           token=config['token'],
                                           method=self.METHOD)

    def _parse_credentials(self, require_expiry: bool = True) \
            -> typing.Optional[dict]:
        """Attempt to parse the credentials, and if found checks for the
        `aws_expiration` field, returning the value in the resulting dict.

        :raises: botocore.exceptions.PartialCredentialsError

        """
        try:
            ini_data = self._ini_parser(self._creds_filename)
        except exceptions.ConfigNotFound:
            return None

        if self._profile_name in ini_data:  # pragma: no-branch
            config = ini_data[self._profile_name]
            if self.ACCESS_KEY in config:
                LOGGER.debug(
                    'Found credentials in shared credentials file: %s',
                    self._creds_filename)
                access_key, secret_key = self._extract_creds_from_mapping(
                    config, self.ACCESS_KEY, self.SECRET_KEY)
                if require_expiry and self.EXPIRY_TIME not in config:
                    raise exceptions.PartialCredentialsError(
                        provider=self.METHOD, cred_var=self.EXPIRY_TIME)
                result = {
                    'access_key': access_key,
                    'secret_key': secret_key,
                    'token': self._get_session_token(config),
                }
                if self.EXPIRY_TIME in config:
                    result['expiry_time'] = config[self.EXPIRY_TIME]
                return result

    def _refresh(self) -> None:
        """Invoked when the session is being refreshed"""
        return self._parse_credentials()


def get_session(**kwargs) -> session.Session:
    """Return an botocore.session.Session that can refresh a
    credentials file.

    The session will include a new credentials provider that will use the
    ``aws_expiration`` field in the credentials file to know when to refresh.

    """
    boto_session = session.Session(**kwargs)
    credentials_file = boto_session.get_config_variable('credentials_file')
    provider = RefreshableSharedCredentialsProvider(credentials_file)
    resolver = boto_session.get_component('credential_provider')
    resolver.insert_before(credentials.SharedCredentialProvider.METHOD,
                           provider)
    return boto_session
