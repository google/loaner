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

from protorpc import message_types

from loaner.web_app.backend.api import user_api
from loaner.web_app.backend.api.messages import user_messages
from loaner.web_app.backend.models import user_model
from loaner.web_app.backend.testing import loanertest


class UserApiTest(loanertest.EndpointsTestCase):

  def setUp(self):
    super(UserApiTest, self).setUp()
    self.service = user_api.UserApi()

  def tearDown(self):
    super(UserApiTest, self).tearDown()
    self.service = None

  def test_get(self):
    """Test that a get returns the expected user message from the datastore."""
    self.login_endpoints_user(loanertest.USER_EMAIL)
    test_user_key = user_model.User(id=loanertest.USER_EMAIL).put()
    test_user = test_user_key.get()
    request = message_types.VoidMessage()
    expected_response = user_messages.User(
        email=test_user.key.id(), roles=[], permissions=[], superadmin=False)

    actual_response = self.service.get(request)

    self.assertEqual(actual_response.email, expected_response.email)
    self.assertEqual(actual_response.roles, expected_response.roles)
    self.assertEqual(actual_response.permissions, expected_response.permissions)
    self.assertEqual(actual_response.superadmin, expected_response.superadmin)

  def test_get__superadmin(self):
    self.login_admin_endpoints_user()

    response = self.service.get(message_types.VoidMessage())

    self.assertCountEqual(response.permissions,
                          user_api.permissions.Permissions.ALL)
    self.assertTrue(response.superadmin)


class RoleApiTest(loanertest.EndpointsTestCase):

  def setUp(self):
    super(RoleApiTest, self).setUp()
    self.service = user_api.RoleApi()
    self.login_admin_endpoints_user()

  def tearDown(self):
    super(RoleApiTest, self).tearDown()
    self.service = None

  def test_create(self):
    new_role = user_messages.Role(
        name='test',
        permissions=['get', 'put'],
        associated_group=loanertest.TECHNICAL_ADMIN_EMAIL)

    self.service.create(new_role)

    created_role = user_model.Role.get_by_name('test')
    self.assertEqual(new_role.name, created_role.name)
    self.assertCountEqual(new_role.permissions, created_role.permissions)

  def test_get(self):
    created_role = user_model.Role.create(
        name='test',
        role_permissions=['get', 'put'],
        associated_group=loanertest.TECHNICAL_ADMIN_EMAIL)

    retrieved_role = self.service.get(
        user_messages.GetRoleRequest(name='test'))

    self.assertEqual(created_role.name, retrieved_role.name)
    self.assertCountEqual(created_role.permissions, retrieved_role.permissions)
    self.assertEqual(
        created_role.associated_group, retrieved_role.associated_group)

  def test_update(self):
    created_role = user_model.Role.create(
        name='test',
        role_permissions=['get', 'put'],
        associated_group=loanertest.TECHNICAL_ADMIN_EMAIL)
    update_message = user_messages.Role(
        name='test',
        permissions=['get', 'create'],
        associated_group=loanertest.TECHNICAL_ADMIN_EMAIL)

    self.service.update(update_message)

    retrieved_role = user_model.Role.get_by_name('test')
    self.assertCountEqual(
        update_message.permissions, retrieved_role.permissions)
    self.assertEqual(
        created_role.associated_group, retrieved_role.associated_group)


if __name__ == '__main__':
  loanertest.main()
