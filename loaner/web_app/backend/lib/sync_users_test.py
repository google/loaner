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

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import mock

from loaner.web_app import constants
from loaner.web_app.backend.clients import directory
from loaner.web_app.backend.lib import sync_users
from loaner.web_app.backend.models import user_model
from loaner.web_app.backend.testing import loanertest


class SyncUsersTest(loanertest.EndpointsTestCase):

  def setUp(self):
    super(SyncUsersTest, self).setUp()
    user_model.Role.create(
        name='technician',
        associated_group='technicians@{}'.format(loanertest.USER_DOMAIN))

    patcher = mock.patch.object(directory, 'DirectoryApiClient')
    mock_directory = patcher.start()
    self.addCleanup(patcher.stop)
    mock_users_for_group = mock_directory.return_value.get_all_users_in_group

    def group_client_side_effect(*args, **kwargs):  # pylint: disable=unused-argument
      if args[0] == constants.SUPERADMINS_GROUP:
        return [
            'need-superadmin@{}'.format(loanertest.USER_DOMAIN),
            'keep-superadmin@{}'.format(loanertest.USER_DOMAIN),
        ]
      elif args[0] == 'technicians@{}'.format(loanertest.USER_DOMAIN):
        return [
            'need-technician@{}'.format(loanertest.USER_DOMAIN),
            'keep-technician@{}'.format(loanertest.USER_DOMAIN),
        ]
    mock_users_for_group.side_effect = group_client_side_effect

  def test_sync_user_roles__standard_user(self):
    user_model.User.get_user('standard-user@{}'.format(loanertest.USER_DOMAIN))

    sync_users.sync_user_roles()

    self.make_assertions(
        'standard-user@{}'.format(loanertest.USER_DOMAIN), [], False)

  def test_sync_user_roles__superadmin(self):
    user_model.User.get_user(
        'need-superadmin@{}'.format(loanertest.USER_DOMAIN))
    user_model.User.get_user(
        'remove-superadmin@{}'.format(loanertest.USER_DOMAIN)
    ).update(superadmin=True)
    user_model.User.get_user(
        'keep-superadmin@{}'.format(loanertest.USER_DOMAIN)
    ).update(superadmin=True)

    sync_users.sync_user_roles()

    self.make_assertions(
        'need-superadmin@{}'.format(loanertest.USER_DOMAIN), [], True)
    self.make_assertions(
        'remove-superadmin@{}'.format(loanertest.USER_DOMAIN), [], False)
    self.make_assertions(
        'keep-superadmin@{}'.format(loanertest.USER_DOMAIN), [], True)

  def test_sync_User_roles__role(self):
    user_model.User.get_user(
        'need-technician@{}'.format(loanertest.USER_DOMAIN))
    user_model.User.get_user(
        'remove-technician@{}'.format(loanertest.USER_DOMAIN)
    ).update(roles=['technician'])
    user_model.User.get_user(
        'keep-technician@{}'.format(loanertest.USER_DOMAIN)
    ).update(roles=['technician'])

    sync_users.sync_user_roles()

    self.make_assertions(
        'need-technician@{}'.format(loanertest.USER_DOMAIN), ['technician'],
        False)
    self.make_assertions(
        'remove-technician@{}'.format(loanertest.USER_DOMAIN), [], False)
    self.make_assertions(
        'keep-technician@{}'.format(loanertest.USER_DOMAIN), ['technician'],
        False)

  def make_assertions(self, user_id, roles, superadmin):
    """Asserts that users have correct roles/superadmin.

    Args:
      user_id: str, user email ID.
      roles: list|str|, roles user should have.
      superadmin: bool, if the user should be superadmin.
    """
    user = user_model.User.get_user(user_id)
    self.assertCountEqual(user.role_names, roles)
    self.assertEqual(user.superadmin, superadmin)

if __name__ == '__main__':
  loanertest.main()
