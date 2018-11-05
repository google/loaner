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
from loaner.deployments.lib import storage
from loaner.deployments.lib import utils

FLAGS = flags.FLAGS

# API Client modules from which OAuth2 scopes should be extracted.
_API_CLIENT_MODULES = (
    app_engine,
    datastore,
    directory,
    storage,
)

_CHANGE_PROJECT = 'change project'
_CONFIGURE = 'configure'
_QUIT = 'quit'

# Main menu options with help descriptions.
_OPTIONS = collections.OrderedDict([
    (_CHANGE_PROJECT, 'Change the Cloud Project currently being managed'),
    (_CONFIGURE, 'Configure project level constants'),
    (_QUIT, 'Quit the Grab n Go Management script'),
])


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
      self, config, constants, creds, gae_admin_api=None, datastore_api=None,
      directory_api=None, storage_api=None,
  ):
    """Initializes manager attributes.

    Args:
      config: common.Config, the config for this project.
      constants: List[app_constants.Constant], a list of project level
          constants.
      creds: auth.CloudCredentials, the credentials to use when making Google
          API calls.
      gae_admin_api: app_engine.AdminAPI, the App Engine Admin API client.
      datastore_api: datastore.DatastoreAPI, the Google Datastore API client.
      directory_api: directory.DirectoryAPI, the Google Directory API client.
      storage_api: storage.CloudStorageAPI, the Google Cloud Storage API client.
    """
    self._config = config
    self._constants = constants
    self._cloud_creds = creds
    self._gae_admin_api = gae_admin_api
    self._datastore_api = datastore_api
    self._directory_api = directory_api
    self._storage_api = storage_api

  def __str__(self):
    return '{} for project {!r}'.format(
        self.__class__.__name__, self._config.project)

  def __repr__(self):
    return '<{0}.new({1}, {2})>'.format(
        self.__class__.__name__, self._config.path, self._config.key)

  @classmethod
  def new(cls, config_file_path, project_key=None):
    """Creates a new instance of a Grab n Go Manager.

    Args:
      config_file_path: str, the name or path to the config file.
      project_key: Optional[str], the project friendly name, used as the
          top-level key in the config file.

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
      return cls.new(config_file_path, project_key)

    gae_admin_api = app_engine.AdminAPI.from_config(config, cloud_creds)
    datastore_api = datastore.DatastoreAPI.from_config(config, cloud_creds)
    directory_api = directory.DirectoryAPI.from_config(config, cloud_creds)
    storage_api = storage.CloudStorageAPI.from_config(config, cloud_creds)

    constants = app_constants.get_constants_from_flags()

    return cls(
        config, constants, cloud_creds, gae_admin_api, datastore_api,
        directory_api, storage_api)

  def run(self):
    """Runs the Grab n Go manager.

    Returns:
      An integer representing the exit code. Zero is success and any other
          number is a failure.
    """
    exit_code = 0
    try:
      while True:
        utils.clear_screen()
        utils.write('Which of the following actions would you like to take?\n')
        for opt, desc in six.iteritems(_OPTIONS):
          utils.write('Action: {!r}\nDescription: {!r}'.format(opt, desc))
        action = utils.prompt_enum(
            '', accepted_values=_OPTIONS.keys(),
            case_sensitive=False).strip().lower()
        if action == _QUIT:
          break
        elif action == _CHANGE_PROJECT:
          self = self._change_project()
        elif action == _CONFIGURE:
          self._configure()
    finally:
      utils.write(
          'Done managing Grab n Go for Cloud Project {!r}.'.format(
              self._config.project))
    return exit_code

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
    return _Manager.new(self._config.path, project_key)

  def _configure(self):
    """Prompts the user for project wide constants."""
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


def main(argv):
  del argv  # Unused.
  utils.clear_screen()
  utils.write('Welcome to the Grab n Go management script!\n')

  try:
    manager = _Manager.new(FLAGS.config_file_path, FLAGS.project)
    exit_code = manager.run()
  except KeyboardInterrupt as err:
    logging.error('Manager received CTRL-C, exiting: %s', err)
    exit_code = 1

  sys.exit(exit_code)


if __name__ == '__main__':
  flags.adopt_module_key_flags(auth)
  flags.adopt_module_key_flags(common)
  app.run(main)
