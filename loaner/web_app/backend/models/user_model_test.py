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

from loaner.web_app.backend.models import user_model
from loaner.web_app.backend.testing import loanertest


class UserModelTest(loanertest.EndpointsTestCase):

  def test_get_user(self):
    # No user model exists.
    user = user_model.User.get_by_id('undefined_user')
    self.assertEqual(user, None)

    # get_user will return user model.
    existing_user_in_datastore = user_model.User(
        id=loanertest.USER_EMAIL, roles=['test'])
    existing_user_in_datastore.put()
    user = user_model.User.get_user(loanertest.USER_EMAIL)
    self.assertEqual(user, existing_user_in_datastore)
    self.assertEqual(user.roles, existing_user_in_datastore.roles)

    # get_user will create new user model.
    user = user_model.User.get_user(email=loanertest.SUPER_ADMIN_EMAIL)
    self.assertEqual(user.key.id(), loanertest.SUPER_ADMIN_EMAIL)
    # make sure role is set to assignee by default
    self.assertEqual(user.roles, ['user'])

    # get user will create a new user model with an admin role.
    opt_roles = [
        'operational-admin', 'technical-admin', 'technician',
    ]
    user = user_model.User.get_user(
        email=loanertest.TECHNICAL_ADMIN_EMAIL, opt_roles=opt_roles)
    opt_roles.append('user')
    self.assertEqual(user.key.id(), loanertest.TECHNICAL_ADMIN_EMAIL)
    # make sure there is more than the default role
    for role in user.roles:
      self.assertTrue(role in opt_roles)

  def test_get_user_no_duplicates(self):
    # Test to make sure that the second call to get_user does not add a
    # duplicate of the opt_role.
    self.login_admin_endpoints_user(
        email=loanertest.TECHNICAL_ADMIN_EMAIL)
    user = user_model.User.get_user(
        loanertest.TECHNICAL_ADMIN_EMAIL,
        opt_roles=['technical-admin'])
    self.assertItemsEqual(
        ['user', 'technical-admin', 'operational-admin', 'technician'],
        user.roles)


if __name__ == '__main__':
  loanertest.main()
