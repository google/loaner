# Copyright 2018 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests for deployments.auth."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

# Prefer Python 2 and fall back on Python 3.
# pylint:disable=g-statement-before-imports,g-import-not-at-top
try:
  import __builtin__ as builtins
except ImportError:
  import builtins
# pylint:enable=g-statement-before-imports,g-import-not-at-top

import datetime
import sys

from absl import flags
from absl.testing import parameterized
from pyfakefs import fake_filesystem
from pyfakefs import mox3_stubout

import google_auth_httplib2

import mock

from oauth2client import client as oauth2_client
from oauth2client import tools

from google.oauth2 import credentials

from absl.testing import absltest
from loaner.deployments.lib import auth
from loaner.deployments.lib import common

FLAGS = flags.FLAGS

_FAKE_JSON_CONTENTS_ONE = '''{"scopes": ["test_scope1"]}'''
_FAKE_JSON_CONTENTS_TWO = '''{"scopes": ["test_scope2"]}'''


class TestCredentials(object):
  """A fake credentials object for testing."""

  def __init__(self, scopes):
    self.scopes = scopes

  def __eq__(self, other):
    return self.__dict__ == other.__dict__

  def has_scopes(self, scopes):
    """If the scopes requested were included on construction.

    Args:
      scopes: list|str|, the list of scopes required.

    Returns:
      True if the scopes provided were also provided during initialization.
    """
    return set(scopes).issubset(set(self.scopes))


class AuthTest(parameterized.TestCase, absltest.TestCase):

  def setUp(self):
    super(AuthTest, self).setUp()
    self._test_project = 'test_project'
    self._test_client_id = 'test_client_id'
    self._test_client_secret = 'test_client_secret'
    self._test_config = common.ProjectConfig(
        'test_key', self._test_project, self._test_client_id,
        self._test_client_secret, None, '/test/path.yaml')
    # Save the real modules for clean up.
    self.real_open = builtins.open
    # Create a fake file system and stub out builtin modules.
    self.fs = fake_filesystem.FakeFilesystem()
    self.os = fake_filesystem.FakeOsModule(self.fs)
    self.open = fake_filesystem.FakeFileOpen(self.fs)
    self.stubs = mox3_stubout.StubOutForTesting()
    self.stubs.SmartSet(builtins, 'open', self.open)
    self.stubs.SmartSet(auth, 'os', self.os)

  def tearDown(self):
    super(AuthTest, self).tearDown()
    self.stubs.UnsetAll()
    builtins.open = self.real_open

  @mock.patch.object(credentials, 'Credentials', autospec=True)
  def test_cloud_credentials_constructor(self, mock_creds):
    """Test the creation of the CloudCredentials object."""
    mock_creds.from_authorized_user_info.return_value = TestCredentials([
        'test_scope1',
    ])
    self.fs.CreateFile(
        self._test_config.local_credentials_file_path,
        contents=_FAKE_JSON_CONTENTS_ONE)
    test_creds = auth.CloudCredentials(self._test_config, ['test_scope1'])
    self.assertEqual(self._test_config, test_creds._config)
    self.assertEqual(TestCredentials(['test_scope1']), test_creds._credentials)

  @parameterized.parameters(
      ('urn:ietf:wg:oauth:2.0:oob', False),
      ('http://localhost:8080/oauth2callback', True),
  )
  @mock.patch.object(oauth2_client, 'OAuth2WebServerFlow', autospec=True)
  @mock.patch.object(tools, 'run_flow')
  def test_cloud_credentials_constructor_no_local_file(
      self, expected_redirect_uri, run_web_server, mock_run_flow,
      mock_server_flow):
    """Test the creation of the CloudCredentials object with no local creds."""
    FLAGS.automatic_oauth = run_web_server
    mock_run_flow.return_value = oauth2_client.OAuth2Credentials(
        access_token='test_access_token',
        client_id=self._test_config.client_id,
        client_secret=self._test_config.client_secret,
        refresh_token='test_refresh_token',
        token_expiry=datetime.datetime(year=2018, month=1, day=1),
        token_uri='test_token_uri',
        user_agent=None,
        id_token='test_id_token',
        scopes=['test_scope1'])
    test_creds = auth.CloudCredentials(self._test_config, ['test_scope1'])
    self.assertEqual(self._test_config, test_creds._config)
    self.assertEqual('test_access_token', test_creds._credentials.token)
    self.assertEqual(
        'test_refresh_token', test_creds._credentials.refresh_token)
    self.assertEqual('test_id_token', test_creds._credentials.id_token)
    self.assertEqual('test_token_uri', test_creds._credentials.token_uri)
    self.assertEqual(
        self._test_config.client_id, test_creds._credentials.client_id)
    self.assertEqual(
        self._test_config.client_secret, test_creds._credentials.client_secret)
    self.assertEqual(['test_scope1'], test_creds._credentials.scopes)
    mock_server_flow.assert_called_once_with(
        client_id=self._test_config.client_id,
        client_secret=self._test_config.client_secret,
        scope=['test_scope1'],
        redirect_uri=expected_redirect_uri)

  @mock.patch.object(
      tools, 'run_flow', side_effect=oauth2_client.FlowExchangeError)
  def test_cloud_credentials_constructor_invalid_creds(self, mock_run_flow):
    """Test that an error is raised if credentials cannot be created."""
    del mock_run_flow  # Unused.
    with self.assertRaises(auth.InvalidCredentials):
      auth.CloudCredentials(self._test_config, ['test_scope1'])

  @mock.patch.object(google_auth_httplib2, 'AuthorizedHttp', autospec=True)
  @mock.patch.object(auth, 'build', autospec=True)
  @mock.patch.object(credentials, 'Credentials', autospec=True)
  def test_get_api_client(self, mock_creds, mock_build, mock_http_auth):
    """Test getting a scoped api client."""
    mock_creds.from_authorized_user_info.return_value = TestCredentials([
        'test_scope1',
    ])
    self.fs.CreateFile(
        self._test_config.local_credentials_file_path,
        contents=_FAKE_JSON_CONTENTS_ONE)
    test_creds = auth.CloudCredentials(self._test_config, ['test_scope1'])
    with mock.patch.object(
        test_creds, '_request_new_credentials',
        return_value=TestCredentials([
            'test_scope2', 'test_scope1'])) as mock_request:
      test_api_client = test_creds.get_api_client(
          'test_service', 'test_version', ['test_scope2'])
      del test_api_client  # Unused.
      mock_request.assert_called_once_with(['test_scope2', 'test_scope1'])
      mock_http_auth.assert_called_once_with(
          credentials=TestCredentials(['test_scope2', 'test_scope1']))
      mock_build.assert_called_once_with(
          serviceName='test_service', version='test_version',
          http=mock_http_auth.return_value)

  def test_remove_creds(self):
    """Test whether or not to remove the local credentials."""
    FLAGS.unparse_flags()
    self.assertFalse(auth._remove_creds())
    flags.FLAGS(sys.argv[:1] + ['--remove_creds'])
    FLAGS.mark_as_parsed()
    self.assertTrue(auth._remove_creds())

  def test_run_local_web_server_for_auth(self):
    """Test whether or not to run the local web server for authentication."""
    FLAGS.unparse_flags()
    self.assertFalse(auth._run_local_web_server_for_auth())
    flags.FLAGS(sys.argv[:1] + ['--automatic_oauth'])
    FLAGS.mark_as_parsed()
    self.assertTrue(auth._run_local_web_server_for_auth())


if __name__ == '__main__':
  absltest.main()
