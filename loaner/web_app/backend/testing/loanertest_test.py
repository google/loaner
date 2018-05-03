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

"""Tests for backend.testing.loanertest."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import mock

import endpoints

from loaner.web_app.backend.lib import action_loader  # pylint: disable=unused-import
from loaner.web_app.backend.testing import loanertest


class EndpointsTestCaseTest(loanertest.EndpointsTestCase):
  """Test the test loanertest EndpointsTestCase methods."""

  def test_successful_login_endpoints_user(self):
    """Test the successful login of an endpoints current user."""
    self.assertFalse(endpoints.get_current_user())
    self.login_endpoints_user()
    self.assertTrue(endpoints.get_current_user())
    self.assertEqual(
        endpoints.get_current_user().email(), loanertest.USER_EMAIL)


class ActionTestCaseTest(loanertest.ActionTestCase):
  """Test a successful use of the TestCase."""

  @mock.patch('__main__.action_loader.load_actions')
  def setUp(self, mock_importactions):
    self.testing_action = 'action_sample'
    self.fake_action = 'fake_action'
    mock_importactions.return_value = {
        'sync': {'action_sample': self.fake_action}}
    super(ActionTestCaseTest, self).setUp()

  def test_success(self):
    self.assertEqual(self.action, self.fake_action)


class ActionTestCaseTestNoTestingAction(loanertest.ActionTestCase):
  """Test what happens when you forget to specify self.testing_action."""

  def setUp(self):
    pass

  def test_fail(self):
    self.assertRaisesRegexp(
        EnvironmentError, '.*Create a TestCase setUp .* variable named.*',
        super(ActionTestCaseTestNoTestingAction, self).setUp)


class ActionTestCaseTestNoActions(loanertest.ActionTestCase):
  """Test what happens when there are no matching action modules available."""

  def setUp(self):
    pass

  @mock.patch('__main__.action_loader.load_actions')
  def test_fail(self, mock_importactions):
    self.testing_action = 'action_sample'
    mock_importactions.return_value = {}
    self.assertRaisesRegexp(
        EnvironmentError, '.*must import at least one.*',
        super(ActionTestCaseTestNoActions, self).setUp)


if __name__ == '__main__':
  loanertest.main()
