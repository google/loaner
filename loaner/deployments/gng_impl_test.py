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

"""Tests for deployments.gng_impl."""

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

import sys

from absl.testing import flagsaver
from absl.testing import parameterized

from pyfakefs import fake_filesystem
from pyfakefs import mox3_stubout

import mock

from google.auth import credentials

from absl.testing import absltest
from loaner.deployments import gng_impl
from loaner.deployments.lib import app_constants
from loaner.deployments.lib import auth
from loaner.deployments.lib import common
from loaner.deployments.lib import utils

_BLANK_CONFIG = '''
default:
  project_id:
  client_id:
  client_secret:
  bucket:
'''

_VALID_CONFIG = '''
default:
  project_id: default-project
  client_id: default.apps.googleusercontent.com
  client_secret: default-secret
  bucket: default-bucket
'''


class _TestClientAPI(object):
  """An object to satisfy the _get_oauth_scopes requirements."""
  SCOPES = ('two', 'one', 'one')


class ManagerTest(parameterized.TestCase, absltest.TestCase):

  def setUp(self):
    super(ManagerTest, self).setUp()
    # Save the real modules for clean up.
    self.real_open = builtins.open
    # Create a fake file system and stub out builtin modules.
    self.fs = fake_filesystem.FakeFilesystem()
    self.os = fake_filesystem.FakeOsModule(self.fs)
    self.open = fake_filesystem.FakeFileOpen(self.fs)
    self.stubs = mox3_stubout.StubOutForTesting()
    self.stubs.SmartSet(builtins, 'open', self.open)
    self.stubs.SmartSet(common, 'os', self.os)

    # Setup Testdata.
    self._testdata_path = '/testdata'
    self._valid_config_path = self._testdata_path + '/valid_config.yaml'
    self._blank_config_path = self._testdata_path + '/blank_config.yaml'

    self.fs.CreateFile(self._valid_config_path, contents=_VALID_CONFIG)
    self.fs.CreateFile(self._blank_config_path, contents=_BLANK_CONFIG)

  def tearDown(self):
    super(ManagerTest, self).tearDown()
    self.stubs.UnsetAll()
    builtins.open = self.real_open

  def test_get_oauth_scopes(self):
    self.assertEqual(
        gng_impl._get_oauth_scopes([sys.modules[__name__]]), ['one', 'two'])

  def test_manager_init(self):
    test_config = common.ProjectConfig(
        'KEY', 'PROJECT', 'ID', 'SECRET', 'BUCKET', self._blank_config_path)
    test_constants = app_constants.get_default_constants()
    test_manager = gng_impl._Manager(test_config, test_constants, None)
    self.assertEqual(str(test_manager), "_Manager for project 'PROJECT'")
    self.assertEqual(
        repr(test_manager),
        '<_Manager.new(/testdata/blank_config.yaml, KEY)>')

  @parameterized.named_parameters(
      ('With Project Key From Prompts', 'dev', '/blank_config.yaml',
       "_Manager for project 'dev-project'",
       ('dev-project', 'dev.apps.googleusercontent.com', 'dev-secret'),),
      ('Without Project Key From YAML', None, '/valid_config.yaml',
       "_Manager for project 'default-project'",
       (common.DEFAULT,),),
  )
  def test_new(self, test_key, config_filename, expected_str, test_input):
    with mock.patch.object(utils, 'prompt_string', side_effect=test_input):
      with mock.patch.object(auth, 'CloudCredentials') as mock_creds:
        mock_creds.return_value.get_credentials.return_value = (
            credentials.AnonymousCredentials())
        test_manager = gng_impl._Manager.new(
            self._testdata_path + config_filename, test_key)
    self.assertEqual(str(test_manager), expected_str)

  def test_new__auth_error(self):
    side_effect = [
        'default-project',
        'default.apps.googleusercontent.com',
        'default-secret',
    ]
    mock_creds = mock.Mock()
    mock_creds.get_credentials.return_value = credentials.AnonymousCredentials()
    with mock.patch.object(
        utils, 'prompt_string', side_effect=side_effect) as mock_prompt_string:
      with mock.patch.object(
          auth, 'CloudCredentials',
          side_effect=[auth.InvalidCredentials, mock_creds]):
        gng_impl._Manager.new(self._valid_config_path, common.DEFAULT)
      self.assertEqual(3, mock_prompt_string.call_count)

  def test_main(self):
    with mock.patch.object(auth, 'CloudCredentials') as mock_creds:
      mock_creds.return_value.get_credentials.return_value = (
          credentials.AnonymousCredentials())
      with flagsaver.flagsaver(
          project=common.DEFAULT, config_file_path=self._valid_config_path):
        with self.assertRaises(SystemExit) as exit_err:
          gng_impl.main('unused')
          self.assertEqual(exit_err.exception.code, 0)

  def test_main__errors(self):
    with mock.patch.object(
        gng_impl._Manager, 'new', side_effect=KeyboardInterrupt()):
      with flagsaver.flagsaver(
          project=common.DEFAULT, config_file_path=self._valid_config_path):
        with self.assertRaises(SystemExit) as exit_err:
          gng_impl.main('unused')
          self.assertEqual(exit_err.exception.code, 1)


if __name__ == '__main__':
  absltest.main()
