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

"""Tests for backend.api.loaner_endpoints."""

import mock

from protorpc import message_types
from google.appengine.api import users
import endpoints

from loaner.web_app.backend.api import loaner_endpoints
from loaner.web_app.backend.api import root_api
from loaner.web_app.backend.auth import permissions
from loaner.web_app.backend.lib import xsrf
from loaner.web_app.backend.models import user_model
from loaner.web_app.backend.testing import loanertest


@root_api.ROOT_API.api_class(resource_name='fake', path='fake')
class FakeApiUserCheck(root_api.Service):

  @loaner_endpoints.authed_method(
      message_types.VoidMessage, http_method='POST', user_auth_only=True)
  def do_something(self, request):
    self.check_xsrf_token(self.request_state)
    return message_types.VoidMessage()


@root_api.ROOT_API.api_class(resource_name='fake2', path='fake2')
class FakeApiPermissionCheck(root_api.Service):

  @loaner_endpoints.authed_method(
      message_types.VoidMessage, http_method='POST', permission='enroll_device')
  def do_something(self, request):
    self.check_xsrf_token(self.request_state)
    return message_types.VoidMessage()


class LoanerEndpointsTest(loanertest.EndpointsTestCase):

  def setUp(self):
    super(LoanerEndpointsTest, self).setUp()
    self.service_user_auth_check = FakeApiUserCheck()
    self.service_permission_check = FakeApiPermissionCheck()
    self.request = message_types.VoidMessage()

    user_model.User(
        id=loanertest.TECHNICAL_ADMIN_EMAIL,
        roles=[permissions.TECHNICAL_ADMIN_ROLE.name]).put()
    user_model.User(
        id=loanertest.OPERATIONAL_ADMIN_EMAIL,
        roles=[permissions.OPERATIONAL_ADMIN_ROLE.name]).put()
    user_model.User(
        id=loanertest.TECHNICIAN_EMAIL,
        roles=[permissions.TECHNICIAN_ROLE.name]).put()
    user_model.User(
        id=loanertest.USER_EMAIL, roles=[permissions.USER_ROLE.name]).put()

  def call_test_as(self, user, user_auth_only=None, permission=None):
    """Used to make a call to FakeApiUserCheck and FakeApiPermissionCheck.

    These calls are made using different users.

    Args:
      user: users.User obj, the App Engine API users object being checked.
      user_auth_only: bool, set if checking user auth only,calling
      FakeApiUserCheck.
      permission: str,  passed if permission being checked, calling
      FakeApiPermissionCheck.

    Returns:
      True if permission or user auth passed the call to the FakeApiUserCheck
      or FakeApiPermissionCheck.
    """
    with mock.patch.object(
        xsrf, 'validate_request') as mock_validate_request:
      mock_validate_request.return_value = True
      with mock.patch.object(users, 'get_current_user') as mock_user:
        mock_user.return_value = user
        if user_auth_only and not permission:
          if (self.service_user_auth_check.do_something(
              self.request) == message_types.VoidMessage()):
            return True
        elif permission:
          if (self.service_permission_check.do_something(
              self.request) == message_types.VoidMessage()):
            return True

  def test_loaner_endpoints_auth_method(self):
    # Test no user logged in.
    permissions.constants.ON_GAE = True
    user = None
    with self.assertRaises(endpoints.NotFoundException):
      self.call_test_as(user=user, user_auth_only=True)

    with self.assertRaises(endpoints.NotFoundException):
      self.call_test_as(user=user, permission='enroll_shelf')

    # Test normal user_auth_only with valid user and domain.
    user = users.User(email=loanertest.USER_EMAIL)
    self.assertTrue(self.call_test_as(user=user, user_auth_only=True))

    # Make sure user_auth_only is not executed since permission is set.
    user = users.User(email=loanertest.USER_EMAIL)
    with self.assertRaises(endpoints.ForbiddenException):
      self.call_test_as(
          user=user, user_auth_only=True, permission='enroll_shelf')

    # Test user_auth_only invalid domain.
    user = users.User(email='daredevil@fakedomain.com')
    with self.assertRaises(endpoints.UnauthorizedException):
      self.call_test_as(user=user, user_auth_only=True)

    # Test permission for Technical Admin user.
    user = users.User(email=loanertest.TECHNICAL_ADMIN_EMAIL)
    self.assertTrue(self.call_test_as(user=user, permission='enroll_device'))

    # Test permission for Operational Admin user.
    user = users.User(email=loanertest.OPERATIONAL_ADMIN_EMAIL)
    self.assertTrue(self.call_test_as(user=user, permission='enroll_device'))

    # Test permission for Technician user.
    user = users.User(email=loanertest.TECHNICIAN_EMAIL)
    self.assertTrue(self.call_test_as(user=user, permission='enroll_device'))

    # Test permission for normal user.
    user = users.User(email=loanertest.USER_EMAIL)
    with self.assertRaises(endpoints.ForbiddenException):
      self.call_test_as(user=user, permission='enroll_shelf')

  def test_loaner_endpoints_auth_method_error(self):
    with self.assertRaises(loaner_endpoints.AuthCheckNotPresent):
      @loaner_endpoints.authed_method(
          message_types.VoidMessage, http_method='POST')
      def do_something():  # pylint: disable=unused-variable
        pass


if __name__ == '__main__':
  loanertest.main()
