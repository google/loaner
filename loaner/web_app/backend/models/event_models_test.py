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

"""Tests for backend.models.event_models."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import datetime
from absl import logging
import mock

from google.appengine.api import datastore_errors
from google.appengine.ext import ndb

from loaner.web_app.backend.clients import directory
from loaner.web_app.backend.models import device_model
from loaner.web_app.backend.models import event_models
from loaner.web_app.backend.models import shelf_model
from loaner.web_app.backend.testing import loanertest

_NOW = datetime.datetime.utcnow()
_THREE_DAYS_AGO_DELTA = event_models.create_timedelta(-3, 'd')


class CoreEventTest(loanertest.TestCase):
  """Tests for CoreEvent class."""

  def test_core_event(self):
    self.assertEqual(event_models.CoreEvent.get('foo'), None)

    test_event = event_models.CoreEvent.create(
        'test_core_event', 'Happens when a thing has occurred.')
    test_event.actions = ['do_thing1', 'do_thing2', 'do_thing3']
    test_event.put()

    fetched_event = event_models.CoreEvent.get('test_core_event')
    self.assertEqual(test_event, fetched_event)

  def test_create_existing(self):
    existing_event = event_models.CoreEvent.create('test_existing_core_event')
    existing_event.put()

    self.assertRaises(
        event_models.ExistingEventError,
        event_models.CoreEvent.create, 'test_existing_core_event')

  def test_create_type(self):
    self.assertRaises(TypeError, event_models.CoreEvent.create, 2)


class CustomEventTest(loanertest.TestCase):
  """Tests for CustomEvent class."""

  @mock.patch.object(directory, 'DirectoryApiClient', autospec=True)
  def setup_devices(self, mock_directoryclass):
    mock_directoryclient = mock_directoryclass.return_value
    mock_directoryclient.get_chrome_device_by_serial.side_effect = [
        loanertest.TEST_DIR_DEVICE1, loanertest.TEST_DIR_DEVICE2
    ]
    mock_directoryclient.move_chrome_device_org_unit.side_effect = [
        loanertest.TEST_DIR_DEVICE_DEFAULT, loanertest.TEST_DIR_DEVICE2
    ]
    self.device1 = device_model.Device.enroll(
        user_email=loanertest.USER_EMAIL, serial_number='123ABC',
        asset_tag='123456')
    self.device2 = device_model.Device.enroll(
        user_email=loanertest.USER_EMAIL, serial_number='654321',
        asset_tag='789012')

  def setup_shelves(self):
    self.shelf1 = shelf_model.Shelf.enroll(
        'test@{}'.format(loanertest.USER_DOMAIN), 'US-NYC', 16,
        'Statue of Liberty', 40.6892534, -74.0466891, 1.0,
        loanertest.USER_EMAIL)
    self.shelf2 = shelf_model.Shelf.enroll(
        'test@{}'.format(loanertest.USER_DOMAIN), 'US-CAM', 24, 'Freedom Trail',
        40.6892534, -74.0466891, 1.0, loanertest.USER_EMAIL)

  def setup_events(self):
    """Creates test events."""
    self.device_event = event_models.CustomEvent.create('device_event')
    self.device_event.description = 'This is the device event.'
    self.device_event.model = 'Device'
    self.device_event.conditions = [
        event_models.CustomEventCondition(
            name='due_date', opsymbol='<', value=event_models.create_timedelta(
                1, 'd')),
        event_models.CustomEventCondition(
            name='locked', opsymbol='=', value=False),
        event_models.CustomEventCondition(
            name='lost', opsymbol='=', value=False)
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

  def test_create_and_get_all(self):
    self.setup_events()
    self.assertLen(event_models.CustomEvent.get_all_enabled(), 3)

  def test_invalid_model(self):
    """Tests that Custom Events can only apply to Device and Shelf models."""
    self.assertRaises(
        datastore_errors.BadValueError, event_models.CustomEvent, model='User')

  def test_create_timedelta(self):
    self.assertRaises(
        event_models.BadTimeUnitError,
        event_models.create_timedelta, 5, 'y')  # No years.
    self.assertEqual(
        event_models.create_timedelta(2, 'h'),
        datetime.timedelta(seconds=2*3600))
    self.assertEqual(
        event_models.create_timedelta(3, 'd'),
        datetime.timedelta(seconds=3*86400))
    self.assertEqual(
        event_models.create_timedelta(4, 'w'),
        datetime.timedelta(seconds=4*604800))

  def test_build_query_components(self):
    """Tests building a simple query and one with two inequality filters."""
    self.setup_events()

    query_components1 = self.device_event._build_query_components()
    self.assertEqual(query_components1['less_than_properties'], ['due_date'])
    self.assertEqual(query_components1['extra_inequality_conditions'], [])
    self.assertLen(
        query_components1['query'].filters._ConjunctionNode__nodes, 3)

    # Add another inequality filter that uses <. Propery name hould be added to
    # less_than_properties, condition should be added to
    # extra_inequality_filters, and the core query should be identical.
    self.device_event.conditions.append(
        event_models.CustomEventCondition(
            name='last_heartbeat', opsymbol='<',
            value=event_models.create_timedelta(-5, 'd')))
    query_components2 = self.device_event._build_query_components()
    self.assertListEqual(
        query_components2['less_than_properties'],
        ['due_date', 'last_heartbeat'])
    self.assertEqual(
        query_components2['extra_inequality_conditions'],
        [self.device_event.conditions[3]])
    self.assertLen(
        query_components2['query'].filters._ConjunctionNode__nodes, 3)

  @mock.patch.object(ndb, 'Query', autospec=True)
  @mock.patch.object(logging, 'error', autospec=True)
  def test_get_matching_entities_bad_query(
      self, mock_logerror, mock_queryclass):
    """Tests with a bad query."""
    mock_query = mock_queryclass.return_value
    mock_query.fetch.side_effect = datastore_errors.BadArgumentError
    self.setup_events()

    self.assertListEqual(list(self.device_event.get_matching_entities()), [])
    self.assertEqual(mock_logerror.call_count, 1)

  def test_get_matching_entities_with_events_devices(self):
    """Tests with two Devices, only one of which matches."""
    self.setup_events()
    self.setup_devices()  # pylint: disable=no-value-for-parameter
    self.device1.due_date = _NOW + datetime.timedelta(days=2)
    self.device1.put()
    self.device2.due_date = _NOW + datetime.timedelta(hours=1)
    self.device2.put()

    self.assertListEqual(
        list(self.device_event.get_matching_entities()),
        [self.device2])

  def test_get_matching_entities_when_one_has_null_less_than_value(self):
    """Tests that an event with a < condition drops entities with null value."""
    self.setup_events()
    self.setup_shelves()

    # Null values cause the shelves to be dropped, with no events raised.
    self.shelf1.last_audit_time = None
    self.shelf1.put()
    self.shelf2.last_audit_time = None
    self.shelf2.put()
    self.assertListEqual(list(self.shelf_event1.get_matching_entities()), [])

    # Restoring a value that matches the condition returns it.
    self.shelf1.last_audit_time = _NOW - datetime.timedelta(days=5)
    self.shelf1.put()
    self.assertListEqual(
        list(self.shelf_event1.get_matching_entities()), [self.shelf1])


class ShelfAuditEventTest(loanertest.TestCase):
  """Tests for ShelfAuditEvent class."""

  def test_shelf_audit_event(self):
    test_event = event_models.ShelfAuditEvent.create(
        actions=['do_thing1', 'do_thing2'])
    self.assertListEqual(
        test_event.actions, ['do_thing1', 'do_thing2', 'request_shelf_audit'])


class ReminderEventTest(loanertest.TestCase):
  """Tests for ReminderEvent class."""

  def test_get_and_put(self):
    self.assertEqual(event_models.ReminderEvent.get(0), None)
    test_event = event_models.ReminderEvent.create(0)

    self.assertEqual(test_event.level, 0)  # Tests @property taken from ID.
    self.assertEqual(test_event.model, 'Device')
    self.assertEqual(test_event.name, 'reminder_level_0')
    self.assertEqual(
        event_models.ReminderEvent.make_name(0), 'reminder_level_0')

    test_event.description = 'Device is due soon.'
    tomorrow = event_models.create_timedelta(1, 'd')
    test_event.conditions = [
        event_models.CustomEventCondition(
            name='due_date', opsymbol='<', value=tomorrow),
        event_models.CustomEventCondition(
            name='locked', opsymbol='=', value=False),
        event_models.CustomEventCondition(
            name='lost', opsymbol='=', value=False)
    ]
    test_event.template = 'reminder_due'
    test_event.put()

    self.assertEqual(test_event, event_models.ReminderEvent.get(0))

  def test_create_existing(self):
    existing_event = event_models.ReminderEvent.create(0)
    existing_event.put()

    self.assertRaises(
        event_models.ExistingEventError, event_models.ReminderEvent.create, 0)

  def test_create_type(self):
    self.assertRaises(TypeError, event_models.ReminderEvent.create, '0')

  def test_get_all(self):
    test_event = event_models.ReminderEvent.create(0)
    test_event.put()

    self.assertTrue(test_event.key)
    self.assertIn(test_event, event_models.ReminderEvent.get_all_enabled())


class CustomEventConditionTest(loanertest.TestCase):
  """Tests for the CustomEventCondition class."""

  def test_get_filter(self):
    condition = event_models.CustomEventCondition(
        name='foo', opsymbol='<', value=42)
    test_filter = condition.get_filter()

    self.assertIsInstance(test_filter, ndb.query.FilterNode)
    self.assertEqual(test_filter._FilterNode__name, condition.name)
    self.assertEqual(test_filter._FilterNode__opsymbol, condition.opsymbol)
    self.assertEqual(test_filter._FilterNode__value, condition.value)

  def test_match(self):
    """Tests the match function in every possible way."""
    test_shelf = shelf_model.Shelf.enroll(
        'test@{}'.format(loanertest.USER_DOMAIN), 'US-NYC', 16,
        'Statue of Liberty', 40.6892534, -74.0466891, 1.0,
        loanertest.USER_EMAIL)

    self.assertFalse(event_models.CustomEventCondition(  # 16 !< 10.
        name='capacity', opsymbol='<', value=10).match(test_shelf))

    self.assertFalse(event_models.CustomEventCondition(  # None !< timedelta.
        name='last_audit_time', opsymbol='<', value='-3d').match(test_shelf))

    self.assertTrue(event_models.CustomEventCondition(  # 16 <= 16.
        name='capacity', opsymbol='<=', value=16).match(test_shelf))

    self.assertFalse(event_models.CustomEventCondition(  # None !<= timedelta.
        name='last_audit_time', opsymbol='<=', value='-3d').match(test_shelf))

    self.assertTrue(event_models.CustomEventCondition(  # 16 == 16.
        name='capacity', opsymbol='==', value=16).match(test_shelf))

    self.assertTrue(event_models.CustomEventCondition(  # 16 != 10.
        name='capacity', opsymbol='!=', value=10).match(test_shelf))

    self.assertTrue(event_models.CustomEventCondition(  # 16 > 10.
        name='capacity', opsymbol='>', value=10).match(test_shelf))

    self.assertFalse(event_models.CustomEventCondition(  # 16 !>= 24.
        name='capacity', opsymbol='>=', value=24).match(test_shelf))


if __name__ == '__main__':
  loanertest.main()
