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

import mock

from protorpc import message_types
from google.appengine.api import users
import endpoints

from loaner.web_app import constants
from loaner.web_app.backend.api import auth
from loaner.web_app.backend.api import permissions
from loaner.web_app.backend.api import root_api
from loaner.web_app.backend.lib import user as user_lib  # pylint: disable=unused-import
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
      permission=permissions.Permissions.LIST_USER_DEVICES,
      allow_assignee=True)
  def api_for_assignee_or_admins(self, request, roles_permitted=None):
    self.check_xsrf_token(self.request_state)
    if roles_permitted == ['user']:
      if users.get_current_user() != users.User(email=loanertest.USER_EMAIL):
        print users.get_current_user(), loanertest.USER_EMAIL
        raise endpoints.ForbiddenException('User is not assignee.')
    return message_types.VoidMessage()

  @auth.method(
      message_types.VoidMessage,
      http_method='POST',
      permission=permissions.Permissions.ENROLL_DEVICE)
  def api_for_admins_only(self, request):
    self.check_xsrf_token(self.request_state)
    return message_types.VoidMessage()


class LoanerEndpointsTest(loanertest.EndpointsTestCase):

  def setUp(self):
    super(LoanerEndpointsTest, self).setUp()
    self.service = FakeApiPermissionChecks()
    self.request = message_types.VoidMessage()

    user_model.User(
        id=loanertest.TECHNICAL_ADMIN_EMAIL,
        roles=['technical-admin']).put()
    user_model.User(
        id=loanertest.OPERATIONAL_ADMIN_EMAIL,
        roles=['operational-admin']).put()
    user_model.User(
        id=loanertest.TECHNICIAN_EMAIL,
        roles=['technician']).put()
    user_model.User(
        id=loanertest.USER_EMAIL, roles=['user']).put()
    user_model.User(
        id='someone-else@{}'.format(loanertest.USER_DOMAIN),
        roles=['user']).put()

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

  def test_loaner_endpoints_auth_method(self):
    # Test no user logged in.
    constants.ON_GAE = True
    user = None
    with self.assertRaises(endpoints.NotFoundException):
      self.call_test_as('api_for_any_authenticated_user', user=user)

    with self.assertRaises(endpoints.NotFoundException):
      self.call_test_as(
          api_name='api_for_assignee_or_admins', user=user)

    with self.assertRaises(endpoints.NotFoundException):
      self.call_test_as(
          api_name='api_for_admins_only', user=user)

    # Test api_for_any_authenticated_user with a user.
    user = users.User(email=loanertest.USER_EMAIL)
    self.assertTrue(self.call_test_as('api_for_any_authenticated_user', user))

    # Test api_for_any_authenticated_user with a technical_admin.
    user = users.User(email=loanertest.TECHNICAL_ADMIN_EMAIL)
    self.assertTrue(self.call_test_as('api_for_any_authenticated_user', user))

    # Test api_for_assignee_or_admins with the assignee.
    user = users.User(email=loanertest.USER_EMAIL)
    self.assertTrue(self.call_test_as('api_for_assignee_or_admins', user))

    # Make sure user_auth_only is not executed since permission is set.
    user = users.User(email=loanertest.USER_EMAIL)
    with self.assertRaises(endpoints.ForbiddenException):
      self.call_test_as('api_for_admins_only', user)

    # Test user_auth_only invalid domain.
    user = users.User(email='daredevil@fakedomain.com')
    with self.assertRaises(endpoints.UnauthorizedException):
      self.call_test_as('api_for_admins_only', user)

    # Test permission for Technical Admin user.
    user = users.User(email=loanertest.TECHNICAL_ADMIN_EMAIL)
    self.assertTrue(self.call_test_as('api_for_admins_only', user))

    # Test permission for Operational Admin user.
    user = users.User(email=loanertest.OPERATIONAL_ADMIN_EMAIL)
    self.assertTrue(self.call_test_as('api_for_admins_only', user))

    # Test permission for Technician user.
    user = users.User(email=loanertest.TECHNICIAN_EMAIL)
    self.assertTrue(self.call_test_as('api_for_admins_only', user))

    # Test permission for normal user.
    user = users.User(email=loanertest.USER_EMAIL)
    with self.assertRaises(endpoints.ForbiddenException):
      self.call_test_as('api_for_admins_only', user)

    # Test permission for normal user, but not the assignee.
    user = users.User(email='someone-else@{}'.format(loanertest.USER_DOMAIN))
    with self.assertRaises(endpoints.ForbiddenException):
      self.call_test_as('api_for_assignee_or_admins', user)


if __name__ == '__main__':
  loanertest.main()
