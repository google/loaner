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

Each user of the API methods has one or more roles, and these roles and their
permissions are defined in api.permissions. For API methods with a permission
specified, this auth.method decorator checks that a user has at least one role
with that permission. For methods with no permission specified, it simply checks
that the user is logged in.

Assignee Methods

All users have the "assignee" role allowing them to borrow devices. If a device
API is meant to allow assignees to use it, its auth.method decorator must
specify allow_assignees=True. The auth.method decorator will keep track of which
roles the user has that allow the API method, and the API method will receive
a roles_permitted kwarg containing a list of these roles. The device API source
code must ensure that if "assignee" is the only item in the list, it verifies
the user is the assignee.

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

The following method will execute if the current user has a role with the
permission "view." But, if they only have permission via the assignee role, the
method must use the roles_permitted list to verify they are the device assignee.

 # configuration of an endpoints method with enforced permission.
@loaner_endpoints.authed_method(
    device_message.DeviceRequest,
    device_message.DeviceResponse,
    name='device_thing',
    path='device_thing',
    http_method='GET',
    permission='view',
    allow_assignees=True)  # Allows assignee, provides API with roles_permitted.
def do_something(self, request, roles_permitted=None):
    ...
    user_email = user.get_user_email()
    if roles_permitted == ['user']:
      _confirm_user_is_the_assignee_action(user_email, device)
    ...
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import functools

from absl import logging

import endpoints

from loaner.web_app import constants
from loaner.web_app.backend.api import permissions
from loaner.web_app.backend.lib import user as user_lib
from loaner.web_app.backend.models import user_model

_FORBIDDEN_MSG = (
    'Permission check failed. Please make sure you are logged in and have the '
    'correct permission to perform this action.')


def method(*args, **kwargs):
  """Configures an endpoint method and enforces permissions."""
  allow_assignee = kwargs.pop('allow_assignee', False)

  def auth_method_decorator(auth_function):
    """Decorator for auth_method."""
    permission = kwargs.pop('permission', None)

    auth_function = _check_auth(permission, allow_assignee)(auth_function)
    return endpoints.method(*args, **kwargs)(auth_function)

  return auth_method_decorator


def _check_auth(permission, allow_assignee):
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

      try:
        user_email = user_lib.get_user_email()
      except user_lib.UserNotFound as err:
        raise endpoints.UnauthorizedException(str(err))
      _forbid_non_domain_users(user_email)

      roles_permitted = []

      if permission is not None:
        datastore_user = user_model.User.get_user(user_email)
        for role in datastore_user.roles:
          if permission in permissions.ROLES[role]:
            roles_permitted.append(role)

      if permission and not roles_permitted:
        raise endpoints.ForbiddenException(_FORBIDDEN_MSG)
      if allow_assignee:
        kwargs['roles_permitted'] = roles_permitted
      else:
        if roles_permitted == ['user']:
          raise endpoints.ForbiddenException(_FORBIDDEN_MSG)

      return function_without_auth_check(*args, **kwargs)

    return wrapper

  return auth_check_decorator


def _forbid_non_domain_users(user_email):
  """Check to make sure that the user is a domain user.

  Args:
    user_email: String, the user email.

  Raises:
    UnauthorizedException: An error will occur when user is not from app domain.
  """
  if user_email.split('@')[1] != constants.APP_DOMAIN:
    raise endpoints.UnauthorizedException(
        '{} is not an authorized user for the {} domain.'.format(
            user_email, constants.APP_DOMAIN))
