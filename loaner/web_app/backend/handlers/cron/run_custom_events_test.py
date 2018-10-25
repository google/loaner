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

"""Tests for backend.handlers.cron.run_custom_events."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import datetime
import logging

import mock

from loaner.web_app.backend.clients import directory  # pylint: disable=unused-import
from loaner.web_app.backend.lib import events
from loaner.web_app.backend.models import device_model
from loaner.web_app.backend.models import event_models
from loaner.web_app.backend.models import shelf_model
from loaner.web_app.backend.testing import handlertest
from loaner.web_app.backend.testing import loanertest

_NOW = datetime.datetime.utcnow()
_THREE_DAYS_AGO_DELTA = event_models.create_timedelta(-3, 'd')


class RunCustomEventsHandlerTest(handlertest.HandlerTestCase):
  """Test the RunCustomEventsHandler."""

  @mock.patch('__main__.directory.DirectoryApiClient', autospec=True)
  def setup_devices(self, mock_directoryclass):
    mock_directoryclient = mock_directoryclass.return_value
    mock_directoryclient.get_chrome_device_by_serial.side_effect = [
        loanertest.TEST_DIR_DEVICE1, loanertest.TEST_DIR_DEVICE2
    ]
    mock_directoryclient.move_chrome_device_org_unit.side_effect = [
        loanertest.TEST_DIR_DEVICE_DEFAULT, loanertest.TEST_DIR_DEVICE2
    ]
    self.device1 = device_model.Device.enroll(
        loanertest.USER_EMAIL, serial_number='123ABC', asset_tag='123456')
    self.device2 = device_model.Device.enroll(
        loanertest.USER_EMAIL, serial_number='654321', asset_tag='789012')

  def setup_shelves(self):
    self.shelf1 = shelf_model.Shelf.enroll(
        'test@{}'.format(loanertest.USER_DOMAIN), 'US-NYC', 16,
        'Statue of Liberty', 40.6892534, -74.0466891, 1.0,
        loanertest.USER_EMAIL)
    self.shelf2 = shelf_model.Shelf.enroll(
        'test@{}'.format(loanertest.USER_DOMAIN), 'US-CAM', 24, 'Freedom Trail',
        40.6892534, -74.0466891, 1.0, loanertest.USER_EMAIL)

  def setup_events(self):
    self.device_event = event_models.CustomEvent.create('device_event')
    self.device_event.description = 'This is the device event.'
    self.device_event.model = 'Device'
    self.device_event.conditions = [
        event_models.CustomEventCondition(
            name='last_known_healthy', opsymbol='<',
            value=_THREE_DAYS_AGO_DELTA),
        event_models.CustomEventCondition(
            name='locked', opsymbol='=', value=False)
    ]
    self.device_event.actions = ['DO_THING1', 'DO_THING2', 'DO_THING3']
    self.device_event.put()

    self.shelf_event1 = event_models.CustomEvent.create('shelf_event_1')
    self.shelf_event1.description = 'This is the first shelf event.'
    self.shelf_event1.model = 'Shelf'
    self.shelf_event1.conditions = [
        event_models.CustomEventCondition(
            name='last_audit_time', opsymbol='<', value=_THREE_DAYS_AGO_DELTA),
        event_models.CustomEventCondition(
            name='enabled', opsymbol='=', value=True)
    ]
    self.shelf_event1.actions = ['DO_THING4', 'DO_THING5', 'DO_THING6']
    self.shelf_event1.put()

    self.shelf_event2 = event_models.CustomEvent.create('shelf_event_2')
    self.shelf_event2.description = 'This is the second shelf event.'
    self.shelf_event2.model = 'Shelf'
    self.shelf_event2.conditions = [
        event_models.CustomEventCondition(
            name='last_audit_time', opsymbol='<', value=_THREE_DAYS_AGO_DELTA),
        event_models.CustomEventCondition(
            name='enabled', opsymbol='=', value=True),
        event_models.CustomEventCondition(
            name='capacity', opsymbol='=', value=24),
    ]
    self.shelf_event2.actions = ['DO_THING7', 'DO_THING8', 'DO_THING9']
    self.shelf_event2.put()

  def test_no_events(self):
    """Test handler with no events, no entities."""
    response = self.testapp.get(r'/_cron/run_custom_events')

    self.assertEqual(response.status_int, 200)
    self.assertFalse(self.testbed.mock_raiseevent.called)

  def test_events_no_entities(self):
    """Tests with events, no entities in datastore."""
    self.setup_events()
    response = self.testapp.get(r'/_cron/run_custom_events')

    self.assertEqual(response.status_int, 200)
    self.assertFalse(self.testbed.mock_raiseevent.called)

  def test_events_devices_and_shelves(self):
    """Tests with events, one returns one Device, other many Shelves."""
    self.setup_events()
    self.setup_devices()  # pylint: disable=no-value-for-parameter
    self.setup_shelves()
    self.device1.last_known_healthy = _NOW - datetime.timedelta(days=4)
    self.device1.put()
    self.device2.last_known_healthy = _NOW - datetime.timedelta(days=2)
    self.device2.put()

    # Will trigger one shelf rule
    self.shelf1.last_audit_time = _NOW - datetime.timedelta(days=4)
    self.shelf1.put()
    # Will trigger both shelf rules because capacity=24
    self.shelf2.last_audit_time = _NOW - datetime.timedelta(days=4)
    self.shelf2.put()

    self.testbed.mock_raiseevent.reset_mock()

    response = self.testapp.get(r'/_cron/run_custom_events')

    self.assertEqual(response.status_int, 200)
    self.assertTrue(self.testbed.mock_raiseevent.called)
    expected_calls = [
        mock.call(event_name='device_event', device=self.device1, shelf=None),
        mock.call(event_name='shelf_event_1', device=None, shelf=self.shelf1),
        mock.call(event_name='shelf_event_1', device=None, shelf=self.shelf2),
        mock.call(event_name='shelf_event_2', device=None, shelf=self.shelf2),
    ]
    for call in expected_calls:
      self.assertIn(call, self.testbed.mock_raiseevent.mock_calls)
    self.assertEqual(
        len(self.testbed.mock_raiseevent.mock_calls), len(expected_calls))

  @mock.patch.object(logging, 'error', autospec=True)
  def test_events_error(self, mock_logging):
    """Tests that error is caught when EventActionsError occurs."""
    self.setup_events()
    self.setup_shelves()
    self.shelf1.last_audit_time = _NOW - datetime.timedelta(days=4)
    self.shelf1.put()
    self.testbed.mock_raiseevent.side_effect = events.EventActionsError
    self.testapp.get(r'/_cron/run_custom_events')
    self.assertEqual(mock_logging.call_count, 1)


if __name__ == '__main__':
  handlertest.main()
