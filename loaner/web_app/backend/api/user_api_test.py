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

"""Tests for backend.api.user_api."""

import mock

from protorpc import message_types

from loaner.web_app.backend.api import root_api  # pylint: disable=unused-import
from loaner.web_app.backend.api import user_api
from loaner.web_app.backend.api.messages import user_message
from loaner.web_app.backend.auth import permissions
from loaner.web_app.backend.models import user_model
from loaner.web_app.backend.testing import loanertest


class UserApiTest(loanertest.EndpointsTestCase):

  def setUp(self):
    super(UserApiTest, self).setUp()
    self.service = user_api.UserApi()
    self.login_admin_endpoints_user()

    self.patcher_build = mock.patch(
        '__main__.root_api.Service.check_xsrf_token')
    self.mock_build = self.patcher_build.start()
    self.addCleanup(self.patcher_build.stop)
    user_model.User.get_user(
        email=loanertest.TECHNICAL_ADMIN_EMAIL,
        opt_roles=[permissions.TECHNICAL_ADMIN_ROLE.name])
    user_model.User.get_user(
        email=loanertest.OPERATIONAL_ADMIN_EMAIL,
        opt_roles=[permissions.OPERATIONAL_ADMIN_ROLE.name])
    user_model.User.get_user(
        email=loanertest.TECHNICIAN_EMAIL,
        opt_roles=[permissions.TECHNICIAN_ROLE.name]).put()
    user_model.User.get_user(
        email=loanertest.USER_EMAIL, opt_roles=[permissions.USER_ROLE.name])
    self.users_list = [
        loanertest.TECHNICAL_ADMIN_EMAIL, loanertest.OPERATIONAL_ADMIN_EMAIL,
        loanertest.TECHNICIAN_EMAIL, loanertest.USER_EMAIL,
        loanertest.SUPER_ADMIN_EMAIL]
    self.admin_list = [
        loanertest.TECHNICAL_ADMIN_EMAIL, loanertest.SUPER_ADMIN_EMAIL]

  def tearDown(self):
    super(UserApiTest, self).tearDown()
    self.service = None

  def test_get_no_email_provided(self):
    request = user_message.GetUserRequest()
    self.assertRaisesRegexp(
        user_api.endpoints.BadRequestException,
        user_api._USER_EMAIL_PROVIDED_MSG,
        self.service.get,
        request)

  def test_get_email_provided(self):
    request = user_message.GetUserRequest(
        email=loanertest.TECHNICAL_ADMIN_EMAIL)
    response = self.service.get(request)

    self.assertEqual(response.email, loanertest.TECHNICAL_ADMIN_EMAIL)
    self.assertTrue(permissions.TECHNICAL_ADMIN_ROLE.name in response.roles)

  def test_get_roles(self):
    self.login_endpoints_user()
    response = self.service.get_role(message_types.VoidMessage())

    self.assertEqual(response.email, loanertest.USER_EMAIL)
    self.assertEqual(response.roles, [permissions.USER_ROLE.name])


if __name__ == '__main__':
  loanertest.main()
