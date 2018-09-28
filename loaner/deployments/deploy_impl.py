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

"""The Grab n Go App Management Script.

usage: deploy_impl.py [FLAGS] [APPLICATION] [DEPLOYMENT]

Build and deploy the Grab n Go Loaner Web and Chrome Applications.

FLAGS (defaults set in deploy.sh)

APPLICATION: web or chrome

DEPLOYMENT: local, dev, qa, or prod

If no deployment is supplied the script defaults to building the application
locally.

Running the script with no arguments will show this help message.

Do not invoke directly -- use deploy.sh for instructions.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import datetime
import getpass
import json
import os
import shutil
import subprocess
import sys
import zipfile

from absl import app
from absl import flags
from absl import logging

from six.moves import input


FLAGS = flags.FLAGS

flags.DEFINE_list(
    'app_servers', None,
    'A comma separated list of available app servers. '
    'They should be in the format of name=project')
flags.DEFINE_string(
    'build_target', None,
    'The BUILD target specified in the loaner_appengine_binary rule found in '
    'the //web_app_dir/BUILD file')
flags.DEFINE_string(
    'chrome_app_dir', None,
    'The Chrome App Directory, relative to the @gng bazel WORKSPACE.')
flags.DEFINE_string(
    'loaner_path', None,
    'The absolute path to the loaner directory inside the @gng bazel '
    'WORKSPACE.')
flags.DEFINE_string(
    'version', None,
    'The version string to use.\n'
    'NOTE: If supplied it overrides the default version string which consists '
    'of the username of the user executing this script and the current date. '
    'The default version is unique for each user on a given day. '
    'Multiple deployments on a given day without a version specified will '
    'overwrite the existing App Engine version.')
flags.DEFINE_string(
    'web_app_dir', None,
    'The Web App Directory, relative to the @gng bazel WORKSPACE.')
flags.DEFINE_list(
    'yaml_files', None,
    'A comma separated list of the App Engine services to deploy.')

_LOCAL = 'local'

_MANIFEST_FILENAME = 'manifest.json'

_ZIPFILENAME = 'loaner_chrome_app.zip'

_APP_SERVER_ERROR = (
    'App Servers need to be a comma separated list in the following format:'
    ' type=project\nInstead received: {}\n'
    'Please check the deploy.sh configuration.')


class Error(Exception):
  """Base error class for this module."""


class ManifestError(Error):
  """Raised when there is an error with the manifest.json file."""

  def __init__(self, errno):
    self.errno = errno
    super(ManifestError, self).__init__()


def _ParseAppServers(app_servers):
  """Parse the app servers for name and project id.

  Args:
    app_servers: list|str|, a list of strings defining the Google Cloud Project
        IDs by friendly name.

  Returns:
    A dictionary with the friendly name as the key and the Google Cloud Project
        ID as the value.
  """
  return dict(server.split('=', 1) for server in app_servers)


def _AppServerValidator(app_servers):
  """Validate the App Engine servers are of the right format.

  Args:
    app_servers: list|str|, a list of strings defining the Google Cloud Project
        IDs by friendly name.

  Returns:
    True if the app_servers are in the correct format.

  Raises:
    flags.ValidationError, if the app_servers are in the incorrect format.
  """
  try:
    _ParseAppServers(app_servers)
  except ValueError:
    raise flags.ValidationError(_APP_SERVER_ERROR.format(app_servers))
  return True


def _ExecuteCommand(command):
  """Execute a command in the shell.

  Args:
    command: list, a list of strings the build a command to execute.

  Returns:
    A running process.
  """
  process = subprocess.Popen(command)
  result = process.wait()
  if result:
    sys.exit(result)
  return process


def _ZipRelativePath(path, name, root):
  """Create a new relative path ZipFile.

  Args:
    path: str, the path to begin zipping.
    name: str, the name of the archive.
    root: str, the root path to strip off the archived files.
  """
  archive = zipfile.ZipFile(name, 'w', zipfile.ZIP_DEFLATED)
  if os.path.isdir(path):
    _ZipRecursively(path, archive, root)
  else:
    archive.write(path)
  archive.close()


def _ZipRecursively(path, archive, root):
  """Recursive path ziping relative to the Chrome Application Bundle.

  Args:
    path: str, the path to traverse for the zip.
    archive: ZipFile, the archive instance to write to.
    root: str, the root path to strip off the archived files.
  """
  paths = os.listdir(path)
  for p in paths:
    p = os.path.join(path, p)
    if os.path.isdir(p):
      _ZipRecursively(p, archive, root)
    else:
      archive.write(p, os.path.relpath(p, root))
  return


class LoanerConfig(object):
  """Loaner configuration object to store relevant variables.

  Attributes:
    deployment_type: str, the friendly name of the Google Cloud Project to
        deploy to.
    loaner_path: str, the relative path to the loaner directory in the @gng
        bazel WORKSPACE.
  """

  def __init__(self, deployment_type, loaner_path):
    self._deployment_type = deployment_type
    self._loaner_path = loaner_path

  @property
  def workspace_path(self):
    """Returns the absolute loaner path as a string."""
    return os.path.abspath(os.path.join(self._loaner_path, '..'))

  @property
  def npm_path(self):
    """Retrieve the npm root path as a string."""
    return os.path.abspath(self._loaner_path)

  @property
  def node_modules_path(self):
    """Retrieve the node_modules path as a string."""
    return os.path.join(self.npm_path, 'node_modules')

  @property
  def on_local(self):
    """Returns whether or not this is to be deployed locally."""
    return self._deployment_type == _LOCAL

  @property
  def on_google_cloud_shell(self):
    """Returns whether or not we are on Google Cloud Shell."""
    return os.environ.get('CLOUD_SHELL') == 'true'


class AppEngineServerConfig(LoanerConfig):
  """App Engine specific server configurations.

  Attributes:
    app_servers: list|str|, app server definitions in the format name=project.
    build_target: str, the BUILD target for the App Engine binary.
    deployment_type: str, the friendly name of the Google Cloud Project to
        deploy to.
    loaner_path: str, the relative path to the loaner directory in the @gng
        bazel WORKSPACE.
    version: str, the App Engine version for this deployment.
    web_app_dir: str, the relative path to the web_app directory in the @gng
        bazel WORKSPACE.
    yaml_files: list|str|, a list of the yaml files defining the App Engine
        services to deploy.
  """

  def __init__(
      self, app_servers, build_target, deployment_type, loaner_path, version,
      web_app_dir, yaml_files):
    super(AppEngineServerConfig, self).__init__(deployment_type, loaner_path)
    self._build_target = build_target
    self._version = version
    self._web_app_dir = web_app_dir
    self._yaml_files = yaml_files
    self._app_servers = _ParseAppServers(app_servers)
    if self._deployment_type not in self._app_servers.keys():
      raise app.UsageError(
          'Application name provided is not in the list of App Servers.\n'
          'Please check the name and/or the deploy.sh configuration.')

  @property
  def project_id(self):
    """Returns the Google Cloud Project ID as a string."""
    return self._app_servers[self._deployment_type]

  @property
  def version(self):
    """Returns the version string for the App Engine services as a string."""
    if self._version:
      return self._version
    return '{user}-{date}'.format(
        user=getpass.getuser(), date=datetime.datetime.strftime(
            datetime.datetime.now(), '%Y%m%d'))

  @property
  def bundle_path(self):
    """Retrieve the path to the bazel built bundle as a string."""
    return os.path.join(
        self.workspace_path, 'bazel-bin', self._web_app_dir,
        '{bundle}.runfiles'.format(bundle=self._build_target))

  @property
  def app_path(self):
    """Retrieve the path to the bazel built application as a string."""
    return os.path.join(self.bundle_path, 'gng')

  @property
  def app_engine_deps_path(self):
    """Retrieve the App Engine Dependencies path as a string."""
    return os.path.join(
        self.app_path, 'external', 'com_google_appengine_python')

  @property
  def frontend_src_path(self):
    """Retrieve the Frontend path as a string."""
    return os.path.join(self.workspace_path, 'loaner', 'web_app', 'frontend')

  @property
  def frontend_bundle_path(self):
    """Retrieve the path to the bundled Frontend as a string."""
    return os.path.join(self.app_path, 'loaner', 'web_app', 'frontend', 'src')

  def _DeleteAppEngExtDepDir(self):
    """Deletes the GAE external dependencies directory."""
    if os.path.isdir(self.app_engine_deps_path):
      logging.info('Removing the local copy of the App Engine dependencies.')
      shutil.rmtree(self.app_engine_deps_path)

  def _DeleteNodeModulesDir(self):
    """Deletes the node_modules directory."""
    if os.path.isdir(self.node_modules_path):
      logging.info(
          'Removing the node_modules directory because we are building on '
          'Google Cloud Shell.')
      shutil.rmtree(self.node_modules_path)

  def _MoveWebAppFrontendBundle(self):
    """Prepare frontend bundle destination and move the build there."""
    if os.path.isdir(self.frontend_bundle_path):
      logging.info(
          'The bundled frontend exists, we are replacing it with a new build.')
      shutil.rmtree(self.frontend_bundle_path)
    logging.debug('Moving the frontend bundle into the web app bundle.')
    shutil.move(
        os.path.join(self.frontend_src_path, 'dist'), self.frontend_bundle_path)

  def _CleanWebAppBackend(self):
    """Run bazel clean --expunge in order to reduce filesystem utilziation."""
    logging.info('Running bazel clean --expunge_async because we are building '
                 'on Google Cloud Shell')
    _ExecuteCommand(['bazel', 'clean', '--expunge_async'])

  def _BuildWebAppBackend(self):
    """Build the Web Application's backend services."""
    logging.debug('Building the backend using Bazel...')
    _ExecuteCommand([
        'bazel', 'build', '//{}:{}'.format(
            self._web_app_dir, self._build_target)])
    if not self.on_local:
      self._DeleteAppEngExtDepDir()

  def _BuildWebAppFrontend(self):
    """Build the Web Application's frontend services."""
    logging.debug('Building the frontend using npm...')
    os.chdir(self.npm_path)
    _ExecuteCommand(['npm', 'install'])
    _ExecuteCommand(['npm', 'run', 'build:frontend'])
    if self.on_google_cloud_shell:
      self._DeleteNodeModulesDir()

  def _BundleWebApp(self):
    """Bundle the web application using bazel and npm."""
    self._BuildWebAppFrontend()
    self._BuildWebAppBackend()
    self._MoveWebAppFrontendBundle()

  def _GetYamlFile(self, yaml_filename):
    """Returns the full path for a given yaml file in the bundle.

    Args:
      yaml_filename: str, the basename for a yaml file.

    Returns:
      The full path for the yaml file in the App Engine bundle as a string.
    """
    return os.path.join(self.app_path, yaml_filename)

  def DeployWebApp(self):
    """Bundle then deploy (or run locally) the web application."""
    self._BundleWebApp()

    if self.on_local:
      print('Run locally...')
    else:
      cmds = [
          'gcloud', 'app', 'deploy', '--no-promote', '--project={}'.format(
              self.project_id), '--version={}'.format(self.version)]
      for yaml_filename in self._yaml_files:
        cmds.append(self._GetYamlFile(yaml_filename))
      logging.info(
          'Deploying to the Google Cloud project: %s using gcloud...',
          self.project_id)
      _ExecuteCommand(cmds)

    if self.on_google_cloud_shell:
      self._CleanWebAppBackend()


