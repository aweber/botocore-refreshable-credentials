import os
import pathlib
import unittest

import botocore.credentials
import botocore.session

import botocore_refreshable_credentials

TESTS = pathlib.Path(__file__).parent


class TestCase(unittest.IsolatedAsyncioTestCase):

    MISSING_ACCESS_KEY = str(TESTS / 'data' / 'missing_access_key')
    MISSING_EXPIRATION = str(TESTS / 'data' / 'missing-expiration')
    WITH_EXPIRATION = str(TESTS / 'data' / 'with-expiration')

    @staticmethod
    def replace_env(env):
        os.environ.clear()
        os.environ.update(env)

    def setUp(self):
        super().setUp()
        self.__saved = os.environ.copy()
        self.addCleanup(self.replace_env, os.environ.copy())

        # remove any creds in env if found
        for key in ('AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY',
                    'AWS_SHARED_CREDENTIALS_FILE'):
            try:
                del os.environ[key]
            except KeyError:
                pass

    def test_get_session_returns_botocore_session(self):
        result = botocore_refreshable_credentials.get_session()
        self.assertIsInstance(result, botocore.session.Session)

    def test_with_non_refreshable_credentials(self):
        os.environ['AWS_ACCESS_KEY_ID'] = 'foo'
        os.environ['AWS_SECRET_ACCESS_KEY'] = 'bar'

        session = botocore_refreshable_credentials.get_session()
        creds = session.get_credentials()
        self.assertIsInstance(creds, botocore.credentials.Credentials)

    def test_with_refreshable_credentials(self):
        os.environ['AWS_SHARED_CREDENTIALS_FILE'] = self.WITH_EXPIRATION

        session = botocore_refreshable_credentials.get_session()
        creds = session.get_credentials()
        self.assertIsInstance(creds,
                              botocore.credentials.RefreshableCredentials)

    def test_with_missing_expiry_in_credentials_file(self):
        os.environ['AWS_SHARED_CREDENTIALS_FILE'] = self.MISSING_EXPIRATION

        session = botocore_refreshable_credentials.get_session()
        creds = session.get_credentials()
        self.assertIsInstance(creds, botocore.credentials.Credentials)

    def test_with_missing_access_key_in_credentials_file(self):
        os.environ['AWS_SHARED_CREDENTIALS_FILE'] = self.MISSING_ACCESS_KEY

        session = botocore_refreshable_credentials.get_session()
        creds = session.get_credentials()
        self.assertEqual(creds, None)

    def test_with_no_credentials(self):
        os.environ['AWS_SHARED_CREDENTIALS_FILE'] = 'test-data/aws-iam/foo'

        session = botocore_refreshable_credentials.get_session()
        creds = session.get_credentials()
        self.assertEqual(creds, None)
