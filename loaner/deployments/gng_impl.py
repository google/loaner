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

"""The Grab n Go management script.

Usage: gng_impl [FLAGS]
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import collections
import datetime
import getpass
import inspect
import sys

from absl import app
from absl import flags
from absl import logging

import six

from loaner.deployments.lib import app_constants
from loaner.deployments.lib import app_engine
from loaner.deployments.lib import auth
from loaner.deployments.lib import common
from loaner.deployments.lib import datastore
from loaner.deployments.lib import directory
from loaner.deployments.lib import menu
from loaner.deployments.lib import storage
from loaner.deployments.lib import utils

FLAGS = flags.FLAGS

flags.DEFINE_bool(
    'prefer_gcs', True,
    'Prefer loading constants from Cloud Storage.\n'
    'An example motivation for setting this to false would be to automate '
    'deployments using command line flags.'
)

flags.DEFINE_string(
    'app_version', None,
    'The version string to use when deploying to App Engine.\n'
    'NOTE: If supplied it overrides the default version string which consists '
    'of the username of the user executing this script and the current date. '
    'The default version is unique for each user on a given day. '
    'Multiple deployments on a given day without a version specified will '
    'overwrite the existing App Engine version.\n'
    'Requirements: The version string must only be composed of lower case '
    "letters, numbers, and hyphens. The versions 'default' and 'latest' are "
    "reserved and cannot be used. The version cannot begin with 'ah-'."
)

# API Client modules from which OAuth2 scopes should be extracted.
_API_CLIENT_MODULES = (
    app_engine,
    datastore,
    directory,
    storage,
)

# Main menu options.
_CHANGE_PROJECT = 'change project'
_CONFIGURE = 'configure'
_QUIT = 'quit'


def _get_oauth_scopes(modules=_API_CLIENT_MODULES):
  """Retrieves all OAuth2 Scopes required for management.

  Args:
    modules: Sequence[module], a sequence of modules to extract OAuth2 scopes
        from.

  Returns:
    A list of all of the OAuth2 Scopes required for management.
  """
  scopes = []
  for client in modules:
    for name, cls in inspect.getmembers(client, inspect.isclass):
      if name.endswith('API') and hasattr(cls, 'SCOPES'):
        scopes.extend(cls.SCOPES)
  return sorted(list(set(scopes)))


class _AuthError(Exception):
  """Raised when an error occurs during authentication."""


class _Manager(object):
  """Grab n Go management object."""

  def __init__(
      self, config, constants, creds, prefer_gcs, gae_admin_api=None,
      datastore_api=None, directory_api=None, storage_api=None, version=None,
  ):
    """Initializes manager attributes.

    Args:
      config: common.Config, the config for this project.
      constants: List[app_constants.Constant], a list of project level
          constants.
      creds: auth.CloudCredentials, the credentials to use when making Google
          API calls.
      prefer_gcs: bool, if True constants will be loaded from Google Cloud
          Storage and will override any constants provided as command line
          flags.
      gae_admin_api: Optional[app_engine.AdminAPI], the Google App Engine Admin
          API client.
      datastore_api: Optional[datastore.DatastoreAPI], the Google Datastore API
          client.
      directory_api: Optional[directory.DirectoryAPI], the Google Admin SDK
          Directory API client.
      storage_api: Optional[storage.CloudStorageAPI], the Google Cloud Storage
          API client.
      version: Optional[str], the version string to use for the next deployed
          version.
    """
    self._config = config
    self._constants = constants
    self._cloud_creds = creds
    self._prefer_gcs = prefer_gcs
    self._gae_admin_api = gae_admin_api
    self._datastore_api = datastore_api
    self._directory_api = directory_api
    self._storage_api = storage_api
    self._version = version
    self._options = collections.OrderedDict([
        (_CHANGE_PROJECT, menu.Option(
            _CHANGE_PROJECT,
            'Change the Cloud Project currently being managed',
            self._change_project,
        )),
        (_CONFIGURE, menu.Option(
            _CONFIGURE, 'Configure project level constants', self._configure)),
        (_QUIT, menu.Option(_QUIT, 'Quit the Grab n Go Management script')),
    ])

  def __str__(self):
    return '{} for project {!r}'.format(
        self.__class__.__name__, self._config.project)

  def __repr__(self):
    return '<{0}.new({1}, {2}, {3})>'.format(
        self.__class__.__name__, self._config.path, self._prefer_gcs,
        self._config.key)

  @property
  def version(self):
    """Getter for the version string.

    If no version was provided upon creation (e.g. via a command line flag), we
    will attempt to auto generate a version string using the username and the
    current date.

    Returns:
      The version as a string.
    """
    if self._version is None:
      self.version = '{user}-{date}'.format(
          user=getpass.getuser().strip().lower(),
          date=datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d'))
    return self._version

  @version.setter
  def version(self, version):
    """Setter for the version string.

    Args:
      version: str, the version string to use for the next deployment.

    Raises:
      ValueError: when the provided version does not meet the requirements.
    """
    self._version = utils.VersionParser().parse(version)

  @classmethod
  def new(cls, config_file_path, prefer_gcs, project_key=None, version=None):
    """Creates a new instance of a Grab n Go Manager.

    Args:
      config_file_path: str, the name or path to the config file.
      prefer_gcs: bool, if True constants will be loaded from Google Cloud
          Storage and will override any constants provided as command line
          flags.
      project_key: Optional[str], the project friendly name, used as the
          top-level key in the config file.
      version: Optional[str], the version string to use for the next deployed
          version.

    Returns:
      A new instance of a Grab n Go Manager.

    Raises:
      _AuthError: when unable to generate valid credentials.
    """
    if project_key is None:
      project_key = utils.prompt_string(
          'A project name was not provided, which project would you like to '
          'configure?\nNOTE: If you are unsure, or if you plan to use only one '
          'Google Cloud Project, you can use the default.\n'
          'The following projects are currently defined in {!r}:\n {}'.format(
              config_file_path,
              ', '.join(common.get_available_configs(config_file_path))),
          default=common.DEFAULT).lower()
    logging.debug(
        'Project key %r was provided, attempting to load from yaml.',
        project_key)

    try:
      config = common.ProjectConfig.from_yaml(project_key, config_file_path)
    except (common.ConfigError, KeyError) as err:
      logging.debug(
          'Failed to initialize project with key %r: %s\n'
          'Attempting to load new config...', project_key, err)
      utils.write(
          'There does not appear to be a saved configuration for this project: '
          '{!r}. Before we can get started, we need to gather some information.'
          '\n'.format(project_key)
      )
      config = common.ProjectConfig.from_prompts(project_key, config_file_path)
      config.write()

    try:
      cloud_creds = auth.CloudCredentials(config, _get_oauth_scopes())
    except auth.InvalidCredentials as err:
      utils.write(
          'We were unable to create credentials for this configuration, please '
          'verify the Project ID, OAuth2 Client ID and Client Secret are '
          'correct and then re-enter them in the following prompts.'
      )
      config = common.ProjectConfig.from_prompts(project_key, config_file_path)
      config.write()
      return cls.new(config_file_path, prefer_gcs, project_key)

    gae_admin_api = app_engine.AdminAPI.from_config(config, cloud_creds)
    datastore_api = datastore.DatastoreAPI.from_config(config, cloud_creds)
    directory_api = directory.DirectoryAPI.from_config(config, cloud_creds)
    storage_api = storage.CloudStorageAPI.from_config(config, cloud_creds)

    constants = app_constants.get_constants_from_flags()

    new_manager = cls(
        config, constants, cloud_creds, prefer_gcs,
        gae_admin_api=gae_admin_api,
        datastore_api=datastore_api,
        directory_api=directory_api,
        storage_api=storage_api,
        version=version,
    )

    if prefer_gcs:
      new_manager.load_constants_from_storage()

    return new_manager

  def run(self):
    """Runs the Grab n Go manager."""
    try:
      while True:
        utils.clear_screen()
        utils.write('Which of the following actions would you like to take?\n')
        for opt in self._options.values():
          utils.write('Action: {!r}\nDescription: {}\n'.format(
              opt.name, opt.description))
        action = utils.prompt_enum(
            '', accepted_values=self._options.keys(),
            case_sensitive=False).strip().lower()
        callback = self._options[action].callback
        if callback is None:
          break
        self = callback()
    finally:
      utils.write(
          'Done managing Grab n Go for Cloud Project {!r}.'.format(
              self._config.project))

  def _change_project(self):
    """Changes the project configuration being managed.

    Returns:
      A new instance of _Manager for the selected project.
    """
    project_key = utils.prompt_string(
        'You are currently managing Google Cloud Project {!r}.\n'
        'This project is currently saved as {!r}.\n'
        'All of the currently configured projects include: {}.\n'
        'Which project would you like to switch to?'.format(
            self._config.project, self._config.key,
            ', '.join(common.get_available_configs(self._config.path))))
    return _Manager.new(
        self._config.path, self._prefer_gcs, project_key=project_key,
        version=self._version)

  def _configure(self):
    """Prompts the user for project wide constants.

    Returns:
      An updated instance of _Manager.
    """
    opts = sorted(self._constants.keys())
    opts.append(_QUIT)
    try:
      while True:
        utils.clear_screen()
        utils.write('Here are the project wide constants for {!r}:\n'.format(
            self._config.project))
        configured, unconfigured = [], []
        for name in sorted(self._constants.keys()):
          if self._constants[name].valid:
            configured.append(name)
          else:
            unconfigured.append(name)
          utils.write(
              'Constant: {!r}\nDescription: {}\nCurrent Value: {}\n'.format(
                  name, self._constants[name].message,
                  self._constants[name].value))
        choice = utils.prompt_enum(
            'Which constant would you like to configure?\n'
            'Currently configured constants include: {}\n'
            'Currently unconfigured constants include: {}\n'.format(
                ', '.join(configured) or 'None',
                ', '.join(unconfigured) or 'None'),
            accepted_values=opts,
            case_sensitive=False).strip().lower()
        if choice == _QUIT:
          break
        else:
          self._constants[choice].prompt()
          self._save_constants()
    finally:
      utils.write(
          'Exiting configuration menu, to return enter {!r} in the main menu.\n'
          'Returning to the main menu.'.format(_CONFIGURE))
    return self

  def _save_constants(self):
    """Writes constants to the configured Google Cloud Storage Bucket."""
    try:
      self._storage_api.insert_blob(
          self._config.constants_storage_path,
          {name: const.value for name, const in six.iteritems(self._constants)},
          bucket_name=self._config.bucket,
      )
    except storage.NotFoundError as err:
      logging.error('Failed to get the bucket for this project: %s', err)

  def load_constants_from_storage(self):
    """Attempts to load constants from Google Cloud Storage."""
    try:
      constants = self._storage_api.get_blob(
          self._config.constants_storage_path,
          self._config.bucket,
      )
    except storage.NotFoundError as err:
      logging.error('Constants were not found in storage: %s', err)
    else:
      for name in self._constants.keys():
        try:
          self._constants[name].value = constants[name]
        except ValueError:
          logging.warning(
              'The value %r for %r stored in Google Cloud Storage does not meet'
              ' the requirements. Using the default value...',
              constants[name], name)
        except KeyError:
          logging.info(
              'The key %r was not found in the stored constants, this may be '
              'because a new constant was added since your most recent '
              'configuration. To resolve run `configure` in the main menu.',
              name)


def main(argv):
  del argv  # Unused.
  utils.clear_screen()
  utils.write('Welcome to the Grab n Go management script!\n')

  try:
    _Manager.new(
        FLAGS.config_file_path,
        FLAGS.prefer_gcs,
        project_key=FLAGS.project,
        version=FLAGS.app_version,
    ).run()
  except KeyboardInterrupt as err:
    logging.error('Manager received CTRL-C, exiting: %s', err)
    exit_code = 1
  else:
    exit_code = 0

  sys.exit(exit_code)


if __name__ == '__main__':
  flags.adopt_module_key_flags(auth)
  flags.adopt_module_key_flags(common)
  app.run(main)