class ChromeAppConfig(LoanerConfig):
  """Chrome Application specific configurations.

  Attributes:
    chrome_app_dir: str, the relative path to the chrome_app directory in the
        @gng bazel WORKSPACE.
    deployment_type: str, the friendly name of the Google Cloud Project to
        deploy to.
    loaner_path: str, the relative path to the loaner directory in the @gng
        bazel WORKSPACE.
  """

  def __init__(self, chrome_app_dir, deployment_type, loaner_path):
    super(ChromeAppConfig, self).__init__(deployment_type, loaner_path)
    self._chrome_app_dir = chrome_app_dir

  @property
  def chrome_app_src_dir(self):
    """Retrieve the absolute path for the Chrome App source as a string."""
    return os.path.join(self.workspace_path, self._chrome_app_dir)

  @property
  def manifest_file(self):
    """Retrieve the absolute path for the manifest.json file as a string."""
    return os.path.join(self.chrome_app_src_dir, _MANIFEST_FILENAME)

  @property
  def chrome_app_temp_dir(self):
    """Retrieve the absolute path for the bundled Chrome App as a string."""
    return os.path.join(self.chrome_app_src_dir, 'dist')

  @property
  def chrome_app_archive(self):
    """Retrieve the final location of the Chrome Application's archive."""
    return os.path.join(self.workspace_path, _ZIPFILENAME)

  def _ManifestCheck(self):
    """Check the manifest.json file for required key/value pairs.

    Raises:
      ManifestError: when there is an issue with the manifest.json file.
    """
    logging.debug('Checking the manifest file...')
    with open(self.manifest_file, 'r') as manifest_data:
      try:
        data = json.load(manifest_data)
      # Catch syntax errors.
      except ValueError:
        sys.stderr.write(
            "The there is a syntax error in the Chrome App's"
            "manifest.json file, located at: {}\n".format(self.manifest_file))
        raise ManifestError(os.EX_SOFTWARE)
      # Set the new version.
      current_version = data['version']
      data['version'] = input(
          'The current Chrome App version is {}, '
          'please enter the new version: '.format(current_version))
      # Check for the Chrome App Key.
      if not data['key']:
        sys.stderr.write(
            "The manifest key is missing, please place it in the Chrome App's "
            "manifest.json file, located at: {}\n".format(self.manifest_file))
        raise ManifestError(os.EX_SOFTWARE)
      # Check for the OAuth2 Client ID.
      if not data['oauth2']['client_id']:
        sys.stderr.write(
            "The OAuth2 Client ID is missing for the Chrome App, please place "
            "it in the Chrome App's manifest.json, "
            "file located at: {}\n".format(
                self.manifest_file))
        raise ManifestError(os.EX_SOFTWARE)

    # Write new version to manifest.
    with open(self.manifest_file, 'w+') as manifest_data:
      json.dump(
          data, manifest_data, sort_keys=True, indent=2, separators=(',', ': '))

  def _BuildChromeApp(self):
    """Build and bundle the Chrome App."""
    logging.debug('Building the Chrome Application...')
    self._ManifestCheck()
    os.chdir(self.npm_path)
    _ExecuteCommand(['npm', 'install'])
    _ExecuteCommand(['npm', 'run', 'build:chromeapp:once'])
    os.chdir(self.chrome_app_src_dir)
    if self.on_local:
      print('Local bundling coming soon...')
    else:
      logging.info('Zipping the Loaner Chrome Application...')
      _ZipRelativePath(
          self.chrome_app_temp_dir, _ZIPFILENAME, self.chrome_app_temp_dir)
      if os.path.isfile(self.chrome_app_archive):
        os.remove(self.chrome_app_archive)
      shutil.move(
          os.path.join(self.chrome_app_src_dir, _ZIPFILENAME),
          self.chrome_app_archive)
      logging.info(
          'The Loaner Chrome Application zip can be found %s',
          self.chrome_app_archive)
      logging.info('Removing the temp files for the Chrome App...')
      shutil.rmtree(self.chrome_app_temp_dir)

  def DeployChromeApp(self):
    """Bundle and deploy the Chrome App."""
    self._BuildChromeApp()


