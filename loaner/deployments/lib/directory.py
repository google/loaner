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

"""This library provides access to the Google Admin Directory API."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

# Prefer Python 3 and fall back on Python 2.
# pylint:disable=g-statement-before-imports,g-import-not-at-top
try:
  from http import HTTPStatus as http_status
except ImportError:
  import httplib as http_status
# pylint:enable=g-statement-before-imports,g-import-not-at-top

from absl import logging

from googleapiclient import errors

from loaner.deployments.lib import google_api

# Error messages.
_FORBIDDEN_ERROR_MSG = (
    'failed to contact the Google Admin Directory API, please ensure API access'
    ' is enabled. Instructions can be found here: '
    'https://support.google.com/a/answer/60757?hl=en')
_INSERT_ROLE_ERROR_MSG = (
    'failed to create new Google Admin Role with name %r: %s')
_INSERT_USER_ERROR_MSG = 'failed to create new GSuite User with email %r: %s'

# Default privileges for the GSuite Role Account.
_ROLE_PRIVILEGES = [
    {'privilegeName': 'USERS_RETRIEVE', 'serviceId': '00haapch16h1ysv'},
    {'privilegeName': 'MANAGE_DEVICES', 'serviceId': '04f1mdlm0ki64aw'},
    {'privilegeName': 'ORGANIZATION_UNITS_CREATE',
     'serviceId': '00haapch16h1ysv'},
    {'privilegeName': 'GROUPS_RETRIEVE', 'serviceId': '00haapch16h1ysv'},
]

# Default GSuite Admin Role description.
_ROLE_DESCRIPTION = (
    'Grab n Go Admin Role to allow access to the Google Admin Directory API.')

# Default GSuite Admin Role name.
_ROLE_NAME = 'Grab n Go Admin'

# Defaults for the role account to create and use in GSuite.
_DEFAULT_ROLE_FAMILY_NAME = 'Role Account'
_DEFAULT_ROLE_GIVEN_NAME = 'Grab n Go'
_PRIMARY_EMAIL = 'grab-n-go-role@example.com'
_ORG_UNIT = '/'


class AlreadyExistsError(Exception):
  """Raised when a resource already exists."""


class ForbiddenError(Exception):
  """Raised when unable to contact the Google Admin Directory API."""


class InsertionError(Exception):
  """Raised when the creation of a resource fails."""


class NotFoundError(Exception):
  """Raised when a resource is not found."""


class DirectoryAPI(google_api.GoogleAPI):
  """Google Admin Directory API access."""

  SCOPES = (
      'https://www.googleapis.com/auth/admin.directory.rolemanagement',
      'https://www.googleapis.com/auth/admin.directory.user')
  SERVICE = 'admin'
  VERSION = 'directory_v1'

  def insert_role(self, name=_ROLE_NAME, customer_id='my_customer'):
    """Creates and inserts a new GSuite Admin Role.

    Args:
      name: str, the name of the new GSuite Admin Role.
      customer_id: str, the G Suite customer ID to insert the role into.

    Returns:
      A dictionary object representing the new GSuite Admin Role.
          https://developers.google.com/admin-sdk/directory/v1/reference/roles

    Raises:
      AlreadyExistsError: when the role with the provided name already exists.
      ForbiddenError: when authorization fails.
      InsertionError: when creation fails (e.g. failed to authenticate, improper
          scopes, etc).
    """
    try:
      return self._client.roles().insert(
          customer=customer_id,
          body={
              'roleName': name,
              'rolePrivileges': _ROLE_PRIVILEGES,
              'roleDescription': _ROLE_DESCRIPTION,
              'isSystemRole': False,
              'isSuperAdminRole': False,
          },
      ).execute()
    except errors.HttpError as err:
      status = err.resp.status

      if (status == http_status.CONFLICT or
          status == http_status.INTERNAL_SERVER_ERROR):
        raise AlreadyExistsError(
            'role with name {!r} already exists'.format(name))

      if status == http_status.FORBIDDEN:
        raise ForbiddenError(_FORBIDDEN_ERROR_MSG)

      logging.error(_INSERT_ROLE_ERROR_MSG, name, err)
      raise InsertionError(_INSERT_ROLE_ERROR_MSG % (name, err))

  def insert_user(
      self, password, family_name=_DEFAULT_ROLE_FAMILY_NAME,
      given_name=_DEFAULT_ROLE_GIVEN_NAME, primary_email=_PRIMARY_EMAIL,
      org_unit=_ORG_UNIT):
    """Creates and inserts a new Google Admin User.

    Args:
      password: str, the password to associate with the new GSuite user.
      family_name: str, the family name of the GSuite user to insert.
      given_name: str, the given name of the GSuite user to insert.
      primary_email: str, the email address of the GSuite user to insert.
      org_unit: str, the path to the Organizational Unit where the new GSuite
          user should be inserted.

    Returns:
      A dictionary object representing the new GSuite user.
          https://developers.google.com/admin-sdk/directory/v1/reference/users

    Raises:
      AlreadyExistsError: when the user with the provided email address already
          exists.
      ForbiddenError: when authorization fails.
      InsertionError: when creation fails (e.g. failed to authenticate, improper
          scopes, etc).
    """
    try:
      return self._client.users().insert(
          body={
              'name': {
                  'familyName': family_name,
                  'givenName': given_name,
              },
              'primaryEmail': primary_email,
              'password': password,
              'orgUnitPath': org_unit,
              'changePasswordAtNextLogin': False,
          },
      ).execute()
    except errors.HttpError as err:
      status = err.resp.status

      if (status == http_status.CONFLICT or
          status == http_status.INTERNAL_SERVER_ERROR):
        raise AlreadyExistsError(
            'user with email address {!r} already exists'.format(primary_email))

      if status == http_status.FORBIDDEN:
        raise ForbiddenError(_FORBIDDEN_ERROR_MSG)

      logging.error(_INSERT_USER_ERROR_MSG, primary_email, err)
      raise InsertionError(_INSERT_USER_ERROR_MSG % (primary_email, err))
