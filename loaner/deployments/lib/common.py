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

FLAGS = flags.FLAGS

flags.DEFINE_string(
    'config_file_path', 'config.yaml',
    'The path to the config file (Optionally the full path to the file).\n'
    'If just the file name is specified we assume the file is located in the '
    'default (loaner/deployments) directory and will look for the file there.')
flags.DEFINE_enum(
    'project', None, ('prod', 'qa', 'dev', 'local'),
    'The friendly name for the Google Cloud Project to deploy to.')

_REQUIRED_FIELDS = ('project_id', 'client_id', 'client_secret')


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
    raise flags.ValidationError('The config file must end in .yaml')
  config_file_path = _get_config_file_path(config_file_path)
  if not os.path.isfile(config_file_path):
    raise flags.ValidationError('The config file specified is not found.')
  return True


class ProjectConfig(object):
  """Google Cloud Project Configuration.

  Attributes:
    project: str, the Google Cloud Project Id.
    client_id: str, the OAuth2 Client Id for deployment.
    client_secret: str, the OAuth2 Client Secret for deployment.
    bucket: str, the name of the Google Cloud Storage Bucket used to store both
        long and short term data.
    configs: str, the path to where the secure configurations are stored in
        Google Cloud Storage.
    local_credentials_file_path: str, the path to the locally stored
        credentials file.
  """

  def __init__(self, project, client_id, client_secret, bucket):
    """Constructor.

    Typically this will not be called directly, instead use the classmethod
    factories.

    Args:
      project: str, the Google Cloud Project Id.
      client_id: str, the OAuth2 Client Id for deployment.
      client_secret: str, the OAuth2 Client Secret for deployment.
      bucket: str, a custom bucket name used for storing configuration data,
          if no custom name is provided we will attempt to create a default
          bucket.
    """
    self._project = project
    self._client_id = client_id
    self._client_secret = client_secret
    self._bucket = bucket

  def __str__(self):
    return '{} for project: {}.'.format(self.__class__.__name__, self.project)

  def __repr__(self):
    return '<{0}({1}, {2}, {3}, {4})>'.format(
        self.__class__.__name__, self.project, self.client_id,
        self.client_secret, self.bucket)

  def __eq__(self, other):
    return self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not self.__eq__(other)

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
    return '{}-gng-loaner'.format(self._project)

  @property
  def configs(self):
    """Getter for Google Cloud Storage configuration path."""
    return '{}/configs'.format(self.bucket)

  @property
  def local_credentials_file_path(self):
    """Getter for the local credentials file."""
    return os.path.join(
        tempfile.gettempdir(), 'gng_auth_{}.dat'.format(self.project))

  @classmethod
  def from_yaml(cls, project, config_file_path):
    """Load project config data from the config yaml file.

    Args:
      project: str, the project friendly name, used as the top-level key in the
          config file.
      config_file_path: str, the path to the config file.

    Returns:
      An instance of ProjectConfig with the project specific configurations.

    Raises:
      ConfigError: when the configuration is missing required values.
    """
    logging.debug('Loading the configuration from the provided config file.')
    with open(_get_config_file_path(config_file_path), 'r') as config_file:
      config = yaml.safe_load(config_file)[project]
    for key in _REQUIRED_FIELDS:
      if config[key] is None:
        raise ConfigError(
            'The field ({key}) is required and is not configured, please ensure'
            ' there is a value set for all of the following fields '
            '{fields}.'.format(key=key, fields=_REQUIRED_FIELDS))
    return cls(
        project=config['project_id'],
        client_id=config['client_id'],
        client_secret=config['client_secret'],
        bucket=config['custom_bucket'],
    )
