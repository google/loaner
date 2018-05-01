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

from loaner.web_app.backend.api.messages import device_message
from loaner.web_app.backend.api.messages import shelf_messages
from loaner.web_app.backend.lib import api_utils
from loaner.web_app.backend.models import device_model
from loaner.web_app.backend.models import shelf_model
from loaner.web_app.backend.testing import loanertest


class ApiUtilsTest(parameterized.TestCase, loanertest.TestCase):

  @parameterized.parameters(
      (1, datetime.datetime(year=2018, month=1, day=1), 2),
      (3, datetime.datetime(year=2017, month=4, day=2), None),
      (5, None, 6),
  )
  def test_build_reminder_message(self, test_level, test_datetime, test_count):
    """Test the construction of a reminder message from a reminder entity."""
    test_reminder = device_model.Reminder(
        level=test_level, time=test_datetime, count=test_count).put().get()
    expected_message = device_message.Reminder(
        level=test_level, time=test_datetime, count=test_count)
    returned_message = api_utils.build_reminder_message(test_reminder)
    self.assertEqual(returned_message, expected_message)

  def test_build_reminder_message_no_reminder(self):
    """Test that no reminder provided returns None."""
    self.assertIsNone(api_utils.build_reminder_message(None))

  def test_build_shelf_message(self):
    """Test the construction of a shelf message from a shelf entitiy."""
    test_shelf = shelf_model.Shelf(
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

    expected_message = shelf_messages.Shelf(
        shelf_request=shelf_messages.ShelfRequest(
            location='test_location', urlsafe_key=test_shelf.key.urlsafe()),
        enabled=True,
        friendly_name='test_friendly_name',
        location='test_location',
        latitude=10.10,
        longitude=20.20,
        altitude=1.1,
        capacity=10,
        audit_notification_enabled=False,
        audit_requested=True,
        responsible_for_audit='test_group',
        last_audit_time=datetime.datetime(year=2018, month=1, day=1),
        last_audit_by='test_auditer')

    returned_message = api_utils.build_shelf_message(test_shelf)
    self.assertEqual(expected_message, returned_message)

  def test_build_shelf_message_not_found_error(self):
    """Test the failure to build a shelf message for an unknown shelf."""
    with self.assertRaises(endpoints.NotFoundException):
      api_utils.build_shelf_message(shelf_model.Shelf())

  def test_to_dict(self):
    """Test that a dictionary is build from a ProtoRPC message."""
    message = shelf_messages.Shelf(
        location='NY', capacity=50, friendly_name='The_Big_Apple',
        audit_requested=False, responsible_for_audit='daredevils',
        last_audit_by=loanertest.USER_EMAIL, enabled=True)
    expected_dict = {
        'location': 'NY', 'capacity': 50, 'friendly_name': 'The_Big_Apple',
        'audit_requested': False, 'responsible_for_audit': 'daredevils',
        'last_audit_by': loanertest.USER_EMAIL, 'enabled': True}
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
