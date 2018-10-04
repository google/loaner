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

"""Module to enforce authentication on endpoints.method.

Each user of the API methods has one or more roles, and these roles grant
specific permissions. For API methods with a permission specified, this
auth.method decorator checks that a user has at least one role
with that permission. For methods with no permission specified, it simply checks
that the user is logged in and a member of the domain. Users that are
superadmins have all permissions by default.

Usage:
-----

The following method will execute if the current user is authenticated properly.

@auth.method(
    chrome_message.ChromeRequest,
    chrome_message.ChromeResponse,
    name='heartbeat',
    path='heartbeat',
    http_method='GET')
def do_something(self, request):
    ...

The following method will execute if the current user has a role with the
permission "view."

 # configuration of an endpoints method with enforced permission.
@loaner_endpoints.authed_method(
    chrome_message.ChromeRequest,
    chrome_message.ChromeResponse,
    name='heartbeat',
    path='heartbeat',
    http_method='GET',
    permission='view')
def do_something(self, request):
    ...
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import functools

from absl import logging

import endpoints

from loaner.web_app import constants
from loaner.web_app.backend.lib import user as user_lib
from loaner.web_app.backend.models import user_model

_FORBIDDEN_MSG = (
    'Permission check failed. Please make sure you are logged in and have the '
    'correct permission to perform this action.')


def method(*args, **kwargs):
  """Configures an endpoint method and enforces permissions."""

  def auth_method_decorator(auth_function):
    """Decorator for auth_method."""
    permission = kwargs.pop('permission', None)

    auth_function = _check_auth(permission)(auth_function)
    return endpoints.method(*args, **kwargs)(auth_function)

  return auth_method_decorator


def _check_auth(permission):
  """Auth check for method calls."""

  def auth_check_decorator(function_without_auth_check):
    """Decorator that adds an auth check to method calls."""

    @functools.wraps(function_without_auth_check)
    def wrapper(*args, **kwargs):
      """Wrapper for auth check decorator."""
      if constants.ON_LOCAL:
        logging.info(
            'Application is running locally. Skipping all auth checks.')
        return function_without_auth_check(*args, **kwargs)

      # Get logged in user.
      try:
        user_email = user_lib.get_user_email()
      except user_lib.UserNotFound as err:
        raise endpoints.UnauthorizedException(str(err))
      # Only allow domain users.
      _forbid_non_domain_users(user_email)

      # If there are no specified permissions, continue with the function.
      if not permission:
        return function_without_auth_check(*args, **kwargs)

      # If there are permissions get the datastore user and compare permissions.
      datastore_user = user_model.User.get_user(user_email)
      if datastore_user.superadmin or (
          permission in datastore_user.get_permissions()):
        return function_without_auth_check(*args, **kwargs)

      # Logged in user does not have correct permissions.
      raise endpoints.ForbiddenException(_FORBIDDEN_MSG)

    return wrapper

  return auth_check_decorator


def _forbid_non_domain_users(user_email):
  """Checks to make sure that the user is a domain user.

  Args:
    user_email: str, the user email.

  Raises:
    UnauthorizedException: An error will occur when user is not from app domain.
  """
  if user_email.split('@')[1] not in constants.APP_DOMAINS:
    raise endpoints.UnauthorizedException(
        '{} is not an authorized user for one of the domains: {}'.format(
            user_email, ', '.join(constants.APP_DOMAINS)))
