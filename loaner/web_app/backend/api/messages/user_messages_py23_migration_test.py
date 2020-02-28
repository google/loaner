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

# Lint as: python3
"""Tests for web_app.backend.api.messages.user_messages."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from loaner.web_app.backend.api.messages import user_messages
from absl.testing import absltest


class UserMessagesPy23MigrationTest(absltest.TestCase):

  def testUser(self):
    user = user_messages.User(
        email='fake@email.com',
        roles=['FAKE-ROLE-1', 'FAKE-ROLE-2'],
        permissions=['FAKE-PERMISSION-1', 'FAKE-PERMISSION-2'],
        superadmin=True)

    self.assertTrue(user.superadmin)
    self.assertEqual(user.email, 'fake@email.com')
    self.assertListEqual(user.roles, ['FAKE-ROLE-1', 'FAKE-ROLE-2'])
    self.assertListEqual(
        user.permissions, ['FAKE-PERMISSION-1', 'FAKE-PERMISSION-2'])

  def testRole(self):
    role = user_messages.Role(
        name='FAKE-ROLE-NAME',
        permissions=['FAKE-PERMISSION-1', 'FAKE-PERMISSION-2'],
        associated_group='FAKE-ASSOCIATED-GROUP')

    self.assertEqual(role.name, 'FAKE-ROLE-NAME')
    self.assertEqual(role.associated_group, 'FAKE-ASSOCIATED-GROUP')
    self.assertListEqual(
        role.permissions, ['FAKE-PERMISSION-1', 'FAKE-PERMISSION-2'])

  def testGetRoleRequest(self):
    get_role_req = user_messages.GetRoleRequest(name='FAKE-ROLE-NAME')
    self.assertEqual(get_role_req.name, 'FAKE-ROLE-NAME')

  def testListRoleResponse(self):
    role_1 = user_messages.Role(name='FAKE-ROLE-NAME-1')
    role_2 = user_messages.Role(name='FAKE-ROLE-NAME-2')
    list_role_resp = user_messages.ListRoleResponse(roles=[role_1, role_2])
    self.assertListEqual(list_role_resp.roles, [role_1, role_2])

  def testDeleteRoleRequest(self):
    delete_role_req = user_messages.DeleteRoleRequest(name='FAKE-ROLE-NAME')
    self.assertEqual(delete_role_req.name, 'FAKE-ROLE-NAME')


if __name__ == '__main__':
  absltest.main()
