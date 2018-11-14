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

"""Tests for backend.lib.action_loader."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import inspect
import logging
import pkgutil

import mock

from loaner.web_app.backend.actions import base_action
from loaner.web_app.backend.lib import action_loader
from loaner.web_app.backend.models import device_model
from loaner.web_app.backend.testing import loanertest


class WorkingActionClass1(base_action.BaseAction):
  """Test Action class."""
  ACTION_NAME = 'action1'
  FRIENDLY_NAME = 'Action 1'
  ACTION_TYPE = base_action.ActionType.SYNC

  def run(self, device=None):
    return device


class WorkingActionClass2(base_action.BaseAction):
  """Test Action class."""
  ACTION_NAME = 'action2'
  FRIENDLY_NAME = 'Action 2'

  def run(self, device=None):
    del device  # Unused.


class DuplicateActionClass(base_action.BaseAction):
  """Test Action class."""
  ACTION_NAME = 'action1'
  FRIENDLY_NAME = 'Action 1'

  def run(self, device=None):
    del device  # Unused.


class NonWorkingActionClass3(object):
  """Test class that doesn't inherit from base_action.BaseAction."""


class ActionClassWithoutActionName4(base_action.BaseAction):
  """Test Action class with no ACTION_NAME attribute."""
  FRIENDLY_NAME = 'Action 4'

  def run(self, device=None):
    del device  # Unused.


class ActionClassWithoutFriendlyName5(base_action.BaseAction):
  """Test Action class with no FRIENDLY_NAME attribute."""
  ACTION_NAME = 'action5'

  def run(self, device=None):
    del device  # Unused.


class ActionClassWithoutRunMethod6(base_action.BaseAction):
  """Test Action class with no run method."""
  ACTION_NAME = 'action6'
  FRIENDLY_NAME = 'Action 6'


class ActionImporterTest(loanertest.TestCase):
  """Tests for the Action Importer lib."""

  @mock.patch.object(logging, 'warning')
  @mock.patch.object(inspect, 'getmembers')
  @mock.patch.object(pkgutil, 'ImpImporter')
  def test_import(
      self, mock_impimporter, mock_getmembers, mock_logwarning):
    """Tests importing modules and actions with success."""
    mock_action_loader = mock.Mock()
    mock_impimporter.return_value = mock_action_loader
    mock_module_loader = mock.Mock()
    mock_action_loader.find_module = mock_module_loader

    mock_action_loader.iter_modules.return_value = [
        ('module1', 'fake_module'),
        ('module2', 'fake_module'),
        ('module3', 'fake_module'),
        ('module4', 'fake_module'),
        ('module5', 'fake_module'),
        ('module6', 'fake_module'),
        ('module1_test', 'fake_module'),  # Skipped test module.
        ('base_action', 'fake_module'),  # Skipped base_action module.
        ('module7', 'fake_module')
    ]
    mock_getmembers.side_effect = [
        (('WorkingActionClass1', WorkingActionClass1),
         ('NonClassObject', 'not-a-class')),
        (('WorkingActionClass2', WorkingActionClass2),
         ('NonClassObject', 'not-a-class')),
        (('NonWorkingActionClass3', NonWorkingActionClass3),),
        (('ActionClassWithoutActionName4', ActionClassWithoutActionName4),),
        (('ActionClassWithoutFriendlyName5', ActionClassWithoutFriendlyName5),),
        (('ActionClassWithoutRunMethod6', ActionClassWithoutRunMethod6),),
        (('DuplicateActionClass', DuplicateActionClass),),
    ]
    test_action_dict = action_loader.load_actions()
    test_device = device_model.Device()
    self.assertEqual(
        test_action_dict[base_action.ActionType.SYNC]['action1'].run(
            device=test_device),
        test_device)
    self.assertIsNone(
        test_action_dict[base_action.ActionType.ASYNC]['action2'].run())
    mock_logwarning.assert_has_calls([
        mock.call(action_loader._INSTANTIATION_ERROR_MSG % (
            'ActionClassWithoutActionName4', 'module4',
            base_action._NO_ACTION_NAME_MSG % (
                'ActionClassWithoutActionName4'))),
        mock.call(action_loader._INSTANTIATION_ERROR_MSG % (
            'ActionClassWithoutFriendlyName5', 'module5',
            base_action._NO_FRIENDLY_NAME_MSG % (
                'ActionClassWithoutFriendlyName5'))),
        mock.call(action_loader._INSTANTIATION_ERROR_MSG % (
            'ActionClassWithoutRunMethod6', 'module6',
            base_action._NO_RUN_METHOD_MSG % (
                'ActionClassWithoutRunMethod6'))),
    ])


if __name__ == '__main__':
  loanertest.main()
