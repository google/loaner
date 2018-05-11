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

"""Tests for backend.api.auth."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import mock

from protorpc import message_types
from google.appengine.api import users
from google.appengine.ext import ndb
import endpoints

from loaner.web_app import constants
from loaner.web_app.backend.api import auth
from loaner.web_app.backend.api import permissions
from loaner.web_app.backend.api import root_api
from loaner.web_app.backend.lib import xsrf
from loaner.web_app.backend.models import user_model
from loaner.web_app.backend.testing import loanertest


@root_api.ROOT_API.api_class(resource_name='fake', path='fake')
class FakeApiPermissionChecks(root_api.Service):

  @auth.method(
      message_types.VoidMessage,
      http_method='POST')
  def api_for_any_authenticated_user(self, request):
    self.check_xsrf_token(self.request_state)
    return message_types.VoidMessage()

  @auth.method(
      message_types.VoidMessage,
      http_method='POST',
      permission=permissions.Permissions.AUDIT_SHELF)
  def api_with_permission(self, request):
    self.check_xsrf_token(self.request_state)
    return message_types.VoidMessage()

  @auth.method(
      message_types.VoidMessage,
      http_method='POST',
      permission=permissions.Permissions.MODIFY_DEVICE)
  def api_for_superadmins_only(self, request):
    self.check_xsrf_token(self.request_state)
    return message_types.VoidMessage()


class LoanerEndpointsTest(loanertest.EndpointsTestCase):

  def setUp(self):
    super(LoanerEndpointsTest, self).setUp()
    self.service = FakeApiPermissionChecks()
    self.request = message_types.VoidMessage()

    user_model.Role.create(
        'technical_admin',
        role_permissions=[permissions.Permissions.AUDIT_SHELF],
        associated_group=loanertest.TECHNICAL_ADMIN_EMAIL)

    user_model.User(
        id=loanertest.SUPER_ADMIN_EMAIL, superadmin=True).put()
    user_model.User(
        id=loanertest.TECHNICAL_ADMIN_EMAIL,
        roles=[ndb.Key(user_model.Role, 'technical_admin')]).put()
    user_model.User(id=loanertest.USER_EMAIL).put()

  def call_test_as(self, api_name, user):
    """Makes a call FakeApiPermissionChecks APIs with different users.

    Args:
      api_name: str, the name of the test API to call.
      user: users.User obj, the App Engine API users object being checked.

    Returns:
      True if permission or user auth passed the call to the API.
    """
    with mock.patch.object(
        xsrf, 'validate_request') as mock_validate_request:
      mock_validate_request.return_value = True
      with mock.patch.object(users, 'get_current_user') as mock_user:
        mock_user.return_value = user
        api_method = getattr(self.service, api_name)
        if api_method(self.request) == message_types.VoidMessage():
          return True

  def test_loaner_endpoints_auth_method__unauthenticated(self):
    # Test no user logged in.
    constants.ON_GAE = True
    user = None
    with self.assertRaises(endpoints.UnauthorizedException):
      self.call_test_as('api_for_any_authenticated_user', user=user)

    with self.assertRaises(endpoints.UnauthorizedException):
      self.call_test_as(
          api_name='api_with_permission', user=user)

    with self.assertRaises(endpoints.UnauthorizedException):
      self.call_test_as(
          api_name='api_for_superadmins_only', user=user)

  def test_loaner_endpoints_auth_method__api_for_any_authenticated_user(self):
    # Test api_with_permission with a user.
    user = users.User(email=loanertest.USER_EMAIL)
    self.assertTrue(self.call_test_as('api_for_any_authenticated_user', user))

    # Test api_for_any_authenticated_user with permission.
    user = users.User(email=loanertest.TECHNICAL_ADMIN_EMAIL)
    self.assertTrue(self.call_test_as('api_for_any_authenticated_user', user))

    # Test api_for_any_authenticated_user with the superadmin.
    user = users.User(email=loanertest.SUPER_ADMIN_EMAIL)
    self.assertTrue(self.call_test_as('api_for_any_authenticated_user', user))

    # Test invalid domain.
    user = users.User(email='userl@fakedomain.com')
    with self.assertRaises(endpoints.UnauthorizedException):
      self.call_test_as('api_for_any_authenticated_user', user)

  def test_loaner_endpoints_auth_method__api_with_permission(self):
    # Forbid standard users.
    user = users.User(email=loanertest.USER_EMAIL)
    with self.assertRaises(endpoints.ForbiddenException):
      self.call_test_as('api_with_permission', user)

    # Test permission for Technical Admin user.
    user = users.User(email=loanertest.TECHNICAL_ADMIN_EMAIL)
    self.assertTrue(self.call_test_as('api_with_permission', user))

    # Test permission for superadmin.
    user = users.User(email=loanertest.SUPER_ADMIN_EMAIL)
    self.assertTrue(self.call_test_as('api_with_permission', user))

  def test_loaner_endpoints_auth_method__api_for_superadmins_only(self):
    # Test wrong permission.
    user = users.User(email=loanertest.TECHNICAL_ADMIN_EMAIL)
    with self.assertRaises(endpoints.ForbiddenException):
      self.call_test_as('api_for_superadmins_only', user)

    # Test superadmin access.
    user = users.User(email=loanertest.SUPER_ADMIN_EMAIL)
    self.call_test_as('api_for_superadmins_only', user)


if __name__ == '__main__':
  loanertest.main()
