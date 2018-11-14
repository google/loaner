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

"""Tests for backend.lib.events."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import logging
import pickle

import mock

from google.appengine.api import taskqueue
from loaner.web_app.backend.actions import base_action
from loaner.web_app.backend.lib import action_loader
from loaner.web_app.backend.lib import events
from loaner.web_app.backend.models import device_model
from loaner.web_app.backend.models import event_models
from loaner.web_app.backend.testing import loanertest

TEST_EVENT_MAPPINGS = {
    'event1': ['action1', 'action2'],
    'event2': ['action3', 'action4'],
    'reminder_level_0': ['action5', 'action6']
}


class EventsTest(loanertest.TestCase):
  """Tests for the Events lib."""

  @mock.patch.object(logging, 'error')
  @mock.patch.object(logging, 'info')
  @mock.patch.object(taskqueue, 'add')
  @mock.patch.object(events, 'get_actions_for_event')
  @mock.patch.object(action_loader, 'load_actions')
  def test_raise_event(
      self, mock_loadactions, mock_getactionsforevent,
      mock_taskqueueadd, mock_loginfo, mock_logerror):
    """Tests raising an Action if the Event is configured for Actions."""
    self.testbed.raise_event_patcher.stop()  # Disable patcher; use real method.

    # No Actions configured for the Event.
    mock_getactionsforevent.return_value = []
    events.raise_event('sample_event')
    mock_loginfo.assert_called_with(events._NO_ACTIONS_MSG, 'sample_event')

    # Everything is running smoothly.
    def side_effect1(device=None):
      """Side effect for sync action's run method that returns the model."""
      return device

    mock_sync_action = mock.Mock()
    mock_sync_action.run.side_effect = side_effect1
    mock_loadactions.return_value = {
        'sync': {'sync_action': mock_sync_action},
        'async': {
            'async_action1': 'fake_async_action1',
            'async_action2': 'fake_async_action2',
            'async_action3': 'fake_async_action3',
        }
    }
    mock_getactionsforevent.return_value = [
        'sync_action', 'async_action3', 'async_action1', 'async_action2']
    test_device = device_model.Device(
        chrome_device_id='4815162342', serial_number='123456')

    expected_async_payload = pickle.dumps({
        'async_actions': ['async_action1', 'async_action2', 'async_action3'],
        'device': test_device
    })

    events.raise_event('sample_event', device=test_device)

    expected_calls = [
        mock.call(
            queue_name='process-action',
            payload=expected_async_payload,
            target='default'),
    ]
    mock_taskqueueadd.assert_has_calls(expected_calls)
    mock_sync_action.run.assert_called_once_with(device=test_device)

    # A sync action raises a catchable exception.
    mock_sync_action.reset_mock()
    mock_logerror.reset_mock()
    mock_getactionsforevent.reset_mock()
    mock_loadactions.reset_mock()

    def side_effect2(device=None):
      """Side effect for sync action's run method that returns the model."""
      del device  # Unused.
      raise base_action.BadDeviceError('Found a bad attribute.')

    mock_sync_action.run.side_effect = side_effect2
    mock_loadactions.return_value = {
        'sync': {'sync_action': mock_sync_action}, 'async': {}}
    mock_getactionsforevent.return_value = ['sync_action']

    with self.assertRaises(events.EventActionsError):
      events.raise_event('sample_event', device=test_device)
      self.assertLen(mock_logerror.mock_calls, 1)

    self.testbed.raise_event_patcher.start()  # Because cleanup will stop().

  @mock.patch.object(events, 'get_all_event_action_mappings')
  def test_get_actions_for_event(self, mock_getalleventmappings):
    """Tests simple get_actions_for_event function."""

    # No Event-Action mappings.
    mock_getalleventmappings.return_value = {}
    self.assertRaises(events.NoEventsError, events.get_actions_for_event, 'foo')

    mock_getalleventmappings.return_value = TEST_EVENT_MAPPINGS
    self.assertEqual(
        events.get_actions_for_event('event2'), ['action3', 'action4'])

  def test_get_all_event_action_mappings_no_existing(self):
    """Tests get_all_event_action_mappings when they're not in memcache."""
    core_event = event_models.CoreEvent.create('event1')
    core_event.actions = ['action1', 'action2']
    core_event.put()
    custom_event = event_models.CustomEvent.create('event2')
    custom_event.model = 'Device'
    custom_event.actions = ['action3', 'action4']
    custom_event.put()
    reminder_event = event_models.ReminderEvent.create(0)
    reminder_event.actions = ['action5', 'action6']
    self.assertDictEqual(
        events.get_all_event_action_mappings(), TEST_EVENT_MAPPINGS)


if __name__ == '__main__':
  loanertest.main()