def main(argv):
  argv = argv[1:]  # Discard the script name.

  # No arguments passed, show usage statement.
  if len(argv) < 1:
    app.usage(shorthelp=True, exitcode=1)

  # Application to deploy: web or chrome.
  application = argv[0]

  # Server to deploy to: local, dev, or prod.
  try:
    deployment_type = argv[1]
  except IndexError:
    logging.info('No deployment type was provided, defaulting to local.')
    deployment_type = _LOCAL

  if application == 'web':
    # If application is web, begin build and deploy for the web app.
    app_engine_server_config = AppEngineServerConfig(
        app_servers=FLAGS.app_servers,
        build_target=FLAGS.build_target,
        deployment_type=deployment_type,
        loaner_path=FLAGS.loaner_path,
        web_app_dir=FLAGS.web_app_dir,
        yaml_files=FLAGS.yaml_files,
        version=FLAGS.version)

    app_engine_server_config.DeployWebApp()

  elif application == 'chrome':
    # If application is chrome, begin build and deploy for the chrome app.
    chrome_app_config = ChromeAppConfig(
        chrome_app_dir=FLAGS.chrome_app_dir,
        deployment_type=deployment_type,
        loaner_path=FLAGS.loaner_path)

    try:
      chrome_app_config.DeployChromeApp()
    except ManifestError as err:
      sys.exit(err.errno)

  else:
    app.usage(shorthelp=True, exitcode=1)


if __name__ == '__main__':
  flags.register_validator('app_servers', _AppServerValidator)
  flags.mark_flags_as_required([
      'app_servers', 'build_target', 'chrome_app_dir', 'loaner_path',
      'web_app_dir', 'yaml_files'])
  app.run(main)
