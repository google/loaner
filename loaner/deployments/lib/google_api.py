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

"""Base class for Google API client libraries."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from absl import logging

from loaner.deployments.lib import auth


class GoogleAPI(object):
  """Google API base class.

  All attributes must be set by subclasses.

  Attributes:
    SCOPES: List[str], a list of the OAuth2 scopes required for the API.
    SERVICE: str, the service name of the API to access.
    VERSION: str, the version of the API to access.
  """
  SCOPES = None
  SERVICE = None
  VERSION = None

  def __init__(self, config, client):
    """Initializes a Google API object.

    This object should be initialized using the classmethod 'from_config'.

    Args:
      config: common.ProjectConfig, the project configuration.
      client: the api client to use when accessing the scoped API.
    """
    logging.debug(
        'Creating a new %r object with config: %r',
        self.__class__.__name__, config)
    self._config = config
    self._client = client

  def __str__(self):
    return '{} for project: "{}"'.format(
        self.__class__.__name__, self._config.project)

  def __repr__(self):
    return '<{}.from_config({!r})>'.format(
        self.__class__.__name__, self._config)

  @classmethod
  def from_config(cls, config, creds=None):
    """Returns an initialized Google API object.

    Args:
      config: common.ProjectConfig, the project configuration.
      creds: auth.CloudCredentials, the credentials to use for client
          authentication.

    Returns:
      An authenticated Google API instance.

    Raises:
      AttributeError: if SCOPES, SERVICE, or VERSION are not set.
    """
    if cls.SCOPES is None:
      raise AttributeError(
          'SCOPES must be set in order to create a new {!r} client'.format(
              cls.__name__))
    if cls.SERVICE is None:
      raise AttributeError(
          'SERVICE must be set in order to create a new {!r} client'.format(
              cls.__name__))
    if cls.VERSION is None:
      raise AttributeError(
          'VESRION must be set in order to create a new {!r} client'.format(
              cls.__name__))
    if creds is None:
      creds = auth.CloudCredentials(config, cls.SCOPES)
    client = creds.get_api_client(cls.SERVICE, cls.VERSION, cls.SCOPES)
    return cls(config, client)
