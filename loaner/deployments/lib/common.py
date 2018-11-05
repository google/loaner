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

"""Contains common configuration information for Grab n Go Projects."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import tempfile

from absl import flags
from absl import logging

import yaml

from loaner.deployments.lib import utils

DEFAULT = 'default'
REQUIRED_FIELDS = ('project_id', 'client_id', 'client_secret')

FLAGS = flags.FLAGS

flags.DEFINE_string(
    'config_file_path', 'config.yaml',
    'The path to the config file (Optionally the full path to the file).\n'
    'If just the file name is specified we assume the file is located in the '
    'default (loaner/deployments) directory and will look for the file there.')
flags.DEFINE_string(
    'project', None,
    'The friendly name for the Google Cloud Project to deploy to.')


class ConfigError(Exception):
  """Raised when there is an error with the user configuration."""


def _get_config_file_path(config_file_path):
  """Gets the config file path if a full path was not provided.

  Args:
    config_file_path: str, the name or the full path of the config file.

  Returns:
    A str representing the full path to the config file.
  """
  if os.path.isabs(config_file_path):
    return config_file_path
  logging.debug(
      'The full path for the config file was not specified, '
      'looking in the default directory.')
  return os.path.join(
      os.path.dirname(os.path.abspath(__file__)), '..', config_file_path)


@flags.validator('config_file_path')
def _config_file_validator(config_file_path):
  """Validate the config yaml file path.

  Args:
    config_file_path: str, the name or the full path of the config file.

  Returns:
    True when the config_file_path is considered valid.

  Raises:
    flags.ValidationError: if the config file does not end in yaml or is not
        found on the path.
  """
  if not config_file_path.endswith('.yaml'):
    raise flags.ValidationError('the config file must end in .yaml')
  config_file_path = _get_config_file_path(config_file_path)
  if not os.path.isfile(config_file_path):
    raise flags.ValidationError('the config file specified is not found')
  return True


def get_available_configs(config_file_path):
  """Retrieves all of the exiting configurations.

  Args:
    config_file_path: str, the name or the full path of the config file.

  Returns:
    A list of available config keys.
  """
  with open(_get_config_file_path(config_file_path)) as config_file:
    configs = yaml.safe_load(config_file)
  return sorted(configs.keys())


class ProjectConfig(object):
  """Google Cloud Project Configuration.

  Attributes:
    key: str, the top-level key in the config file for this project.
    project: str, the Google Cloud Project Id.
    client_id: str, the OAuth2 Client Id for deployment.
    client_secret: str, the OAuth2 Client Secret for deployment.
    bucket: str, the name of the Google Cloud Storage Bucket used to store both
        long and short term data.
    configs: str, the path to where the secure configurations are stored in
        Google Cloud Storage.
    local_credentials_file_path: str, the path to the locally stored
        credentials file.
    path: str, the absolute path including the name of the config file used to
        load and store this configuration.
  """

  def __init__(self, key, project, client_id, client_secret, bucket, path):
    """Constructor.

    Typically this will not be called directly, instead use the classmethod
    factories.

    Args:
      key: str, the top-level key in the config file for this project.
      project: str, the Google Cloud Project Id.
      client_id: str, the OAuth2 Client Id for deployment.
      client_secret: str, the OAuth2 Client Secret for deployment.
      bucket: str, a custom bucket name used for storing configuration data,
          if no custom name is provided we will attempt to create a default
          bucket.
      path: str, the absolute path including the name of the config file used to
          load and store this configuration.
    """
    self._key = key
    self._project = project
    self._client_id = client_id
    self._client_secret = client_secret
    self._bucket = bucket
    self._path = path

  def __str__(self):
    return '{} for project {!r}.'.format(self.__class__.__name__, self.project)

  def __repr__(self):
    return '<{0}({1}, {2}, {3}, {4}, {5}, {6})>'.format(
        self.__class__.__name__, self.key, self.project, self.client_id,
        self.client_secret, self.bucket, self.path)

  def __eq__(self, other):
    return self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not self.__eq__(other)

  @property
  def key(self):
    """Getter for the top-level config key."""
    return self._key

  @property
  def project(self):
    """Getter for the Google Cloud Project ID."""
    return self._project

  @property
  def client_id(self):
    """Getter for the OAuth2 Client ID."""
    return self._client_id

  @property
  def client_secret(self):
    """Getter for the OAuth2 Client Secret."""
    return self._client_secret

  @property
  def bucket(self):
    """Getter for Google Cloud Storage bucket name."""
    if self._bucket:
      return self._bucket
    return '{}.appspot.com'.format(self._project)

  @property
  def constants_storage_path(self):
    """Getter for Google Cloud Storage configuration path."""
    return 'configs/constants.json'

  @property
  def local_credentials_file_path(self):
    """Getter for the local credentials file."""
    return os.path.join(
        tempfile.gettempdir(), 'gng_auth_{}.dat'.format(self.project))

  @property
  def path(self):
    """Getter for the local configuration file."""
    return self._path

  @classmethod
  def from_yaml(cls, key, config_file_path):
    """Load project config data from the config yaml file.

    Args:
      key: str, the top-level key in the config file for this project.
      config_file_path: str, the name or path to the config file.

    Returns:
      An instance of ProjectConfig with the project specific configurations.

    Raises:
      ConfigError: when the configuration is missing required values.
    """
    logging.debug('Loading the configuration from the provided config file.')
    path = _get_config_file_path(config_file_path)
    with open(path) as config_file:
      config = yaml.safe_load(config_file)[key]
    for field in REQUIRED_FIELDS:
      if config[field] is None:
        raise ConfigError(
            'the field {field!r} is required and is not configured, please '
            'ensure there is a value set for all of the following fields '
            '{fields}'.format(field=field, fields=REQUIRED_FIELDS))
    return cls(
        key=key,
        project=config['project_id'],
        client_id=config['client_id'],
        client_secret=config['client_secret'],
        bucket=config['bucket'],
        path=path,
    )

  @classmethod
  def from_prompts(cls, key, config_file_path):
    """Creates new project config data from prompts.

    Args:
      key: str, the top-level key in the config file for this project.
      config_file_path: str, the name or path to the config file.

    Returns:
      An instance of ProjectConfig with the project specific configurations.
    """
    project = utils.prompt_string(
        'Which Google Cloud Project ID would you like to use to host this '
        "deployment of Grab n Go? You can find the Google Cloud Project ID's "
        'at https://console.cloud.google.com/cloud-resource-manager. If you '
        'do not have an existing project to use, you can create a new one at '
        'https://console.cloud.google.com/projectcreate. For further '
        'instructions on how to create a new Google Cloud project please visit:'
        ' https://cloud.google.com/resource-manager/docs/creating-managing-'
        'projects.\nPlease ensure Billing has been enabled as it is required '
        'for this application (instructions can be found here: '
        'https://cloud.google.com/billing/docs/how-to/modify-project).')
    client_id = utils.prompt_string(
        'An OAuth2 Token is required to authenticate to the Google services '
        'required to manage this application. To do this we first need to '
        'configure the OAuth Consent Screen at: '
        'https://console.cloud.google.com/apis/credentials/consent?'
        'project={0}\nOnce the OAuth Consent Screen is configured please '
        'create a new OAuth2 Client ID and secret at '
        'https://console.cloud.google.com/apis/credentials/oauthclient?'
        "project={0}\nThe 'Application Type' should be 'Other'.\n"
        'Once you have successfully created a new Client ID and secret, '
        'both will be provided to you. For further instructions please visit: '
        'https://support.google.com/cloud/answer/6158849?hl=en.\n'
        'Please provide the Client ID:'.format(project))
    client_secret = utils.prompt_string('Please provide the Client Secret:')
    return cls(
        key, project, client_id, client_secret, None,
        _get_config_file_path(config_file_path))

  def write(self):
    """Writes the project config for the provided key to disk."""
    with open(self.path) as config_file:
      configs = yaml.safe_load(config_file)

    config = configs.get(self.key) or {}
    config['project_id'] = self.project
    config['client_id'] = self.client_id
    config['client_secret'] = self.client_secret
    config['bucket'] = self.bucket
    configs[self.key] = config

    with open(self.path, 'w') as config_file:
      yaml.dump(configs, config_file, default_flow_style=False)
