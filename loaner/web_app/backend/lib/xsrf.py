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

"""Module for handling tokens to prevent malicious XSRF."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import datetime
import logging
import threading
import uuid

from oauth2client.contrib import xsrfutil
from protorpc import remote
import webapp2
from google.appengine.ext import ndb

from loaner.web_app import constants
from loaner.web_app.backend.lib import user


class Error(Exception):
  """Default error class for this module."""


class UnsupportedRequestError(Error):
  """Raised when an unsupported request is passed."""


class _XsrfSecretKey(ndb.Model):
  """Store secret key in datastore."""
  secret = ndb.StringProperty(required=True)


_xsrf_secret = None
_xsrf_secret_lock = threading.Lock()


def _get_xsrf_secret():
  """Creates a secret if it is not set.

    The global _xsrf_secret contains the cached xsrf key from the datastore. It
    is used to prevent having to go to the datastore every time the key is
    requested by calling _get_xsrf_secret.

  Returns:
    The existing XSRF secret or a new one persisted in the datastore.
  """
  global _xsrf_secret  #  pylint: disable=global-statement
  with _xsrf_secret_lock:  # pylint: disable=not-context-manager
    if not _xsrf_secret:
      _xsrf_secret = str(
          _XsrfSecretKey.get_or_insert(
              'xsrf_secret_key', secret=uuid.uuid4().hex).secret)
  return _xsrf_secret


def _generate_token(time=None):
  """Generate XSRF token.

  Args:
    time: The time in microseconds since the epoch at which the user was
    authorized for this action. Of not set, the current time is used.

  Returns:
    Generated XSRF token string, or an empty string if no user is logged in.
  """
  current_user = user.get_user_email()
  if not current_user:
    return ''
  return xsrfutil.generate_token(
      key=_get_xsrf_secret(),
      user_id=current_user,
      action_id=constants.XSRF_ACTION_ID,
      when=time)


def add_xsrf_token_cookie(response):
  """Adds XSRF token cookie to a response object.

  Args:
    response: The webapp2.Response object.
  """
  expires = (datetime.datetime.utcnow() + datetime.timedelta(
      microseconds=constants.XSRF_TOKEN_TIMEOUT))
  response.set_cookie(
      constants.XSRF_COOKIE_NAME,
      _generate_token(),
      expires=expires,
      overwrite=True)


def validate_request(request, response=None):
  """Makes sure the XSRF token is valid.

  Args:
    request: remote.HttpRequestState or webapp2.Request object.
    response: Optional webapp2.Response object

  Returns:
    True if the token in the request is valid for the user.

  Raises:
    UnsupportedRequestError: When an invalid request is passed.
  """
  if not constants.ON_GAE:
    return True

  current_user = user.get_user_email()
  if not current_user:
    logging.info(
        'Unable to validate XSRF token because there is no user logged in')
    return False
  if not isinstance(request, (remote.HttpRequestState, webapp2.Request)):
    raise UnsupportedRequestError(
        'Request type {} is not supported.'.format(str(type(request))))

  if (hasattr(request, 'service_path') and
      request.service_path.startswith('/_ah/api')):
    return True
  if request.method not in constants.XSRF_EXEMPT_METHODS:
    xsrf_token = (request.headers.get(constants.XSRF_HEADER) or
                  request.params.get(constants.XSRF_PARAM))
    if not xsrf_token:
      logging.warning('XSRF token not found in request')
      return False
    if xsrfutil.validate_token(
        key=_get_xsrf_secret(),
        token=xsrf_token,
        user_id=current_user,
        action_id=constants.XSRF_ACTION_ID):
      return True
    else:
      logging.info('No valid XSRF token.')
      if response:
        response.delete_cookie(constants.XSRF_COOKIE_NAME)
      return False
  return True
