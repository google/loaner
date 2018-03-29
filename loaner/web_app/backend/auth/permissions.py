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

"""Define permission for the Grab n Go Application.

There are 4 main roles that are defined (Technical Admin, Operational Admin,
Technician, and User). Each role has a predefined set of permissions. These
permissions are defined below using a namedTuple. We will be using the
check_auth decorator below to check to see if a user has permission to execute
methods.

Usage:
-----
 # only check to see if the user is authenticated
@permissions.check_auth(user_auth_only==True)
def do_something():
    print 'hello'

The above method will execute if the current user is authenticated properly.

@permission.check_auth(permission='view')
def do_something():
    print 'hello'

The above method will only execute if the current user's role has the permission
"view". If the user's role does not, the method will never print hello.

Note:
-----
The decorator should be applied with a permission when a method requires
a permission to be executed.
"""

import collections
import functools
import logging

import enum

import endpoints

from loaner.web_app import constants
from loaner.web_app.backend.lib import user as user_lib
from loaner.web_app.backend.models import user_model

_FORBIDDEN_MSG = (
    'Permission check failed. Please make sure you are logged in and have the '
    'correct permission to perform this action.')
_ROLE = collections.namedtuple('Role', 'name permissions')


@enum.unique
class Permissions(str, enum.Enum):
  """Permission enums for all API method calls."""
  AUDIT_SHELF = 'audit_shelf'
  BOOTSTRAP = 'bootstrap'
  CREATE_SURVEY = 'create_survey'
  DATASTORE_IMPORT = 'datastore_import'
  DEVICE_AUDIT = 'device_audit'
  DISABLE_SHELF = 'disable_shelf'
  EDIT_SHELF = 'edit_shelf'
  ENABLE_SHELF = 'enable_shelf'
  ENROLL_DEVICE = 'enroll_device'
  ENROLL_SHELF = 'enroll_shelf'
  GET_CONFIG = 'get_config'
  GET_DEVICE = 'get_device'
  GET_SHELF = 'get_shelf'
  GET_USER = 'get_user'
  LIST_CONFIG = 'list_configs'
  LIST_DEVICES = 'list_devices'
  LIST_SHELF = 'list_shelves'
  LIST_SURVEYS = 'list_surveys'
  LIST_USER_DEVICES = 'list_user_devices'
  LIST_USERBYROLE = 'list_user'
  PATCH_SURVEY = 'patch_survey'
  RESPONSIBLE_FOR_AUDIT = 'responsible_for_audit'
  UNENROLL_DEVICE = 'unenroll_device'
  UPDATE_CONFIG = 'update_config'
  UPDATE_SHELF = 'update_shelf'
  UPDATE_USER = 'update_user'


TECHNICAL_ADMIN_ROLE = _ROLE(
    name='technical-admin',
    permissions=[
        Permissions.AUDIT_SHELF,
        Permissions.BOOTSTRAP,
        Permissions.CREATE_SURVEY,
        Permissions.DATASTORE_IMPORT,
        Permissions.DEVICE_AUDIT,
        Permissions.DISABLE_SHELF,
        Permissions.EDIT_SHELF,
        Permissions.ENABLE_SHELF,
        Permissions.ENROLL_DEVICE,
        Permissions.ENROLL_SHELF,
        Permissions.GET_CONFIG,
        Permissions.GET_DEVICE,
        Permissions.GET_SHELF,
        Permissions.GET_USER,
        Permissions.LIST_CONFIG,
        Permissions.LIST_DEVICES,
        Permissions.LIST_SHELF,
        Permissions.LIST_SURVEYS,
        Permissions.LIST_USER_DEVICES,
        Permissions.LIST_USERBYROLE,
        Permissions.PATCH_SURVEY,
        Permissions.RESPONSIBLE_FOR_AUDIT,
        Permissions.UNENROLL_DEVICE,
        Permissions.UPDATE_CONFIG,
        Permissions.UPDATE_SHELF,
        Permissions.UPDATE_USER
    ])
OPERATIONAL_ADMIN_ROLE = _ROLE(
    name='operational-admin',
    permissions=[
        Permissions.ENROLL_DEVICE,
        Permissions.GET_CONFIG,
        Permissions.GET_DEVICE,
        Permissions.GET_SHELF,
        Permissions.GET_USER,
        Permissions.LIST_CONFIG,
        Permissions.LIST_DEVICES,
        Permissions.LIST_SHELF,
        Permissions.LIST_USER_DEVICES,
        Permissions.LIST_USERBYROLE,
        Permissions.RESPONSIBLE_FOR_AUDIT,
        Permissions.UNENROLL_DEVICE,
    ])
TECHNICIAN_ROLE = _ROLE(
    name='technician',
    permissions=[
        Permissions.AUDIT_SHELF,
        Permissions.DEVICE_AUDIT,
        Permissions.ENROLL_DEVICE,
        Permissions.GET_CONFIG,
        Permissions.GET_DEVICE,
        Permissions.GET_SHELF,
        Permissions.GET_USER,
        Permissions.LIST_CONFIG,
        Permissions.LIST_DEVICES,
        Permissions.LIST_SHELF,
        Permissions.LIST_USER_DEVICES,
        Permissions.RESPONSIBLE_FOR_AUDIT,
        Permissions.UNENROLL_DEVICE
    ])
USER_ROLE = _ROLE(
    name='user', permissions=[
        Permissions.GET_DEVICE, Permissions.LIST_USER_DEVICES])


def check_auth(permission=None, user_auth_only=None):
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
        raise endpoints.NotFoundException(str(err))
      if user_email:
        _forbid_non_domain_users(user_email)
        if permission is None and user_auth_only is True:
          return function_without_auth_check(*args, **kwargs)
        elif permission is not None:
          datastore_user = user_model.User.get_user(user_email)
          if _check_permission(datastore_user, permission):
            return function_without_auth_check(*args, **kwargs)
      logging.info(_FORBIDDEN_MSG)
      raise endpoints.ForbiddenException(_FORBIDDEN_MSG)

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


def _check_permission(user, permission):
  """Check to see if user has the given permission.

  Args:
    user: user_model.User object
    permission: str, name of the permission to check

  Returns:
    True if the given permission is in the user's role.
  """
  roles = user.roles
  for role in roles:
    if role == 'technical-admin':
      if permission in TECHNICAL_ADMIN_ROLE.permissions:
        return True
    elif role == 'operational-admin':
      if permission in OPERATIONAL_ADMIN_ROLE.permissions:
        return True
    elif role == 'technician':
      if permission in TECHNICIAN_ROLE.permissions:
        return True
    elif role == 'user':
      if permission in USER_ROLE.permissions:
        return True
