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

from six.moves import StringIO

from google.auth import credentials

from absl.testing import absltest
from loaner.deployments import gng_impl
from loaner.deployments.lib import app_constants
from loaner.deployments.lib import auth
from loaner.deployments.lib import common
from loaner.deployments.lib import utils

# The following constants are YAML file contents that are written to the fake
# file system.
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
dev:
  project_id: dev-project
  client_id: dev.apps.googleusercontent.com
  client_secret: dev-secret
  bucket: dev-bucket
'''

# The following constants are what will be displayed on the screen for the
# functions being tested. This makes it easier to visiualize what will be
# displayed to the user.
_CHANGE_PROJECT_GOLDEN = (
    '''You are currently managing Google Cloud Project 'default-project'.
This project is currently saved as 'default'.
All of the currently configured projects include: default, dev.
Which project would you like to switch to?''')

_MAIN_HELP_GOLDEN = (
    '''To take an action type the action into the menu and press <Enter>
The following actions are available:

Action: 'change project'
Description: 'Change the Cloud Project currently being managed'

Action: 'help'
Description: 'Show this message'

Action: 'quit'
Description: 'Quit the Grab n Go Management script'

Press <Enter> to return to the main menu.

--------------------------------------------------------------------------------

''')


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
    self.stdout = StringIO()
    self.stubs = mox3_stubout.StubOutForTesting()
    self.stubs.SmartSet(builtins, 'open', self.open)
    self.stubs.SmartSet(common, 'os', self.os)
    self.stubs.SmartSet(sys, 'stdout', self.stdout)

    # Setup Testdata.
    self._testdata_path = '/testdata'
    self._valid_config_path = self._testdata_path + '/valid_config.yaml'
    self._blank_config_path = self._testdata_path + '/blank_config.yaml'

    self.fs.CreateFile(self._valid_config_path, contents=_VALID_CONFIG)
    self.fs.CreateFile(self._blank_config_path, contents=_BLANK_CONFIG)

    self.auth_patcher = mock.patch.object(auth, 'CloudCredentials')
    self.mock_creds = self.auth_patcher.start()
    self.mock_creds.return_value.get_credentials.return_value = (
        credentials.AnonymousCredentials())

  def tearDown(self):
    super(ManagerTest, self).tearDown()
    self.stubs.UnsetAll()
    builtins.open = self.real_open

    self.auth_patcher.stop()

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

  @mock.patch.object(utils, 'prompt_string', return_value='dev')
  @mock.patch.object(utils, 'prompt')
  def test_run(self, mock_prompt, mock_prompt_string):
    test_manager = gng_impl._Manager.new(
        self._valid_config_path, common.DEFAULT)
    side_effect = [
        gng_impl._CHANGE_PROJECT,
        gng_impl._HELP,
        gng_impl._QUIT,
    ]
    with mock.patch.object(utils, 'prompt_enum', side_effect=side_effect):
      self.assertEqual(test_manager.run(), 0)
    self.assertEqual(mock_prompt.call_count, 1)
    self.assertEqual(mock_prompt_string.call_count, 1)

  @mock.patch.object(utils, 'clear_screen')
  def test_main_help(self, mock_clear):
    with mock.patch.object(utils, 'input', return_value=''):
      test_manager = gng_impl._Manager(None, [], None)
      test_manager._main_help()
    self.assertEqual(self.stdout.getvalue(), _MAIN_HELP_GOLDEN)
    self.assertEqual(mock_clear.call_count, 1)

  def test_change_project(self):
    with mock.patch.object(
        utils, 'prompt_string', return_value='dev') as mock_prompt_string:
      test_manager = gng_impl._Manager.new(
          self._valid_config_path, common.DEFAULT)
      other_manager = test_manager._change_project()
    self.assertEqual(other_manager._config.project, 'dev-project')
    self.assertEqual(other_manager._config.client_secret, 'dev-secret')
    mock_prompt_string.assert_called_once_with(_CHANGE_PROJECT_GOLDEN)

  @mock.patch.object(utils, 'prompt_enum', return_value=gng_impl._QUIT)
  def test_main(self, mock_prompt_enum):
    with flagsaver.flagsaver(
        project=common.DEFAULT, config_file_path=self._valid_config_path):
      with self.assertRaises(SystemExit) as exit_err:
        gng_impl.main('unused')
        self.assertEqual(exit_err.exception.code, 0)
    self.assertEqual(mock_prompt_enum.call_count, 1)

  @parameterized.parameters('new', 'run')
  def test_main__errors(self, method):
    with mock.patch.object(
        gng_impl._Manager, method, side_effect=KeyboardInterrupt()):
      with flagsaver.flagsaver(
          project=common.DEFAULT, config_file_path=self._valid_config_path):
        with self.assertRaises(SystemExit) as exit_err:
          gng_impl.main('unused')
          self.assertEqual(exit_err.exception.code, 1)


if __name__ == '__main__':
  absltest.main()
