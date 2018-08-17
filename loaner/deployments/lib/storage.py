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

from loaner.deployments.lib import google_api

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


class CloudStorageAPI(google_api.GoogleAPI):
  """Google Cloud Storage API access."""

  SCOPES = ('https://www.googleapis.com/auth/devstorage.read_write',)
  SERVICE = 'storage'
  VERSION = 'v1'

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
