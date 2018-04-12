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

"""Root API for loaner.example.com implemented using Google Endpoints."""

from protorpc import remote

from google.appengine.api import datastore_errors
from google.appengine.datastore import datastore_query
from google.appengine.ext import ndb

import endpoints

from loaner.web_app import constants
from loaner.web_app.backend.lib import xsrf

__all__ = ['ROOT_API']

_CORRUPT_KEY_MSG = 'The key provided for submission was not found.'
_MALFORMED_PAGE_TOKEN_MSG = 'The page token provided is incorrect.'


class Service(remote.Service):
  """Remote Service subclass."""

  def check_xsrf_token(self, request_state):
    """Examine a request and raise an exception for an invalid XSRF token.

    Args:
      request_state: a protorpc.remote.HttpRequestState object from Endpoints
      API request.

    Raises:
      endpoints.ForbiddenException: if the call to xsrf.validate_request returns
      False.
    """
    if not xsrf.validate_request(request_state):
      raise endpoints.ForbiddenException(
          'Refresh page to obtain a valid XSRF token.')

  def to_dict(self, entity, model_class):
    """Builds a dictionary of filtered properties of an NDB model.

    Args:
      entity: An instance of an NDB Model or a ProtoRPC message.
      model_class: NDB model to use for iterating its properties.

    Returns:
      A dictionary with filter properties.
    """
    dictionary = {}
    for key in model_class._properties:  # pylint: disable=protected-access
      value = getattr(entity, key, None)
      if value is not None and value != []:  # pylint: disable=g-explicit-bool-comparison
        dictionary[key] = value
    return dictionary

  def get_datastore_cursor(self, urlsafe_cursor):
    """Builds a datastore.Cursor from a urlsafe cursor.

    Args:
      urlsafe_cursor: str, The urlsafe representation of a datastore.Cursor.

    Returns:
      datastore.Cursor instance.

    Raises:
      endpoints.BadRequestException: if the creation of the datastore.Cursor
          fails.
    """
    try:
      return datastore_query.Cursor(urlsafe=urlsafe_cursor)
    except datastore_errors.BadValueError:
      raise endpoints.BadRequestException(_MALFORMED_PAGE_TOKEN_MSG)


def get_ndb_key(urlsafe_key):
  """Builds an ndb.Key from a urlsafe key.

  Args:
    urlsafe_key: str, A urlsafe ndb.Key to cast into an ndb.Key.

  Returns:
    An ndb.Key instance.

  Raises:
    endpoints.BadRequestException: if the creation of the ndb.Key fails.
  """
  try:
    return ndb.Key(urlsafe=urlsafe_key)
  except Exception:  # pylint: disable=broad-except
    raise endpoints.BadRequestException(_CORRUPT_KEY_MSG)


ROOT_API = endpoints.api(
    allowed_client_ids=constants.ALLOWED_CLIENT_IDS,
    auth_level=endpoints.AUTH_LEVEL.REQUIRED,
    description='Loaner Root API',
    name='loaner',
    scopes=constants.ROOT_SCOPES,
    title='Loaner API',
    version='v1')

