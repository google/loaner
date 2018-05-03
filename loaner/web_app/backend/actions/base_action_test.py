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

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from absl import logging
from absl.testing import parameterized

from loaner.web_app.backend.actions import base_action
from loaner.web_app.backend.models import device_model
from loaner.web_app.backend.testing import loanertest


class TestActionNoActionName(base_action.BaseAction):
  FRIENDLY_NAME = 'A test action'

  def run(self, device=None):
    del device  # Unused.
    return 'foo'

no_action_name_error = base_action._NO_ACTION_NAME_MSG % (
    'TestActionNoActionName')


class TestActionNoFriendlyName(base_action.BaseAction):
  ACTION_NAME = 'test'

  def run(self, device=None):
    del device  # Unused.
    return 'foo'

no_friendly_name_error = base_action._NO_FRIENDLY_NAME_MSG % (
    'TestActionNoFriendlyName')


class TestActionNoRunMethod(base_action.BaseAction):
  ACTION_NAME = 'test'
  FRIENDLY_NAME = 'A test action'

no_run_method_error = base_action._NO_RUN_METHOD_MSG % 'TestActionNoRunMethod'


class TestActionBadSyncRunMethod(base_action.BaseAction):
  ACTION_NAME = 'test'
  FRIENDLY_NAME = 'A test action'
  ACTION_TYPE = base_action.ActionType.SYNC

  def run(self, device=None):
    del device  # Unused.

bad_sync_run_method_error = base_action._BAD_SYNC_RUN_MSG % (
    'TestActionBadSyncRunMethod')


class TestActionBadAsyncRunMethod(base_action.BaseAction):
  ACTION_NAME = 'test'
  FRIENDLY_NAME = 'A test action'
  ACTION_TYPE = base_action.ActionType.ASYNC

  def run(self, device=None):
    return device

bad_async_run_method_error = base_action._BAD_ASYNC_RUN_MSG % (
    'TestActionBadAsyncRunMethod')


class TestActionSyncSuccess(base_action.BaseAction):
  ACTION_NAME = 'test'
  FRIENDLY_NAME = 'A test action'
  ACTION_TYPE = base_action.ActionType.SYNC

  def run(self, device=None):
    logging.info('blah')
    return device


class TestActionAsyncSuccess(base_action.BaseAction):
  ACTION_NAME = 'test'
  FRIENDLY_NAME = 'A test action'
  ACTION_TYPE = base_action.ActionType.ASYNC

  def run(self, device=None):
    del device  # Unused.
    logging.info('blah')


class BaseActionTest(parameterized.TestCase, loanertest.TestCase):
  """Test the BaseAction class."""

  @parameterized.parameters(
      (TestActionNoActionName, no_action_name_error),
      (TestActionNoFriendlyName, no_friendly_name_error),
      (TestActionNoRunMethod, no_run_method_error)
  )
  def test_failures_missing_attributes(self, test_class, error):
    self.assertRaisesWithLiteralMatch(AttributeError, error, test_class)

  @parameterized.parameters(
      (TestActionBadSyncRunMethod, bad_sync_run_method_error),
      (TestActionBadAsyncRunMethod, bad_async_run_method_error),
  )
  def test_failures_bad_run_methods(self, test_class, error):
    test_device = device_model.Device()
    test_instance = test_class()
    self.assertRaisesWithLiteralMatch(
        TypeError, error, test_instance.run, device=test_device)

  def test_run_success_sync(self):
    test_device = device_model.Device()
    test_instance = TestActionSyncSuccess()
    test_response = test_instance.run(device=test_device)
    self.assertEqual(test_device, test_response)

  def test_run_success_async(self):
    test_device = device_model.Device()
    test_instance = TestActionAsyncSuccess()
    test_response = test_instance.run(device=test_device)
    self.assertIsNone(test_response)


if __name__ == '__main__':
  loanertest.main()
