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

"""This library provides access to the Google Cloud Datastore API."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from absl import logging

from google.cloud import datastore

from loaner.deployments.lib import auth


class NotFoundError(Exception):
  """Raised when a resource is not found."""


class DatastoreAPI(object):
  """Google Cloud Datastore API access."""

  SCOPES = ('https://www.googleapis.com/auth/datastore',)

  def __init__(self, config, client):
    """Initializes the Google Cloud Datastore API.

    This object should be initialized using the classmethod 'from_config'.

    Args:
      config: common.ProjectConfig, the project configuration.
      client: the api client to use when accessing the Google Cloud Datstore
          API.
    """
    logging.debug('Creating a new DatastoreAPI object with config: %s', config)
    self._config = config
    self._client = client

  def __str__(self):
    return '{} for project: {}.'.format(
        self.__class__.__name__, self._config.project)

  @classmethod
  def from_config(cls, config, creds=None):
    """Returns an initialized DatastoreAPI object.

    Args:
      config: common.ProjectConfig, the project configuration.
      creds: auth.CloudCredentials, the credentials to use for client
          authentication.

    Returns:
      An authenticated DatastoreAPI instance.
    """
    if creds is None:
      creds = auth.CloudCredentials(config, cls.SCOPES)
    client = datastore.Client(
        project=config.project, credentials=creds.get_credentials(cls.SCOPES))
    return cls(config, client)

  def get_version(self):
    """Retrieves the version information associated with a given Project ID.

    Returns:
      An integer representing the version of the datastore or None if the value
          does not exist.

    Raises:
      NotFoundError: when unable to find a Google Cloud Datastore version for
          the provided Google Cloud Project ID.
    """
    entity = self._client.get(
        key=self._client.key('Config', 'datastore_version'))
    try:
      return entity['integer_value']
    except KeyError as err:
      raise NotFoundError(
          'failed to retrieve the datastore version for project '
          '{!r}: {}'.format(self._config.project, err))
