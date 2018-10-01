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

import json

from absl import logging

from google.cloud import exceptions
from google.cloud import storage

from loaner.deployments.lib import auth

# Error messages.
_GET_BUCKET_ERROR_MSG = 'failed to retrieve Google Cloud Storage Bucket %r: %s'
_GET_BLOB_ERROR_MSG = (
    'failed to retrieve Blob with name %r from Google Cloud Storage Bucket '
    '%r: %s')


class AlreadyExistsError(Exception):
  """Raised when a resource already exists."""


class NotFoundError(Exception):
  """Raised when a resource is not found."""


class CloudStorageAPI(object):
  """Google Cloud Storage API access."""

  SCOPES = ('https://www.googleapis.com/auth/devstorage.read_write',)

  def __init__(self, config, client):
    """Initializes the Google Cloud Storage API.

    This object should be initialized using the classmethod 'from_config'.

    Args:
      config: common.ProjectConfig, the project configuration.
      client: the api client to use when accessing the Google Cloud Storage
          API.
    """
    logging.debug(
        'Creating a new CloudStorageAPI object with config: %s', config)
    self._config = config
    self._client = client

  def __str__(self):
    return '{} for project: {}.'.format(
        self.__class__.__name__, self._config.project)

  @classmethod
  def from_config(cls, config, creds=None):
    """Returns an initialized CloudStorageAPI object.

    Args:
      config: common.ProjectConfig, the project configuration.
      creds: auth.CloudCredentials, the credentials to use for client
          authentication.

    Returns:
      An authenticated CloudStorageAPI instance.
    """
    if creds is None:
      creds = auth.CloudCredentials(config, cls.SCOPES)
    client = storage.Client(
        project=config.project, credentials=creds.get_credentials(cls.SCOPES))
    return cls(config, client)

  def get_bucket(self, bucket_name=None):
    """Retrieves a Google Cloud Storage Bucket object.

    Args:
      bucket_name: str, the name of the Google Cloud Storage Bucket to retrieve.

    Returns:
      A dictionary object representing a Google Cloud Storage Bucket.
          type: google.cloud.storage.bucket.Bucket

    Raises:
      NotFoundError: when a resource is not found.
    """
    bucket_name = bucket_name or self._config.bucket
    try:
      return self._client.get_bucket(bucket_name)
    except exceptions.NotFound as err:
      logging.error(_GET_BUCKET_ERROR_MSG, bucket_name, err)
      raise NotFoundError(_GET_BUCKET_ERROR_MSG % (bucket_name, err))

  def insert_bucket(self, bucket_name=None):
    """Inserts a Google Cloud Storage Bucket object.

    Args:
      bucket_name: str, the name of the Google Cloud Storage Bucket to insert.

    Returns:
      A dictionary object representing a Google Cloud Storage Bucket.
          type: google.cloud.storage.bucket.Bucket

    Raises:
      AlreadyExistsError: when trying to insert a bucket that already exists.
    """
    bucket_name = bucket_name or self._config.bucket
    try:
      new_bucket = self._client.create_bucket(bucket_name)
    except exceptions.Conflict as err:
      raise AlreadyExistsError(
          'the Google Cloud Storage Bucket with name {!r} already exists: '
          '{}'.format(bucket_name, err))

    logging.debug(
        'The Googld Cloud Storage Bucket %r has been created for project '
        '%r.', bucket_name, self._config.project)
    return new_bucket

  def insert_blob(self, path, contents, bucket_name=None):
    """Inserts a new json encoded Blob in the Cloud Storage bucket provided.

    NOTE: If a Blob already exists at the provided path it will be overwritten
    by the new contents without warning.

    Args:
      path: str, the path of the Blob to create relative to the root of the
          Google Cloud Storage Bucket including the name of the Blob.
      contents: dict, a dictionary representing the contents of the new Blob.
      bucket_name: str, the name of the Google Cloud Storage Bucket to insert
          the new Blob into.
    """
    bucket_name = bucket_name or self._config.bucket

    blob = storage.Blob(
        name=path,
        bucket=self.get_bucket(bucket_name),
    )

    blob.upload_from_string(
        data=json.dumps(contents),
        content_type='application/json',
        client=self._client,
    )

    logging.info(
        'Successfully uploaded blob %r to bucket %r.', path, bucket_name)

  def get_blob(self, path, bucket_name=None):
    """Retrieves a json encoded Blob from Google Cloud Storage as a dictionary.

    Args:
      path: str, the path of the Blob to retrieve relative to the root of the
          Google Cloud Storage Bucket including the name of the Blob.
      bucket_name: str, the name of the Google Cloud Storage Bucket to retrieve
          the Blob from.

    Returns:
      A dictionary of the Blob from Google Cloud Storage.

    Raises:
      NotFoundError: when the path provided is not associated with a Blob in the
          Google Cloud Storage Bucket.
    """
    bucket_name = bucket_name or self._config.bucket

    blob = self.get_bucket(bucket_name).get_blob(path, self._client)

    try:
      contents = blob.download_as_string(self._client)
    except (AttributeError, exceptions.NotFound) as err:
      logging.error(_GET_BLOB_ERROR_MSG, path, bucket_name, err)
      raise NotFoundError(_GET_BLOB_ERROR_MSG % (path, bucket_name, err))
    return json.loads(contents)
