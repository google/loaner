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

import pickle

import mock

from google.appengine.api import memcache

from loaner.web_app.backend.lib import events
from loaner.web_app.backend.models import device_model
from loaner.web_app.backend.models import event_models
from loaner.web_app.backend.models import shelf_model
from loaner.web_app.backend.testing import loanertest

TEST_EVENT_MAPPINGS = {
    'event1': ['action1', 'action2'],
    'event2': ['action3', 'action4'],
    'reminder_level_0': ['action5', 'action6']
}


class EventsTest(loanertest.TestCase):
  """Tests for the Events lib."""

  @mock.patch('__main__.events.logging.info')
  @mock.patch('__main__.events.taskqueue.add')
  @mock.patch('__main__.events.get_actions_for_event')
  def test_raise_event(
      self, mock_geteventactions, mock_taskqueueadd, mock_loginfo):
    """Tests raising an Action if the Event is configured for Actions."""

    self.testbed.raise_event_patcher.stop()  # Disable patcher; use real method.

    # No Actions configured for the Event.
    mock_geteventactions.return_value = []
    events.raise_event('sample_event')
    mock_loginfo.assert_called_with(events._NO_ACTIONS_MSG, 'sample_event')

    mock_geteventactions.return_value = ['action1', 'action2']
    test_device = device_model.Device(
        chrome_device_id='4815162342', serial_number='123456')
    test_shelf = shelf_model.Shelf(capacity=42, location='Helpdesk 123')
    expected_payload1 = pickle.dumps({
        'action_name': 'action1',
        'device': test_device,
        'shelf': test_shelf
    })
    expected_payload2 = pickle.dumps({
        'action_name': 'action2',
        'device': test_device,
        'shelf': test_shelf
    })

    events.raise_event('sample_event', device=test_device, shelf=test_shelf)

    self.testbed.raise_event_patcher.start()  # Because cleanup will stop().

    expected_calls = [
        mock.call(
            queue_name='process-action',
            payload=expected_payload1,
            target='default'),
        mock.call(
            queue_name='process-action',
            payload=expected_payload2,
            target='default')
    ]
    mock_taskqueueadd.assert_has_calls(expected_calls)

  @mock.patch('__main__.events.get_all_event_action_mappings')
  def test_get_actions_for_event(self, mock_getalleventmappings):
    """Tests simple get_actions_for_event function."""

    # No Event-Action mappings.
    mock_getalleventmappings.return_value = {}
    self.assertRaises(events.NoEventsError, events.get_actions_for_event, 'foo')

    mock_getalleventmappings.return_value = TEST_EVENT_MAPPINGS
    self.assertEqual(
        events.get_actions_for_event('event2'), ['action3', 'action4'])

  def test_get_all_event_action_mappings_existing(self):
    """Tests get_all_event_action_mappings when they're in memcache."""
    memcache.set(key='event_action_mappings', value=TEST_EVENT_MAPPINGS)
    self.assertDictEqual(
        events.get_all_event_action_mappings(), TEST_EVENT_MAPPINGS)

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
