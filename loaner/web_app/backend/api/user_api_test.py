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

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from absl.testing import parameterized

from protorpc import message_types

from loaner.web_app.backend.api import user_api
from loaner.web_app.backend.api.messages import user_messages
from loaner.web_app.backend.models import user_model
from loaner.web_app.backend.testing import loanertest


class UserApiTest(loanertest.EndpointsTestCase, parameterized.TestCase):

  def setUp(self):
    super(UserApiTest, self).setUp()
    self.service = user_api.UserApi()

  def tearDown(self):
    super(UserApiTest, self).tearDown()
    self.service = None

  @parameterized.parameters(
      {'test_email': loanertest.USER_EMAIL, 'test_roles': ['user'],},
      {'test_email': loanertest.TECHNICIAN_EMAIL, 'test_roles': [
          'technician', 'user'],},
      {'test_email': loanertest.OPERATIONAL_ADMIN_EMAIL, 'test_roles': [
          'operational-admin', 'user'],},
      {'test_email': loanertest.TECHNICAL_ADMIN_EMAIL, 'test_roles': [
          'technical-admin', 'user'],},
      {'test_email': loanertest.SUPER_ADMIN_EMAIL, 'test_roles': [
          'technical-admin', 'operational-admin', 'technician', 'user'],},)
  def test_get(self, test_email, test_roles):
    """Test that a get returns the expected user message from the datastore."""
    self.login_endpoints_user(test_email)
    test_user_key = user_model.User(id=test_email, roles=test_roles).put()
    test_user = test_user_key.get()
    request = message_types.VoidMessage()
    expected_response = user_messages.UserResponse(
        email=test_user.key.id(), roles=test_user.roles)
    actual_response = self.service.get(request)
    self.assertEqual(actual_response.email, expected_response.email)
    self.assertCountEqual(actual_response.roles, expected_response.roles)


if __name__ == '__main__':
  loanertest.main()
