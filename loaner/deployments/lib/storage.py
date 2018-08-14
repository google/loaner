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

"""This library provides access to the Google Cloud Storage API."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import httplib

from absl import logging

from googleapiclient import errors

from loaner.deployments.lib import auth

# Google App Engine Admin SDK constants.
_SERVICE_NAME = 'storage'
_VERSION = 'v1'
_SCOPES = ('https://www.googleapis.com/auth/devstorage.read_write',)

# Error messages.
_GET_BUCKET_ERROR_MSG = 'Failed to retrieve Google Cloud Storage Bucket %r: %s.'
_INSERT_BUCKET_ERROR_MSG = (
    'Failed to insert Google Cloud Storage Bucket %r for project %r: %s.')


class AlreadyExistsError(Exception):
  """Raised when a resource already exists."""


class NotFoundError(Exception):
  """Raised when a resource is not found."""


class InsertionError(Exception):
  """Raised when inserting a new resource fails."""


class CloudStorageAPI(object):
  """Google Cloud Storage API access."""

  def __init__(self, config, client):
    """Initializes the Google Cloud Storage API.

    Args:
      config: common.ProjectConfig, the project configuration.
      client: the api client to use when accessing the Google Cloud Storage API.
    """
    logging.debug('Creating a new Cloud Storage object with config: %r', config)
    self._config = config
    self._client = client

  def __str__(self):
    return '{} for project: {}.'.format(
        self.__class__.__name__, self._config.project)

  @classmethod
  def from_config(cls, config):
    """Returns an initialized CloudStorageAPI object.

    Args:
      config: common.ProjectConfig, the project configuration.

    Returns:
      An authenticated CloudStorageAPI instance.
    """
    creds = auth.CloudCredentials(config, _SCOPES)
    client = creds.get_api_client(_SERVICE_NAME, _VERSION, _SCOPES)
    return cls(config, client)

  def get_bucket(self, bucket_name=None):
    """Retrieves a Google Cloud Storage Bucket object.

    Args:
      bucket_name: str, the name of the Google Cloud Storage Bucket to retrieve.

    Returns:
      A dictionary object representing a Google Cloud Storage Bucket.

    Raises:
      NotFoundError: when a resource is not found.
    """
    bucket_name = bucket_name or self._config.bucket
    try:
      return self._client.buckets().get(bucket=bucket_name).execute()
    except errors.HttpError as err:
      logging.error(_GET_BUCKET_ERROR_MSG, self._config.bucket, err)
      raise NotFoundError(_GET_BUCKET_ERROR_MSG % (self._config.bucket, err))

  def insert_bucket(self, bucket_name=None):
    """Inserts a Google Cloud Storage Bucket object.

    Args:
      bucket_name: str, the name of the Google Cloud Storage Bucket to insert.

    Returns:
      A dictionary object representing a Google Cloud Storage Bucket.

    Raises:
      AlreadyExistsError: when trying to insert a bucket that already exists.
      InsertionError: when inserting a bucket fails for an unknown reason.
    """
    bucket_name = bucket_name or self._config.bucket
    try:
      new_bucket = self._client.buckets().insert(
          project=self._config.project,
          body={'name': bucket_name},
      ).execute()
    except errors.HttpError as err:
      if err.resp.status == httplib.CONFLICT:
        raise AlreadyExistsError(
            'The Google Cloud Storage Bucket with name %r already exists.' %
            bucket_name)

      logging.error(
          _INSERT_BUCKET_ERROR_MSG, bucket_name, self._config.project, err)
      raise InsertionError(
          _INSERT_BUCKET_ERROR_MSG % (bucket_name, self._config.project, err))

    logging.info(
        'The Googld Cloud Storage Bucket %r has been created for project '
        '%r.', bucket_name, self._config.project)
    return new_bucket
