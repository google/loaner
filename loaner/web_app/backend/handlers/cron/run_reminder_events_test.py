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

"""Tests for backend.handlers.cron.run_reminder_events."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import datetime

import mock

from google.appengine.ext import ndb  # pylint: disable=unused-import

from loaner.web_app.backend.clients import directory  # pylint: disable=unused-import
from loaner.web_app.backend.handlers.cron import run_reminder_events
from loaner.web_app.backend.lib import events  # pylint: disable=unused-import
from loaner.web_app.backend.models import device_model
from loaner.web_app.backend.models import event_models
from loaner.web_app.backend.testing import handlertest
from loaner.web_app.backend.testing import loanertest

_NOW = datetime.datetime.utcnow()


class RunReminderEventsHandlerTest(handlertest.HandlerTestCase):
  """Tests the RunReminderEventsHandler."""

  @mock.patch('__main__.directory.DirectoryApiClient', autospec=True)
  def setup_devices(self, mock_directoryclass):
    mock_directoryclient = mock_directoryclass.return_value
    mock_directoryclient.get_chrome_device_by_serial.side_effect = [
        loanertest.TEST_DIR_DEVICE1, loanertest.TEST_DIR_DEVICE2,
        loanertest.TEST_DIR_DEVICE_DEFAULT
    ]
    mock_directoryclient.move_chrome_device_org_unit.side_effect = [
        loanertest.TEST_DIR_DEVICE1, loanertest.TEST_DIR_DEVICE2,
        loanertest.TEST_DIR_DEVICE_DEFAULT
    ]

    self.device1 = device_model.Device.enroll(
        user_email=loanertest.USER_EMAIL, serial_number='123ABC',
        asset_tag='123456')
    self.device1.assigned_user = loanertest.USER_EMAIL
    self.device1.assigned_date = _NOW - datetime.timedelta(days=7)
    self.device1.put()

    self.device2 = device_model.Device.enroll(
        user_email=loanertest.USER_EMAIL, serial_number='654321',
        asset_tag='789012')
    self.device2.assigned_user = loanertest.SUPER_ADMIN_EMAIL
    self.device2.assigned_date = _NOW - datetime.timedelta(days=5)
    self.device2.put()

    self.device3 = device_model.Device.enroll(
        user_email=loanertest.USER_EMAIL, serial_number='4815162342',
        asset_tag='135790')
    self.device3.assigned_user = loanertest.TECHNICIAN_EMAIL
    self.device3.assigned_date = _NOW - datetime.timedelta(days=1)
    self.device3.put()

  def setup_events(self):
    tomorrow_delta = event_models.create_timedelta(1, 'd')
    self.reminder_due_event = event_models.ReminderEvent.create(0)
    self.reminder_due_event.description = 'Device due in less than one day.'
    self.reminder_due_event.conditions = [
        event_models.CustomEventCondition(
            name='due_date', opsymbol='<', value=tomorrow_delta),
        event_models.CustomEventCondition(
            name='due_date', opsymbol='>', value=datetime.timedelta(seconds=0)),
        event_models.CustomEventCondition(
            name='locked', opsymbol='=', value=False),
        event_models.CustomEventCondition(
            name='lost', opsymbol='=', value=False)
    ]
    self.reminder_due_event.actions = ['DO_THING1', 'DO_THING2', 'DO_THING3']
    self.reminder_due_event.put()

  @mock.patch('__main__.run_reminder_events.logging.error')
  def test_no_events(self, mock_logerror):
    """Tests handler with no events, no entities."""
    response = self.testapp.get(
        r'/_cron/run_reminder_events?find_remindable_devices=true')

    self.assertEqual(response.status_int, 200)
    self.assertFalse(self.testbed.mock_raiseevent.called)
    mock_logerror.assert_called_once_with(
        run_reminder_events._NO_REMINDER_EVENTS_MSG)

  def test_events_no_entities(self):
    """Tests with events, no entities in datastore."""
    self.setup_events()
    response = self.testapp.get(
        r'/_cron/run_reminder_events?find_remindable_devices=true')

    self.assertEqual(response.status_int, 200)
    self.assertFalse(self.testbed.mock_raiseevent.called)

  @mock.patch('__main__.run_reminder_events.logging.info')
  def test_null_due_dates(self, mock_loginfo):
    """Tests with events and devices, but due_date for both devices are null."""
    self.setup_devices()  # pylint: disable=no-value-for-parameter
    tomorrow_delta = event_models.create_timedelta(1, 'd')
    simple_reminder_due_event = event_models.ReminderEvent.create(0)
    simple_reminder_due_event.description = 'Due date-based event.'
    simple_reminder_due_event.conditions = [
        event_models.CustomEventCondition(
            name='due_date', opsymbol='<', value=tomorrow_delta)]
    simple_reminder_due_event.put()
    self.testbed.mock_raiseevent.reset_mock()

    response = self.testapp.get(
        r'/_cron/run_reminder_events?find_remindable_devices=true')

    self.assertEqual(response.status_int, 200)
    retrieved_device1 = self.device1.key.get()
    retrieved_device2 = self.device2.key.get()

    self.assertIsNone(retrieved_device1.next_reminder)
    self.assertIsNone(retrieved_device2.next_reminder)

  @mock.patch('__main__.run_reminder_events.logging.info')
  def test_find_one_due(self, mock_loginfo):
    """Tests with events and devices, one of which is remindable."""
    self.setup_events()
    self.setup_devices()  # pylint: disable=no-value-for-parameter
    self.device1.due_date = _NOW + datetime.timedelta(hours=23)  # Due soon.
    self.device1.put()
    self.device2.due_date = _NOW + datetime.timedelta(days=2)  # Not due soon.
    self.device2.put()
    self.testbed.mock_raiseevent.reset_mock()

    response = self.testapp.get(
        r'/_cron/run_reminder_events?find_remindable_devices=true')

    self.assertEqual(response.status_int, 200)
    retrieved_device1 = self.device1.key.get()
    mock_loginfo.assert_any_call(
        run_reminder_events._DEVICE_SET_REMINDER_MSG, self.device1.identifier,
        0, str(retrieved_device1.next_reminder.time))
    self.assertFalse(self.testbed.mock_raiseevent.called)

    self.assertFalse(retrieved_device1.last_reminder)
    self.assertTrue(retrieved_device1.next_reminder.time)
    self.assertEqual(retrieved_device1.next_reminder.level, 0)

    retrieved_device2 = self.device2.key.get()
    self.assertFalse(retrieved_device2.last_reminder)
    self.assertFalse(retrieved_device2.next_reminder)

    # Device next reminder already set.
    mock_loginfo.reset_mock()
    self.testapp.get(
        r'/_cron/run_reminder_events?find_remindable_devices=true')
    mock_loginfo.assert_any_call(
        run_reminder_events._DEVICE_ALREADY_NOTED_MSG,
        self.device1.identifier, 0)

  @mock.patch('__main__.run_reminder_events.logging.info')
  def test_device_marked_returned(self, mock_loginfo):
    """Tests that a marked returned device is not reminded."""
    self.setup_events()
    self.setup_devices()  # pylint: disable=no-value-for-parameter

    self.device1.due_date = _NOW + datetime.timedelta(hours=23)
    self.device1.next_reminder = device_model.Reminder(
        time=_NOW - datetime.timedelta(minutes=1), level=0)
    self.device1.mark_pending_return_date = datetime.datetime.utcnow()
    self.device1.put()
    self.testbed.mock_raiseevent.reset_mock()

    self.testapp.get(
        r'/_cron/run_reminder_events?find_remindable_devices=true')
    mock_loginfo.assert_any_call(
        run_reminder_events._DEVICE_MARKED_RETURNED_MSG,
        self.device1.identifier, 0)
    self.assertFalse(self.testbed.mock_raiseevent.called)

  @mock.patch('__main__.run_reminder_events.logging.info')
  def test_reminded_too_early_for_repeat(self, mock_loginfo):
    """Tests that a device that was already reminded is still waiting."""
    self.setup_events()
    self.setup_devices()  # pylint: disable=no-value-for-parameter

    # Device reminded an hour ago, and repeats allowed, but it's early yet.
    self.device1.due_date = _NOW + datetime.timedelta(hours=23)
    self.device1.last_reminder = device_model.Reminder(
        time=_NOW - datetime.timedelta(minutes=60), level=0)
    self.device1.put()
    self.reminder_due_event.interval = 1
    self.reminder_due_event.repeat_interval = True
    self.reminder_due_event.put()
    self.testbed.mock_raiseevent.reset_mock()

    self.testapp.get(
        r'/_cron/run_reminder_events?find_remindable_devices=true')
    mock_loginfo.assert_called_with(
        run_reminder_events._DEVICE_REPEAT_WAITING_MSG,
        self.device1.identifier, 0, self.reminder_due_event.repeat_interval)
    self.assertFalse(self.testbed.mock_raiseevent.called)

  @mock.patch.object(run_reminder_events, 'logging')
  def test_remind_one(self, mock_logging):
    """Tests that one device should be reminded."""
    self.setup_events()
    self.setup_devices()  # pylint: disable=no-value-for-parameter

    # Remindable.
    self.device1.due_date = _NOW + datetime.timedelta(hours=23)
    self.device1.next_reminder = device_model.Reminder(
        time=_NOW - datetime.timedelta(minutes=1), level=0)
    self.device1.put()

    # Not yet remindable.
    self.device2.due_date = _NOW + datetime.timedelta(hours=25)
    self.device2.next_reminder = device_model.Reminder(
        time=_NOW + datetime.timedelta(hours=2), level=0)
    self.device1.put()
    self.device2.put()

    self.testbed.mock_raiseevent.reset_mock()
    self.testbed.mock_raiseevent.side_effect = events.EventActionsError(
        'Failed.')

    response = self.testapp.get(
        r'/_cron/run_reminder_events?remind_for_devices=true')

    self.assertEqual(response.status_int, 200)
    mock_logging.info.assert_any_call(
        run_reminder_events._DEVICE_REMINDING_NOW_MSG,
        self.device1.identifier, 0)
    self.assertEqual(mock_logging.error.call_count, 1)
    self.testbed.mock_raiseevent.assert_called_once_with(
        event_name='reminder_level_0', device=self.device1)

  def test_reminded_no_repeat(self):
    """Tests that a device that was already reminded is not done again."""
    self.setup_events()
    self.setup_devices()  # pylint: disable=no-value-for-parameter

    # Device reminded an hour ago, and repeats not allowed.
    self.device1.due_date = _NOW + datetime.timedelta(hours=23)
    self.device1.last_reminder = device_model.Reminder(
        time=_NOW - datetime.timedelta(minutes=60), level=0)
    self.device1.put()

    self.testbed.mock_raiseevent.reset_mock()

    self.testapp.get(
        r'/_cron/run_reminder_events?remind_for_devices=true')
    retrieved_device1 = self.device1.key.get()
    self.assertEqual(retrieved_device1.next_reminder, None)
    self.assertFalse(self.testbed.mock_raiseevent.called)

if __name__ == '__main__':
  handlertest.main()
