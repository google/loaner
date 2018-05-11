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

"""Tests for backend.models.user_model."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from loaner.web_app.backend.api import permissions
from loaner.web_app.backend.models import user_model
from loaner.web_app.backend.testing import loanertest


class RoleModelTest(loanertest.TestCase):

  def setUp(self):
    super(RoleModelTest, self).setUp()
    self.role_name = 'Technician'
    self.permissions = (permissions.Permissions.BOOTSTRAP,
                        permissions.Permissions.MODIFY_SHELF)
    self.associated_group = 'technicians@example.com'

  def test_create_role(self):
    user_model.Role.create(
        self.role_name, self.permissions, self.associated_group)

    created_role = user_model.Role.get_by_id(self.role_name)
    self.assertEqual(created_role.name, self.role_name)
    self.assertCountEqual(created_role.permissions, self.permissions)

  def test_create_role__create_superadmin(self):
    self.assertRaises(
        user_model.CreateRoleError, user_model.Role.create,
        name='superadmin')

  def test_create_role__name_exists(self):
    user_model.Role.create('test')
    self.assertRaises(
        user_model.CreateRoleError, user_model.Role.create,
        name='test')

  def test_get_by_name(self):
    user_model.Role.create(
        self.role_name, self.permissions, self.associated_group)

    retrieved_role = user_model.Role.get_by_name(self.role_name)

    self.assertEqual(retrieved_role.name, self.role_name)
    self.assertCountEqual(retrieved_role.permissions, self.permissions)

  def test_update(self):
    user_model.Role.create(
        self.role_name, self.permissions, self.associated_group)
    updated_permissions = (permissions.Permissions.AUDIT_SHELF,
                           permissions.Permissions.BOOTSTRAP,
                           permissions.Permissions.MODIFY_SURVEY)

    role = user_model.Role.get_by_id(self.role_name)
    role.update(permissions=updated_permissions)

    self.assertCountEqual(role.permissions, updated_permissions)
    self.assertEqual(role.associated_group, self.associated_group)

  def test_update__name_error(self):
    user_model.Role.create(
        self.role_name, self.permissions, self.associated_group)

    retrieved_role = user_model.Role.get_by_id(self.role_name)
    self.assertRaises(
        user_model.UpdateRoleError, retrieved_role.update, name='test')


class UserModelTest(loanertest.TestCase):

  def setUp(self):
    super(UserModelTest, self).setUp()
    self.technician_role = user_model.Role.create(
        name='technician',
        role_permissions=[
            permissions.Permissions.AUDIT_SHELF,
            permissions.Permissions.READ_SHELVES,
        ],
        associated_group='technicians@example.com')
    self.operations_role = user_model.Role.create(
        name='operations',
        role_permissions=[
            permissions.Permissions.MODIFY_DEVICE,
            permissions.Permissions.MODIFY_SHELF,
        ],
        associated_group='operations@example.com')

  def test_role_names(self):
    user = user_model.User(id=loanertest.USER_EMAIL)
    roles = ['technician', 'operations']
    user.update(roles=roles)

    self.assertCountEqual(roles, user.role_names)

  def test_role_names__no_roles(self):
    user = user_model.User(id=loanertest.USER_EMAIL)
    self.assertEqual(user.role_names, [])

  def test_get_user(self):
    # No user model exists.
    user = user_model.User.get_by_id('undefined_user')
    self.assertEqual(user, None)

    # get_user will return user model.
    existing_user_in_datastore = user_model.User(id=loanertest.USER_EMAIL)
    existing_user_in_datastore.put()
    user = user_model.User.get_user(loanertest.USER_EMAIL)
    self.assertEqual(user, existing_user_in_datastore)

    # get_user will create new user model.
    user = user_model.User.get_user(email=loanertest.SUPER_ADMIN_EMAIL)
    self.assertEqual(user.key.id(), loanertest.SUPER_ADMIN_EMAIL)

  def test_update__superadmin(self):
    user = user_model.User.get_user(email=loanertest.SUPER_ADMIN_EMAIL)
    self.assertFalse(user.superadmin)
    user.update(superadmin=True)
    self.assertTrue(user.superadmin)
    datastore_user = user_model.User.get_by_id(loanertest.SUPER_ADMIN_EMAIL)
    self.assertTrue(datastore_user.superadmin)

  def test_update__one_role(self):
    user = user_model.User(id=loanertest.USER_EMAIL)

    user.update(roles=['technician'])

    self.assertEqual(user.roles, [self.technician_role.key])

  def test_update__remove_roles(self):
    user = user_model.User(id=loanertest.USER_EMAIL)
    user.update(roles=['technician'])
    self.assertCountEqual(user.role_names, ['technician'])

    user.update(roles=[])

    self.assertEqual(user.roles, [])

  def test_update__multiple_roles(self):
    user = user_model.User(id=loanertest.USER_EMAIL)
    expected_roles = [self.technician_role.key, self.operations_role.key]

    user.update(roles=['technician', 'operations'])

    self.assertCountEqual(user.roles, expected_roles)

  def test_update__invalid_role(self):
    user = user_model.User(id=loanertest.USER_EMAIL)

    self.assertRaises(user_model.RoleNotFoundError, user.update,
                      roles=['unknown'])

  def test_get_permissions__one_role(self):
    user = user_model.User(id=loanertest.USER_EMAIL)
    user.update(roles=['technician'])

    self.assertCountEqual(user.get_permissions(),
                          self.technician_role.permissions)

  def test_get_permissions__multiple_roles(self):
    user = user_model.User(id=loanertest.USER_EMAIL)
    user.update(roles=['technician', 'operations'])
    expected_permissions = [
        permissions.Permissions.AUDIT_SHELF,
        permissions.Permissions.READ_SHELVES,
        permissions.Permissions.MODIFY_DEVICE,
        permissions.Permissions.MODIFY_SHELF,
    ]

    self.assertCountEqual(user.get_permissions(), expected_permissions)

  def test_get_permissions__superadmin(self):
    user = user_model.User.get_user(email=loanertest.SUPER_ADMIN_EMAIL)
    user.update(superadmin=True)

    self.assertCountEqual(user.get_permissions(), permissions.Permissions.ALL)


if __name__ == '__main__':
  loanertest.main()
