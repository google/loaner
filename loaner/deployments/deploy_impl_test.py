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

"""Tests for deployments.deploy_impl."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

# Prefer Python 3 and fall back on Python 2.
# pylint:disable=g-statement-before-imports,g-import-not-at-top
try:
  import builtins
except ImportError:
  import __builtin__ as builtins
# pylint:enable=g-statement-before-imports,g-import-not-at-top

import datetime
import json
import subprocess

from absl import app
from absl import flags
from pyfakefs import fake_filesystem
from pyfakefs import fake_filesystem_shutil
from pyfakefs import mox3_stubout

import freezegun
import mock

from absl.testing import absltest
from loaner.deployments import deploy_impl

_WORKSPACE_PATH = '/this/is/a/workspace'
_LOANER_PATH = _WORKSPACE_PATH + '/loaner'
_APP_SERVERS = ['dev=development', 'prod=production']
_BUILD_TARGET = 'runfiles'
_CHROME_APP_DIR = 'loaner/chrome_app'
_CHROME_ZIP = 'loaner_chrome_app.zip'
_DEPLOYMENT_TYPE = 'prod'
_VERSION = 'new_version'
_WEB_APP_DIR = 'loaner/web_app'
_YAML_FILES = ['app.yaml', 'endpoints.yaml']

_CORRECT_JSON = '''{
  "version": "version_value",
  "key": "key_value",
  "oauth2": {
    "client_id": "client_id_value"
    }
  }
'''

_JSON_SYNTAX_ERR = '''{
  "version": "version_value"
  "key": "key_value",
  "oauth2": {
    "client_id": "client_id_value"
    }
  }
'''

_JSON_MISSING_KEY = '''{
  "version": "version_value",
  "key": "",
  "oauth2": {
    "client_id": "client_id_value"
    }
  }
'''

_JSON_MISSING_CLIENT_ID = '''{
  "version": "version_value",
  "key": "key_value",
  "oauth2": {
    "client_id": ""
    }
  }
'''


class DeployImplTest(absltest.TestCase):

  def setUp(self):
    super(DeployImplTest, self).setUp()
    # Save the real modules for clean up.
    self.real_open = builtins.open
    # Create a fake file system and stub out builtin modules.
    self.fs = fake_filesystem.FakeFilesystem()
    self.os = fake_filesystem.FakeOsModule(self.fs)
    self.open = fake_filesystem.FakeFileOpen(self.fs)
    self.shutil = fake_filesystem_shutil.FakeShutilModule(self.fs)
    self.stubs = mox3_stubout.StubOutForTesting()
    self.stubs.SmartSet(builtins, 'open', self.open)
    self.stubs.SmartSet(deploy_impl, 'os', self.os)
    self.stubs.SmartSet(deploy_impl, 'shutil', self.shutil)
    # Populate the fake file system with the expected directories and files.
    self.fs.CreateDirectory('/this/is/a/workspace/loaner/web_app/frontend/dist')
    self.fs.CreateDirectory('/this/is/a/workspace/loaner/chrome_app/dist')
    self.fs.CreateFile('/this/is/a/workspace/loaner/web_app/app.yaml')
    self.fs.CreateFile('/this/is/a/workspace/loaner/web_app/endpoints.yaml')

  def tearDown(self):
    super(DeployImplTest, self).tearDown()
    self.stubs.UnsetAll()
    builtins.open = self.real_open

  def CreateTestAppEngineConfig(
      self, app_servers=None, build_target=_BUILD_TARGET,
      deployment_type=_DEPLOYMENT_TYPE, loaner_path=_LOANER_PATH,
      version=_VERSION, web_app_dir=_WEB_APP_DIR, yaml_files=None):
    """Create an instance of the deploy_impl.AppEngineServerConfig for testing.

    This is a helper function to create a correctly populated
    AppEngineServerConfig, each argument can be overridden to test the handling
    of individual arguments.

    Args:
      app_servers: list|str|, app server definitions in the format name=project.
      build_target: str, the BUILD target for the App Engine binary.
      deployment_type: str, the name of the server to deploy to.
      loaner_path: str, the relative path to the loaner directory in the @gng
          bazel WORKSPACE.
      version: str, the App Engine version for this deployment.
      web_app_dir: str, the relative path to the web_app directory in the @gng
          bazel WORKSPACE.
      yaml_files: list|str|, a list of the yaml files defining the App Engine
          services to deploy.

    Returns:
      An instance of deploy_impl.AppEngineServerConfig.
    """
    if app_servers is None:
      app_servers = _APP_SERVERS
    if yaml_files is None:
      yaml_files = _YAML_FILES
    return deploy_impl.AppEngineServerConfig(
        app_servers=app_servers, build_target=build_target,
        deployment_type=deployment_type, loaner_path=loaner_path,
        yaml_files=yaml_files, version=version, web_app_dir=web_app_dir)

  def CreateTestChromeAppConfig(
      self, chrome_app_dir=_CHROME_APP_DIR, deployment_type=_DEPLOYMENT_TYPE,
      loaner_path=_LOANER_PATH):
    """Create an instance of the deploy_impl.ChromeAppConfig for testing.

    This is a helper function to create a correctly populated ChromeAppConfig,
    each argument can be overridden to test the handling of individual
    arguments.

    Args:
      chrome_app_dir: str, the relative path to the chrome_app directory in the
          @gng bazel WORKSPACE.
      deployment_type: str, the name of the server to deploy to.
      loaner_path: str, the relative path to the loaner directory in the @gng
          bazel WORKSPACE.

    Returns:
      An instance of deploy_impl.ChromeAppConfig.
    """
    return deploy_impl.ChromeAppConfig(
        chrome_app_dir=chrome_app_dir, deployment_type=deployment_type,
        loaner_path=loaner_path)

  def testParseAppServers(self):
    """Test that the app server parser returns the expected dictionary."""
    self.assertDictEqual(
        deploy_impl._ParseAppServers(_APP_SERVERS),
        {'dev': 'development', 'prod': 'production'})

  def testAppServerValidator(self):
    """Test when an app server string is correct."""
    self.assertTrue(
        deploy_impl._AppServerValidator(app_servers=_APP_SERVERS))

  def testAppServerValidatorWithMalformedFlag(self):
    """Test that incorrect input handling, raises ValidationError."""
    # Test that the second split (ValueError) is caught.
    with self.assertRaises(flags.ValidationError):
      deploy_impl._AppServerValidator(app_servers=['wrong:format'])

  def testExecuteCommand(self):
    """Test that a process is returned when executing a command."""
    self.assertIsInstance(
        deploy_impl._ExecuteCommand(['echo', 'foobar']), subprocess.Popen)

  def testExecuteFailingCommand(self):
    """Test a no-op command, raises SystemExit."""
    with self.assertRaises(SystemExit):
      deploy_impl._ExecuteCommand(['false'])

  @mock.patch.object(deploy_impl, '_ZipRecursively', autospec=True)
  @mock.patch.object(deploy_impl, 'zipfile', autospec=True)
  def testZipRelativePath(self, mock_zipfile, mock_ziprecursively):
    """Test zipping a relative path."""
    path = '/this/is/a/workspace/loaner/chrome_app'
    name = 'archive'
    mock_archive = mock_zipfile.ZipFile.return_value
    deploy_impl._ZipRelativePath(path, name, path)
    assert mock_zipfile.ZipFile.call_count == 1
    assert mock_ziprecursively.call_count == 1
    assert mock_archive.write.call_count == 0
    assert mock_archive.close.call_count == 1

  @mock.patch.object(deploy_impl, '_ZipRecursively', autospec=True)
  @mock.patch.object(deploy_impl, 'zipfile', autospec=True)
  def testZipRelativeFile(self, mock_zipfile, mock_ziprecursively):
    """Test zipping a single file."""
    path = '/this/is/a/workspace/loaner/chrome_app'
    name = 'archive'
    full_path = path + '/' + name
    mock_archive = mock_zipfile.ZipFile.return_value
    deploy_impl._ZipRelativePath(full_path, name, path)
    assert mock_zipfile.ZipFile.call_count == 1
    mock_archive.write.assert_called_once_with(full_path)
    assert mock_ziprecursively.call_count == 0
    assert mock_archive.close.call_count == 1

  @mock.patch.object(deploy_impl, 'zipfile', autospec=True)
  def testZipRecursively(self, mock_zipfile):
    """Test the recursive zip."""
    path = '/this/is/a/workspace/loaner/chrome_app'
    self.fs.CreateFile('/this/is/a/workspace/loaner/chrome_app/src/file')
    self.fs.CreateFile('/this/is/a/workspace/loaner/chrome_app/assets/asset')
    self.fs.CreateFile('/this/is/a/workspace/loaner/chrome_app/archive')
    mock_archive = mock_zipfile.ZipFile.return_value
    deploy_impl._ZipRecursively(path, mock_archive, path)
    assert mock_archive.write.call_count == 3

  def testLoanerConfigInit(self):
    """Test the basic LoanerConfig creation."""
    test_loaner_config = deploy_impl.LoanerConfig(
        deployment_type=_DEPLOYMENT_TYPE, loaner_path=_LOANER_PATH)
    self.assertFalse(test_loaner_config.on_local)
    self.assertEqual(_LOANER_PATH, test_loaner_config._loaner_path)
    self.assertEqual(_WORKSPACE_PATH, test_loaner_config.workspace_path)
    self.assertEndsWith(test_loaner_config.npm_path, '/loaner')
    self.assertEndsWith(test_loaner_config.node_modules_path, '/node_modules')

  def testAppEngineServerConfigInit(self):
    """Test the basic AppEngineServerConfig creation."""
    test_app_engine_config = self.CreateTestAppEngineConfig()
    # Test that the Google Cloud Project was correctly split.
    self.assertEqual(test_app_engine_config.project_id, 'production')
    # Test that the version supplied is the default.
    self.assertEqual(test_app_engine_config.version, _VERSION)
    # Test that the bundle_path ends in .runfiles
    self.assertEndsWith(test_app_engine_config.bundle_path, '.runfiles')
    # Test that the app_path end with the WORKSPACE name (gng).
    self.assertEndsWith(test_app_engine_config.app_path, '.runfiles/gng')
    # Test that the app_engine_path ends with the bazel package name for app
    # engine.
    self.assertEndsWith(
        test_app_engine_config.app_engine_deps_path,
        '.runfiles/gng/external/com_google_appengine_python')
    # Test that the frontend_src_path ends with the frontend package.
    self.assertEndsWith(
        test_app_engine_config.frontend_src_path,
        'loaner/web_app/frontend')
    # Test that the frontend_bundle_path ends with the bundled frontend package.
    self.assertEndsWith(
        test_app_engine_config.frontend_bundle_path,
        'loaner/web_app/frontend/src')

  @mock.patch.object(deploy_impl.getpass, 'getuser', autospec=True)
  def testAppEngineServerConfigWithVersionSupplied(self, mock_getuser):
    """Test that the supplied version overrides the default."""
    now = datetime.datetime(year=2017, month=1, day=1)
    with freezegun.freeze_time(now):
      mock_getuser.return_value = 'daredevil'
      # Test that the default version is correctly created when a version is not
      # provided.
      test_app_engine_config = self.CreateTestAppEngineConfig(version=None)
      self.assertEqual('daredevil-20170101', test_app_engine_config.version)

  def testAppEngineServerConfigWithMissingDeploymentServer(self):
    """Test a deployment server that is not in appservers, raises UsageError."""
    with self.assertRaises(app.UsageError):
      self.CreateTestAppEngineConfig(deployment_type='not_real_server')

  def testMoveWebAppFrontendBundle(self):
    """Test that frontend is moved correctly."""
    fake_frontend_path = (
        '/this/is/a/workspace/bazel-bin/loaner/web_app/runfiles.runfiles/gng/'
        'loaner/web_app/frontend/src')
    self.fs.CreateDirectory(fake_frontend_path)
    test_app_engine_config = self.CreateTestAppEngineConfig()
    test_app_engine_config._MoveWebAppFrontendBundle()
    assert self.os.path.isdir(fake_frontend_path)
    assert not self.os.path.isdir(
        '/this/is/a/workspace/loaner/web_app/frontend/dist')

  @mock.patch.object(deploy_impl, '_ExecuteCommand', autospec=True)
  def testBuildWebAppBackend(self, mock_execute):
    """Test that the build web application backend executes."""
    fake_app_engine_deps_path = (
        '/this/is/a/workspace/bazel-bin/loaner/web_app/runfiles.runfiles/gng/'
        'external/com_google_appengine_python')
    self.fs.CreateDirectory(fake_app_engine_deps_path)
    test_app_engine_config = self.CreateTestAppEngineConfig()
    test_app_engine_config._BuildWebAppBackend()
    assert mock_execute.call_count == 1
    self.assertFalse(self.os.path.isdir(fake_app_engine_deps_path))

  @mock.patch.object(deploy_impl.AppEngineServerConfig, '_DeleteNodeModulesDir')
  @mock.patch.object(deploy_impl, '_ExecuteCommand', autospec=True)
  def testBuildWebAppFrontend(self, mock_execute, mock_del):
    """Test that the build web application frontend executes."""
    test_app_engine_config = self.CreateTestAppEngineConfig()
    test_app_engine_config._BuildWebAppFrontend()
    assert mock_execute.call_count == 2
    mock_del.assert_not_called()
    assert self.os.path.isdir(
        '/this/is/a/workspace/loaner/web_app/frontend/dist')

  @mock.patch.object(deploy_impl, '_ExecuteCommand', autospec=True)
  def testBuildWebAppFrontendGoogleCloudShell(self, mock_execute):
    """Test that the build web application frontend executes on GCS."""
    self.fs.CreateDirectory('/this/is/a/workspace/loaner/node_modules')
    test_app_engine_config = self.CreateTestAppEngineConfig()
    self.os.environ['CLOUD_SHELL'] = 'true'
    test_app_engine_config._BuildWebAppFrontend()
    assert not self.os.path.isdir(test_app_engine_config.node_modules_path)
    assert mock_execute.call_count == 2
    self.os.environ['CLOUD_SHELL'] = 'false'

  @mock.patch.object(
      deploy_impl.AppEngineServerConfig, '_BuildWebAppFrontend', autospec=True)
  @mock.patch.object(
      deploy_impl.AppEngineServerConfig, '_BuildWebAppBackend', autospec=True)
  @mock.patch.object(
      deploy_impl.AppEngineServerConfig, '_MoveWebAppFrontendBundle')
  def testBundleWebApp(self, mock_frontend, mock_backend, mock_move):
    """Test that the bundle web application executes both web app builds."""
    test_app_engine_config = self.CreateTestAppEngineConfig()
    test_app_engine_config._BundleWebApp()
    assert mock_backend.call_count == 1
    assert mock_frontend.call_count == 1
    assert mock_move.call_count == 1

  def testGetYamlFile(self):
    """Test that the get yaml file returns the full path for a yaml file."""
    test_app_engine_config = self.CreateTestAppEngineConfig()
    for yaml_filename in test_app_engine_config._yaml_files:
      yaml_path = test_app_engine_config._GetYamlFile(yaml_filename)
      self.assertEndsWith(yaml_path, '.runfiles/gng/{}'.format(yaml_filename))

  @mock.patch.object(deploy_impl, '_ExecuteCommand', autospec=True)
  @mock.patch.object(
      deploy_impl.AppEngineServerConfig, '_GetYamlFile', autospec=True)
  @mock.patch.object(
      deploy_impl.AppEngineServerConfig, '_BundleWebApp', autospec=True)
  def testDeployWebApp(self, mock_bundle, mock_get_yaml, mock_execute):
    """Test that the web application deployment bundles the app and deploys."""
    self.os.environ['CLOUD_SHELL'] = 'true'
    test_app_engine_config = self.CreateTestAppEngineConfig()
    test_app_engine_config.DeployWebApp()
    assert mock_bundle.call_count == 1
    assert mock_get_yaml.call_count == len(test_app_engine_config._yaml_files)
    assert mock_execute.call_count == 2
    self.os.environ['CLOUD_SHELL'] = 'false'

  def testChromeAppConfigInit(self):
    """Test the basic ChromeAppConfig creation."""
    test_chrome_app_config = self.CreateTestChromeAppConfig()
    # Test that the manifest file is in the chrome app dir.
    self.assertEndsWith(
        test_chrome_app_config.manifest_file, 'loaner/chrome_app/manifest.json')
    # Test that the chrome_app_src_dir is the chrome_app.
    self.assertEndsWith(
        test_chrome_app_config.chrome_app_src_dir, 'loaner/chrome_app')
    # Test that the chrome_app_temp_dir is the chrome_app/dist path.
    self.assertEndsWith(
        test_chrome_app_config.chrome_app_temp_dir, 'loaner/chrome_app/dist')

  @mock.patch.object(deploy_impl, 'input', autospec=True, return_value='1.0')
  def testManifestCheck(self, mock_rawinput):
    """Test the manifest file check opens and loads json data."""
    file_name = '/this/is/a/workspace/loaner/chrome_app/manifest.json'
    self.fs.CreateFile(file_name, contents=_CORRECT_JSON)
    test_chrome_app_config = self.CreateTestChromeAppConfig()
    test_chrome_app_config._ManifestCheck()
    assert mock_rawinput.call_count == 1
    with open(file_name, 'r') as f:
      data = json.load(f)
      assert data['version'] == '1.0'

  @mock.patch.object(deploy_impl, 'input', autospec=True, return_value='1.0')
  def testManifestJsonFailure(self, mock_rawinput):
    """Test the manifest check fails given syntactically invalid json data."""
    self.fs.CreateFile(
        '/this/is/a/workspace/loaner/chrome_app/manifest.json',
        contents=_JSON_SYNTAX_ERR)
    test_chrome_app_config = self.CreateTestChromeAppConfig()
    with self.assertRaises(deploy_impl.ManifestError):
      test_chrome_app_config._ManifestCheck()
    assert mock_rawinput.call_count == 0

  @mock.patch.object(deploy_impl, 'input', autospec=True, return_value='1.0')
  def testManifestCheckKeyFailure(self, mock_rawinput):
    """Test the manifest check fails without a 'key' value."""
    self.fs.CreateFile(
        '/this/is/a/workspace/loaner/chrome_app/manifest.json',
        contents=_JSON_MISSING_KEY)
    test_chrome_app_config = self.CreateTestChromeAppConfig()
    with self.assertRaises(deploy_impl.ManifestError):
      test_chrome_app_config._ManifestCheck()
    assert mock_rawinput.call_count == 1

  @mock.patch.object(deploy_impl, 'input', autospec=True, return_value='1.0')
  def testManifestCheckOauthIdFailure(self, mock_rawinput):
    """Test the manifest check fails without an oauth client id value."""
    self.fs.CreateFile(
        '/this/is/a/workspace/loaner/chrome_app/manifest.json',
        contents=_JSON_MISSING_CLIENT_ID)
    test_chrome_app_config = self.CreateTestChromeAppConfig()
    with self.assertRaises(deploy_impl.ManifestError):
      test_chrome_app_config._ManifestCheck()
    assert mock_rawinput.call_count == 1

  @mock.patch.object(deploy_impl, '_ZipRelativePath', autospec=True)
  @mock.patch.object(deploy_impl, '_ExecuteCommand', autospec=True)
  @mock.patch.object(
      deploy_impl.ChromeAppConfig, '_ManifestCheck', autospec=True)
  def testBuildChromeApp(self, mock_manifest, mock_execute, mock_zip):
    """Test that the build Chrome Application executes."""
    self.fs.CreateFile(
        '/this/is/a/workspace/loaner/chrome_app/loaner_chrome_app.zip')
    test_chrome_app_config = self.CreateTestChromeAppConfig()
    test_chrome_app_config._BuildChromeApp()
    assert mock_manifest.call_count == 1
    assert mock_execute.call_count == 2
    assert mock_zip.call_count == 1

  @mock.patch.object(
      deploy_impl.ChromeAppConfig, '_BuildChromeApp', autospec=True)
  def testDeployChromeApp(self, mock_buildchromeapp):
    """Test that the Chrome App deployment first builds."""
    test_chrome_app_config = self.CreateTestChromeAppConfig()
    test_chrome_app_config.DeployChromeApp()
    assert mock_buildchromeapp.call_count == 1


if __name__ == '__main__':
  absltest.main()
