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

"""Tests for backend.auth.permissions."""

import mock

from google.appengine.api import users
import endpoints

from loaner.web_app import constants
from loaner.web_app.backend.auth import permissions
from loaner.web_app.backend.models import user_model
from loaner.web_app.backend.testing import loanertest


class Error(Exception):
  """Default error class for this test."""


class AuthCheckError(Error):
  """Raised when fake_function_auth_check function executes."""


@permissions.check_auth()
def fake_function_auth_check():
  raise AuthCheckError('check_auth() failed! It should never be able to raise '
                       'this exception!')


@permissions.check_auth()
def fake_function_local():
  return True


class PermissionsTest(loanertest.EndpointsTestCase):

  def setUp(self):
    super(PermissionsTest, self).setUp()

    self.technical_admin_in_datastore = user_model.User(
        id=loanertest.TECHNICAL_ADMIN_EMAIL,
        roles=[permissions.TECHNICAL_ADMIN_ROLE.name])

    self.operational_admin_in_datastore = user_model.User(
        id=loanertest.OPERATIONAL_ADMIN_EMAIL,
        roles=[permissions.OPERATIONAL_ADMIN_ROLE.name])

    self.technician_in_datastore = user_model.User(
        id=loanertest.TECHNICIAN_EMAIL,
        roles=[permissions.TECHNICIAN_ROLE.name])

    self.user_in_datastore = user_model.User(
        id=loanertest.USER_EMAIL,
        roles=[permissions.USER_ROLE.name])

    self.user_no_permission_in_datastore = user_model.User(
        id=loanertest.USER_EMAIL)

    self.technical_admin_in_datastore.put()
    self.operational_admin_in_datastore.put()
    self.technician_in_datastore.put()
    self.user_in_datastore.put()

  def call_test_as(self, email):
    user = None
    if email:
      user = users.User(email)
    with mock.patch.object(endpoints, 'get_current_user', return_value=user):
      with self.assertRaises(endpoints.ForbiddenException):
        fake_function_auth_check()

  def test_check_auth_not_on_gae(self):
    # When ON_LOCAL is True.
    with mock.patch('__main__.permissions.logging.info') as mock_log:
      permissions.constants.ON_LOCAL = True
      self.assertTrue(fake_function_local())
      mock_log.assert_called_once_with(
          'Application is running locally. Skipping all auth checks.')

  def test_check_user(self):
    # No user logged in.
    permissions.constants.ON_LOCAL = False
    user = None
    self.assertIsNone(self.call_test_as(user))

    with mock.patch('__main__.permissions.logging.info') as mock_info:
      user = self.user_no_permission_in_datastore
      self.call_test_as(user.key.id())
      mock_info.assert_called_once_with(
          permissions._FORBIDDEN_MSG)

  def test_forbid_non_domain_users(self):
    permissions.constants.ON_LOCAL = False
    # Non-domain user.
    email = 'user@fakedomain.com'
    with self.assertRaises(endpoints.UnauthorizedException):
      self.call_test_as(email)

    # Domain user.
    email = 'user@' + constants.APP_DOMAIN
    try:
      self.call_test_as(email)
    except endpoints.UnauthorizedException:
      self.fail('call_test_as() failed with UnauthorizedException')

  def test_check_technical_admin_permission(self):
    permissions.constants.ON_LOCAL = False
    # Has valid permission.
    self.assertTrue(
        permissions._check_permission(
            self.technical_admin_in_datastore,
            permissions.Permissions.BOOTSTRAP))

    # Does not have valid permission.
    permission = 'not_valid'
    self.assertFalse(
        permissions._check_permission(
            self.technical_admin_in_datastore, permission))

  def test_check_operational_admin_permission(self):
    permissions.constants.ON_LOCAL = False
    # Has valid permission.
    self.assertTrue(
        permissions._check_permission(
            self.operational_admin_in_datastore,
            permissions.Permissions.ENROLL_DEVICE))

    # Does not have valid permission.
    permission = 'not_valid'
    self.assertFalse(
        permissions._check_permission(
            self.operational_admin_in_datastore, permission))

  def test_check_technician_permission(self):
    permissions.constants.ON_LOCAL = False
    # Has valid permission.
    self.assertTrue(
        permissions._check_permission(
            self.technician_in_datastore,
            permissions.Permissions.ENROLL_DEVICE))

    # Does not have valid permission.
    permission = 'not_valid'
    self.assertFalse(
        permissions._check_permission(self.technician_in_datastore, permission))

  def test_check_user_permission(self):
    permissions.constants.ON_LOCAL = False
    # Has valid permission.
    self.assertTrue(
        permissions._check_permission(
            self.user_in_datastore,
            permissions.Permissions.GET_DEVICE))

    # Does not have valid permission.
    permission = 'not_valid'
    self.assertFalse(
        permissions._check_permission(self.user_in_datastore, permission))


if __name__ == '__main__':
  loanertest.main()
