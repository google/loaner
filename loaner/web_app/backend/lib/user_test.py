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

"""Tests for backend.lib.user."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import mock

import endpoints

from loaner.web_app.backend.lib import user
from loaner.web_app.backend.testing import loanertest


class UserTest(loanertest.EndpointsTestCase):

  def test_get_user_email(self):
    self.login_user()
    self.assertEqual(user.get_user_email(), loanertest.USER_EMAIL)

  def test_get_endpoints_user_email(self):
    self.login_endpoints_user()
    self.assertEqual(user.get_user_email(), loanertest.USER_EMAIL)

  @mock.patch('__main__.user.endpoints.get_current_user')
  @mock.patch('__main__.user.users.get_current_user')
  def test_endpoints_error(
      self, mock_currentuser, mock_currentuser_endpoint):
    mock_currentuser.return_value = None
    mock_currentuser_endpoint.side_effect = endpoints.InvalidGetUserCall
    with self.assertRaises(user.UserNotFound):
      user.get_user_email()

  @mock.patch('__main__.user.endpoints.get_current_user')
  @mock.patch('__main__.user.users.get_current_user')
  def test_get_user_email_no_user_found(
      self, mock_currentuser, mock_currentuser_endpoint):
    mock_currentuser.return_value = None
    mock_currentuser_endpoint.return_value = None
    with self.assertRaises(user.UserNotFound):
      user.get_user_email()

if __name__ == '__main__':
  loanertest.main()
