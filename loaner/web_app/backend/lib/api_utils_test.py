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

"""Tests for backend.lib.api_utils."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import datetime

from absl.testing import parameterized

from google.appengine.ext import ndb

import endpoints

from loaner.web_app import constants
from loaner.web_app.backend.api.messages import device_messages
from loaner.web_app.backend.api.messages import shelf_messages
from loaner.web_app.backend.lib import api_utils
from loaner.web_app.backend.models import device_model
from loaner.web_app.backend.models import shelf_model
from loaner.web_app.backend.testing import loanertest


class ApiUtilsTest(parameterized.TestCase, loanertest.TestCase):

  def setUp(self):
    super(ApiUtilsTest, self).setUp()
    self.test_shelf_model = shelf_model.Shelf(
        enabled=True,
        friendly_name='test_friendly_name',
        location='test_location',
        lat_long=ndb.GeoPt(10.10, 20.20),
        altitude=1.1,
        capacity=10,
        audit_interval_override=12,
        audit_notification_enabled=False,
        audit_requested=True,
        responsible_for_audit='test_group',
        last_audit_time=datetime.datetime(year=2018, month=1, day=1),
        last_audit_by='test_auditer').put().get()
    self.expected_shelf_message = shelf_messages.Shelf(
        shelf_request=shelf_messages.ShelfRequest(
            location='test_location',
            urlsafe_key=self.test_shelf_model.key.urlsafe()),
        enabled=True,
        friendly_name='test_friendly_name',
        location='test_location',
        identifier='test_friendly_name',
        latitude=10.10,
        longitude=20.20,
        altitude=1.1,
        capacity=10,
        audit_notification_enabled=False,
        audit_requested=True,
        responsible_for_audit='test_group',
        last_audit_time=datetime.datetime(year=2018, month=1, day=1),
        last_audit_by='test_auditer')

  def test_build_device_message_from_model(self):
    """Test the construction of a device message from a device entity."""
    test_device = device_model.Device(
        serial_number='test_serial_value',
        asset_tag='test_asset_tag_value',
        enrolled=True,
        device_model='test model value',
        due_date=datetime.datetime(year=2018, month=1, day=1),
        last_known_healthy=datetime.datetime(year=2018, month=1, day=2),
        shelf=self.test_shelf_model.key,
        assigned_user='user value',
        assignment_date=datetime.datetime(year=2018, month=1, day=3),
        current_ou=constants.ORG_UNIT_DICT['GUEST'],
        ou_changed_date=datetime.datetime(year=2018, month=1, day=4),
        locked=True,
        lost=False,
        mark_pending_return_date=datetime.datetime(year=2018, month=1, day=5),
        chrome_device_id='device id value',
        last_heartbeat=datetime.datetime(year=2018, month=1, day=6),
        damaged=None,
        damaged_reason='Not damaged',
        last_reminder=device_model.Reminder(level=1),
        next_reminder=device_model.Reminder(level=2),
    ).put().get()
    expected_message = device_messages.Device(
        serial_number='test_serial_value',
        asset_tag='test_asset_tag_value',
        identifier='test_asset_tag_value',
        enrolled=True,
        device_model='test model value',
        due_date=datetime.datetime(year=2018, month=1, day=1),
        last_known_healthy=datetime.datetime(year=2018, month=1, day=2),
        shelf=self.expected_shelf_message,
        assigned_user='user value',
        assignment_date=datetime.datetime(year=2018, month=1, day=3),
        current_ou=constants.ORG_UNIT_DICT['GUEST'],
        ou_changed_date=datetime.datetime(year=2018, month=1, day=4),
        locked=True,
        lost=False,
        mark_pending_return_date=datetime.datetime(year=2018, month=1, day=5),
        chrome_device_id='device id value',
        last_heartbeat=datetime.datetime(year=2018, month=1, day=6),
        damaged=None,
        damaged_reason='Not damaged',
        last_reminder=device_messages.Reminder(level=1),
        next_reminder=device_messages.Reminder(level=2),
        guest_permitted=True,
        guest_enabled=True,
        max_extend_date=device_model.calculate_return_dates(
            test_device.assignment_date).max,
        overdue=True,
    )
    actual_message = api_utils.build_device_message_from_model(
        test_device, True)
    self.assertEqual(actual_message, expected_message)

  @parameterized.parameters(
      (1, datetime.datetime(year=2018, month=1, day=1), 2),
      (3, datetime.datetime(year=2017, month=4, day=2), None),
      (5, None, 6),
  )
  def test_build_reminder_message_from_model(
      self, test_level, test_datetime, test_count):
    """Test the construction of a reminder message from a reminder entity."""
    test_reminder = device_model.Reminder(
        level=test_level, time=test_datetime, count=test_count).put().get()
    expected_message = device_messages.Reminder(
        level=test_level, time=test_datetime, count=test_count)
    returned_message = api_utils.build_reminder_message_from_model(
        test_reminder)
    self.assertEqual(returned_message, expected_message)

  def test_build_shelf_message_from_model(self):
    """Test the construction of a shelf message from a shelf entitiy."""
    actual_message = api_utils.build_shelf_message_from_model(
        self.test_shelf_model)
    self.assertEqual(actual_message, self.expected_shelf_message)

  @parameterized.named_parameters(
      {'testcase_name': 'with_lat_long', 'message': shelf_messages.Shelf(
          location='NY', capacity=50, friendly_name='Big_Apple',
          audit_requested=False, responsible_for_audit='daredevils',
          latitude=12.5, longitude=12.5, last_audit_by=loanertest.USER_EMAIL,
          enabled=True), 'expected_dict': {
              'location': 'NY', 'capacity': 50, 'friendly_name': 'Big_Apple',
              'audit_requested': False, 'responsible_for_audit': 'daredevils',
              'lat_long': ndb.GeoPt(12.5, 12.5),
              'last_audit_by': loanertest.USER_EMAIL, 'enabled': True},},
      {'testcase_name': 'without_lat_long', 'message': shelf_messages.Shelf(
          location='NY'), 'expected_dict': {'location': 'NY', 'enabled': True},}
  )
  def test_to_dict(self, message, expected_dict):
    """Test that a dictionary is build from a ProtoRPC message."""
    filters = api_utils.to_dict(message, shelf_model.Shelf)
    self.assertEqual(filters, expected_dict)

  def test_get_ndb_key_not_found(self):
    """Test the get of an ndb.Key, raises endpoints.BadRequestException."""
    with self.assertRaisesRegexp(
        endpoints.BadRequestException,
        api_utils._CORRUPT_KEY_MSG):
      api_utils.get_ndb_key('corruptKey')

  def test_get_datastore_cursor_not_found(self):
    """Test the get of a datastore.Cursor, raises endpoints.BadRequestException.
    """
    with self.assertRaisesRegexp(
        endpoints.BadRequestException,
        api_utils._MALFORMED_PAGE_TOKEN_MSG):
      api_utils.get_datastore_cursor('malformedPageToken')


if __name__ == '__main__':
  loanertest.main()
