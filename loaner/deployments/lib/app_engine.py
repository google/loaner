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

"""This library provides access to the App Engine Admin API."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from absl import logging

from googleapiclient import errors

from loaner.deployments.lib import google_api

# Error messages.
_CREATE_ERROR_MSG = (
    'failed to create Google App Engine project for project %r in '
    'location %r: %s')
_GET_ERROR_MSG = 'failed to get project %r: %s'

# Valid App Engine application locations.
LOCATIONS = frozenset([
    'us-east1',
    'us-east4',
    'us-central',
    'us-west2',
    'northamerica-northeast1',
    'southamerica-east1',
    'europe-west',
    'europe-west2',
    'europe-west3',
    'asia-northeast1',
    'asia-south1',
    'australia-southeast1',
])


class Error(Exception):
  """Base error class for this module. """


class CreationError(Error):
  """Raised when the creation of a resource fails."""


class NotFoundError(Error):
  """Raised when a resource is not found."""


class AdminAPI(google_api.GoogleAPI):
  """App Engine Admin API access."""

  SCOPES = ('https://www.googleapis.com/auth/appengine.admin',)
  SERVICE = 'appengine'
  VERSION = 'v1'

  def create(self, location):
    """Creates a new Google App Engine application in a given location.

    Args:
      location: str, the location in which the Google App Engine application is
          to be hosted.

    Returns:
      A dictionary object representing the newly created Google App Engine
          application (Type: google.appengine.v1.Application).

    Raises:
      CreationError: when creation fails (e.g. failed to authenticate, improper
          scopes, project already exists, etc).
      NotFoundError: if the provided location is not a valid location.
    """
    if location not in LOCATIONS:
      raise NotFoundError(
          'the location provided {!r} was not found in the list of approved '
          'locations {}'.format(location, LOCATIONS))
    try:
      return self._client.apps().create(
          body={
              'id': self._config.project,
              'locationId': location,
          },
      ).execute()
    except errors.HttpError as err:
      logging.error(_CREATE_ERROR_MSG, self._config.project, location, err)
      raise CreationError(
          _CREATE_ERROR_MSG % (self._config.project, location, err))

  def get(self):
    """Retrieves the information associated with a given Project ID.

    Returns:
      A dictionary object representing a deployed Google App Engine application
          (Type: google.appengine.v1.Application).

    Raises:
      NotFoundError: when unable to find a Google App Engine application for the
          provided Google Cloud Project ID.
    """
    try:
      return self._client.apps().get(appsId=self._config.project).execute()
    except errors.HttpError as err:
      logging.error(_GET_ERROR_MSG, self._config.project, err)
      raise NotFoundError(_GET_ERROR_MSG % (self._config.project, err))
