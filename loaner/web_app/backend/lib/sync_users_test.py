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

"""Tests for backend.lib.sync_users."""

import mock

from loaner.web_app.backend.clients import directory
from loaner.web_app.backend.lib import sync_users
from loaner.web_app.backend.models import user_model
from loaner.web_app.backend.testing import loanertest


class SyncUsersTest(loanertest.EndpointsTestCase):

  def setUp(self):
    super(SyncUsersTest, self).setUp()

    user_model.User.get_user(
        'tech_admin_user@{}'.format(loanertest.USER_DOMAIN))
    user_model.User.get_user(
        'tech_admin_user2@{}'.format(loanertest.USER_DOMAIN),
        opt_roles=['technical-admin', 'operational-admin'])
    user_model.User.get_user(
        'ops_admin_user@{}'.format(loanertest.USER_DOMAIN))
    user_model.User.get_user(
        'ops_admin_user2@{}'.format(loanertest.USER_DOMAIN),
        opt_roles=['operational-admin'])
    user_model.User.get_user('technician@{}'.format(loanertest.USER_DOMAIN))
    user_model.User.get_user(
        'technician2@{}'.format(loanertest.USER_DOMAIN),
        opt_roles=['technician'])
    user_model.User.get_user(loanertest.USER_EMAIL)
    self.datastore_technical_admin_users = user_model.User.query(
        user_model.User.roles.IN(
            ['technical-admin'])).fetch(keys_only=True)
    self.datastore_operational_admin_users = user_model.User.query(
        user_model.User.roles.IN(
            ['operational-admin'])).fetch(keys_only=True)
    self.datastore_technician_users = user_model.User.query(
        user_model.User.roles.IN(['technician'])).fetch(keys_only=True)

    self.directory_obj_tech_admins = [
        {'members': [
            {'email': 'tech_admin_user@{}'.format(loanertest.USER_DOMAIN)},
        ],
         'nextPageToken': 'AHmOf6b_Ika37tPYH5N'},
        {'members': [
            {'email': 'tech_admin_user2@{}'.format(loanertest.USER_DOMAIN)},
        ],
         'nextPageToken': 'AHmOf6b_Ika37tPYH5N'},
        {'members': [
            {'email': 'tech_admin_user3@{}'.format(loanertest.USER_DOMAIN)},
        ],
        }
    ]
    self.directory_obj_tech_admins_no_pagetoken = [
        {'members': [
            {'email': 'tech_admin_user@{}'.format(loanertest.USER_DOMAIN)},
        ],
        }
    ]
    self.populated_tech_admins_list = [
        'tech_admin_user@{}'.format(loanertest.USER_DOMAIN),
        'tech_admin_user2@{}'.format(loanertest.USER_DOMAIN),
        'tech_admin_user3@{}'.format(loanertest.USER_DOMAIN)]
    self.populated_ops_admins_list = [
        'ops_admin_user@{}'.format(loanertest.USER_DOMAIN),
        'ops_admin_user2@{}'.format(loanertest.USER_DOMAIN),
        'ops_admin_user3@{}'.format(loanertest.USER_DOMAIN)]
    self.populated_technicians_list = [
        'technician@{}'.format(loanertest.USER_DOMAIN),
        'technician2@{}'.format(loanertest.USER_DOMAIN),
        'technician3@{}'.format(loanertest.USER_DOMAIN)]

  @mock.patch('__main__.sync_users.logging.info')
  @mock.patch('__main__.sync_users.directory.DirectoryApiClient')
  def test_sync_user_roles(self, mock_directoryclass, mock_logging_info):
    del mock_directoryclass  # Unused.
    sync_users.sync_user_roles()
    mock_logging_info.assert_called_once()

  @mock.patch('__main__.sync_users.directory.DirectoryApiClient')
  def test_get_users_directory_check(self, mock_directoryclass):
    mockdirectoryclient = mock_directoryclass.return_value
    mockdirectoryclient.users_in_group.side_effect = (
        self.directory_obj_tech_admins)
    tech_admin_users = sync_users._get_users_directory(
        loanertest.USER_EMAIL, mockdirectoryclient)
    self.assertListEqual(tech_admin_users, self.populated_tech_admins_list)

  @mock.patch('__main__.sync_users.directory.DirectoryApiClient')
  def test_get_users_directory_check_rpcerror_with_nextpagetoken(
      self, mock_directoryclass):
    directory_obj_rpcerror = [
        {'members': [
            {'email': 'tech_admin_user@{}'.format(loanertest.USER_DOMAIN)},
        ],
         'nextPageToken': 'AHmOf6b_Ika37tPYH5N'},
        directory.DirectoryRPCError('Directory Failed')
    ]
    mockdirectoryclient = mock_directoryclass.return_value
    mockdirectoryclient.users_in_group.side_effect = (directory_obj_rpcerror)
    with self.assertRaisesRegexp(
        sync_users.InvalidCallToDirectoryError,
        sync_users._DIR_CALL_INVALID_MSG % 'Directory Failed'):
      sync_users._get_users_directory(
          loanertest.USER_EMAIL, mockdirectoryclient)

  @mock.patch('__main__.sync_users.directory.DirectoryApiClient')
  def test_get_users_directory_check_no_pagetoken(
      self, mock_directoryclass):
    mockdirectoryclient = mock_directoryclass.return_value
    mockdirectoryclient.users_in_group.side_effect = (
        self.directory_obj_tech_admins_no_pagetoken)
    tech_admin_users = sync_users._get_users_directory(
        loanertest.USER_EMAIL, mockdirectoryclient)
    self.assertListEqual(
        tech_admin_users, ['tech_admin_user@{}'.format(loanertest.USER_DOMAIN)])

  @mock.patch('__main__.sync_users.directory.DirectoryApiClient')
  def test_get_users_directory_invalid_call(self, mock_directoryclass):
    def raise_error(group_email):
      raise directory.DirectoryRPCError(group_email)
    mockdirectoryclient = mock_directoryclass.return_value
    mockdirectoryclient.users_in_group.side_effect = raise_error

    # Should raise an error when the call to Directory API fails in any way.
    with self.assertRaises(sync_users.InvalidCallToDirectoryError):
      sync_users._get_users_directory(
          group_email='', client=mockdirectoryclient)
    mockdirectoryclient.users_in_group.side_effect = (
        self.directory_obj_tech_admins)

  def test_add_or_remove_user_roles_technical_admins(self):
    sync_users._add_or_remove_user_roles(
        users_keys=self.datastore_technical_admin_users,
        group_users=self.populated_tech_admins_list,
        role='technical-admin')
    # Make sure tech_admin_user still has technical-admin role.
    user = user_model.User.get_user(
        'tech_admin_user@{}'.format(loanertest.USER_DOMAIN))
    self.assertListEqual(
        user.roles,
        ['user', 'technical-admin'])
    # Make sure that tech_admin_user2 got technical-admin role
    # added.
    user = user_model.User.get_user(
        'tech_admin_user2@{}'.format(loanertest.USER_DOMAIN))
    self.assertTrue('technical-admin' in user.roles)
    # Make sure that tech_admin_user3 was created and roles
    # added.
    user = user_model.User.get_user(
        'tech_admin_user3@{}'.format(loanertest.USER_DOMAIN))
    self.assertListEqual(
        user.roles,
        ['user', 'technical-admin'])

  def test_add_or_remove_user_roles_operational_admins(self):
    sync_users._add_or_remove_user_roles(
        users_keys=self.datastore_operational_admin_users,
        group_users=self.populated_ops_admins_list,
        role='operational-admin')
    # Make sure ops_admin_user still has technical-admin role.
    user = user_model.User.get_user(
        'ops_admin_user@{}'.format(loanertest.USER_DOMAIN))
    self.assertListEqual(
        user.roles,
        ['user', 'operational-admin'])
    # Make sure that ops_admin_user2 got technical-admin role
    # added.
    user = user_model.User.get_user(
        'ops_admin_user2@{}'.format(loanertest.USER_DOMAIN))
    self.assertTrue('operational-admin' in user.roles)
    self.assertEqual(len(user.roles), 2)
    # Make sure that ops_admin_user3 was created and roles added.
    user = user_model.User.get_user(
        'ops_admin_user3@{}'.format(loanertest.USER_DOMAIN))
    self.assertListEqual(
        user.roles,
        ['user', 'operational-admin'])

    # Make sure that tech_admin_user2 got role removed.
    user = user_model.User.get_user(
        'tech_admin_user2@{}'.format(loanertest.USER_DOMAIN))
    self.assertTrue('operational-admin' not in user.roles)

  def test_add_or_remove_user_roles_technicians(self):
    sync_users._add_or_remove_user_roles(
        users_keys=self.datastore_technician_users,
        group_users=self.populated_technicians_list,
        role='technician')
    # Make sure technician still has technical-admin role.
    user = user_model.User.get_user(
        'technician@{}'.format(loanertest.USER_DOMAIN))
    self.assertListEqual(
        user.roles, ['user', 'technician'])
    # Make sure that technician2 got technical-admin role added.
    user = user_model.User.get_user(
        'technician2@{}'.format(loanertest.USER_DOMAIN))
    self.assertTrue('technician' in user.roles)
    self.assertEqual(len(user.roles), 2)
    # Make sure that technician3 was created and roles added.
    user = user_model.User.get_user(
        'technician3@{}'.format(loanertest.USER_DOMAIN))
    self.assertListEqual(
        user.roles, ['user', 'technician'])

if __name__ == '__main__':
  loanertest.main()
