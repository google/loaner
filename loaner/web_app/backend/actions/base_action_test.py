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

"""Tests for backend.actions.base_action."""

from loaner.web_app.backend.actions import base_action
from loaner.web_app.backend.testing import loanertest


class BaseActionTest(loanertest.TestCase):
  """Test the BaseAction class."""

  def test_success(self):

    class TestActionClass(base_action.BaseAction):
      ACTION_NAME = 'test'
      FRIENDLY_NAME = 'A test action'

      def run(self):
        return 'foo'

    test_instance = TestActionClass()
    self.assertEqual(test_instance.run(), 'foo')

  def test_failure_no_action_name(self):

    class TestActionClass(base_action.BaseAction):
      FRIENDLY_NAME = 'A test action'

      def run(self):
        return 'foo'

    expected_error_message = base_action._NO_ACTION_NAME_MSG % 'TestActionClass'
    self.assertRaisesRegexp(
        AttributeError, expected_error_message, TestActionClass)

  def test_failure_no_friendly_name(self):

    class TestActionClass(base_action.BaseAction):
      ACTION_NAME = 'test'

      def run(self):
        return 'foo'

    expected_error_message = base_action._NO_FRIENDLY_NAME_MSG % (
        'TestActionClass')
    self.assertRaisesRegexp(
        AttributeError, expected_error_message, TestActionClass)

  def test_failure_no_run_method(self):

    class TestActionClass(base_action.BaseAction):
      ACTION_NAME = 'test'
      FRIENDLY_NAME = 'A test action'

    expected_error_message = base_action._NO_RUN_METHOD_MSG % 'TestActionClass'
    self.assertRaisesRegexp(
        AttributeError, expected_error_message, TestActionClass)


if __name__ == '__main__':
  loanertest.main()
