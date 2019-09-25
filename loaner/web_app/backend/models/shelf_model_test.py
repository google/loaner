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

"""Tests for backend.models.shelf_model."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import datetime

from absl.testing import parameterized

import freezegun
import mock

from google.appengine.api import datastore_errors
from google.appengine.api import search
from google.appengine.ext import ndb

from loaner.web_app import constants
from loaner.web_app.backend.lib import events
from loaner.web_app.backend.models import config_model
from loaner.web_app.backend.models import shelf_model
from loaner.web_app.backend.testing import loanertest


class ShelfModelTest(loanertest.EndpointsTestCase, parameterized.TestCase):
  """Tests for the Shelf class."""

  def setUp(self):
    super(ShelfModelTest, self).setUp()
    self.original_location = 'US-NYC'
    self.original_friendly_name = 'NYC office'
    self.original_capacity = 18
    self.test_shelf = shelf_model.Shelf(
        enabled=True,
        friendly_name=self.original_friendly_name,
        location=self.original_location,
        capacity=self.original_capacity,
        audit_notification_enabled=True).put().get()

  def test_get_search_index(self):
    self.assertIsInstance(shelf_model.Shelf.get_index(), search.Index)

  @parameterized.parameters((-1,), (0,))
  def test_validate_capacity(self, capacity):
    """Test that validate capacity raises db.BadValueError for less than 1."""
    with self.assertRaisesWithLiteralMatch(
        datastore_errors.BadValueError, shelf_model._NEGATIVE_CAPACITY_MSG):
      shelf_model._validate_capacity('capacity', capacity)

  def create_shelf_list(self):
    """Convenience function to create extra shelves to test listing."""
    self.shelf2 = shelf_model.Shelf(
        enabled=True,
        location='US-NYC2',
        capacity=20).put().get()
    self.shelf3 = shelf_model.Shelf(
        enabled=False,
        location='US-NYC3',
        capacity=30).put().get()
    self.shelf4 = shelf_model.Shelf(
        enabled=False,
        location='US-NYC4',
        capacity=40).put().get()

  def test_audited_property_false(self):
    """Test that the audited property is False outside the interval."""
    now = datetime.datetime.utcnow()
    config_model.Config.set('audit_interval', 48)
    with freezegun.freeze_time(now):
      self.test_shelf.last_audit_time = now - datetime.timedelta(hours=49)
      shelf_key = self.test_shelf.put()
      retrieved_shelf = shelf_model.Shelf.get_by_id(shelf_key.id())
      self.assertFalse(retrieved_shelf.audited)

  def test_audited_property_true(self):
    """Test that the audited property is True inside the interval."""
    now = datetime.datetime.utcnow()
    config_model.Config.set('audit_interval', 48)
    with freezegun.freeze_time(now):
      self.test_shelf.last_audit_time = now - datetime.timedelta(hours=47)
      shelf_key = self.test_shelf.put()
      retrieved_shelf = shelf_model.Shelf.get_by_id(shelf_key.id())
      self.assertTrue(retrieved_shelf.audited)

  @mock.patch.object(shelf_model.Shelf, 'to_document', autospec=True)
  def test_identifier(self, mock_to_document):
    """Test the identifier property."""
    # Name is friendly name.
    self.assertEqual(self.test_shelf.identifier, self.original_friendly_name)

    # Name is location.
    self.test_shelf.friendly_name = None
    shelf_key = self.test_shelf.put()
    assert mock_to_document.call_count == 1
    retrieved_shelf = shelf_model.Shelf.get_by_id(shelf_key.id())
    self.assertEqual(retrieved_shelf.identifier, self.original_location)

  @mock.patch.object(shelf_model.Shelf, 'stream_to_bq', autospec=True)
  @mock.patch.object(shelf_model, 'logging', autospec=True)
  def test_enroll_new_shelf(self, mock_logging, mock_stream):
    """Test enrolling a new shelf."""
    new_location = 'US-NYC2'
    new_capacity = 16
    new_friendly_name = 'Statue of Liberty'
    lat = 40.6892534
    lon = -74.0466891
    new_shelf = shelf_model.Shelf.enroll(
        loanertest.USER_EMAIL, new_location, new_capacity, new_friendly_name,
        lat, lon, 1.0, loanertest.USER_EMAIL)

    self.assertEqual(new_shelf.location, new_location)
    self.assertEqual(new_shelf.capacity, new_capacity)
    self.assertEqual(new_shelf.friendly_name, new_friendly_name)
    self.assertEqual(new_shelf.lat_long, ndb.GeoPt(lat, lon))
    self.assertEqual(new_shelf.latitude, lat)
    self.assertEqual(new_shelf.longitude, lon)
    mock_logging.info.assert_called_once_with(
        shelf_model._CREATE_NEW_SHELF_MSG, new_shelf.identifier)
    mock_stream.assert_called_once_with(
        new_shelf, loanertest.USER_EMAIL,
        shelf_model._ENROLL_MSG % new_shelf.identifier)
    self.testbed.mock_raiseevent.assert_called_once_with(
        'shelf_enroll', shelf=new_shelf)

  @mock.patch.object(shelf_model.Shelf, 'stream_to_bq', autospec=True)
  @mock.patch.object(shelf_model, 'logging', autospec=True)
  def test_enroll_new_shelf_no_lat_long_event_error(
      self, mock_logging, mock_stream):
    """Test enrolling a new shelf without latitude and longitude."""
    self.testbed.mock_raiseevent.side_effect = events.EventActionsError
    new_location = 'US-NYC2'
    new_capacity = 16
    new_friendly_name = 'Statue of Liberty'
    new_shelf = shelf_model.Shelf.enroll(
        loanertest.USER_EMAIL, new_location, new_capacity, new_friendly_name)

    self.assertEqual(new_shelf.location, new_location)
    self.assertEqual(new_shelf.capacity, new_capacity)
    self.assertEqual(new_shelf.friendly_name, new_friendly_name)
    self.assertIsNone(new_shelf.lat_long)
    self.assertIsNone(new_shelf.latitude)
    self.assertIsNone(new_shelf.longitude)
    mock_logging.info.assert_called_once_with(
        shelf_model._CREATE_NEW_SHELF_MSG, new_shelf.identifier)
    mock_stream.assert_called_once_with(
        new_shelf, loanertest.USER_EMAIL,
        shelf_model._ENROLL_MSG % new_shelf.identifier)
    self.assertEqual(mock_logging.error.call_count, 1)
    self.testbed.mock_raiseevent.assert_called_once_with(
        'shelf_enroll', shelf=new_shelf)

  @mock.patch.object(shelf_model.Shelf, 'stream_to_bq', autospec=True)
  @mock.patch.object(shelf_model, 'logging', autospec=True)
  def test_enroll_shelf_exists(self, mock_logging, mock_stream):
    """Test enrolling an existing shelf reactivates the shelf."""
    new_capacity = 14
    lat = 40.6892534
    lon = -74.0466891
    self.test_shelf.enabled = False
    self.test_shelf.put()
    reactivated_shelf = shelf_model.Shelf.enroll(
        user_email=loanertest.USER_EMAIL,
        location=self.original_location,
        capacity=new_capacity, latitude=lat, longitude=lon)

    self.assertEqual(self.test_shelf.key, reactivated_shelf.key)
    self.assertEqual(new_capacity, reactivated_shelf.capacity)
    self.assertEqual(reactivated_shelf.lat_long, ndb.GeoPt(lat, lon))
    mock_logging.info.assert_called_once_with(
        shelf_model._REACTIVATE_MSG, self.test_shelf.identifier)
    mock_stream.assert_called_once_with(
        reactivated_shelf, loanertest.USER_EMAIL,
        shelf_model._ENROLL_MSG % reactivated_shelf.identifier)
    self.testbed.mock_raiseevent.assert_called_once_with(
        'shelf_enroll', shelf=reactivated_shelf)

  def test_enroll_latitude_no_longitude(self):
    """Test that enroll requires both lat and long, raises EnrollmentError."""
    with self.assertRaisesRegexp(
        shelf_model.EnrollmentError,
        shelf_model._LAT_LONG_MSG):
      shelf_model.Shelf.enroll(
          loanertest.USER_EMAIL, self.original_location, self.original_capacity,
          self.original_friendly_name, 40.6892534)

  def test_get_with_friendly_name(self):
    """Test the get method with a friendly_name provided."""
    self.assertEqual(
        self.test_shelf, shelf_model.Shelf.get(
            friendly_name=self.original_friendly_name))

  def test_get_with_location(self):
    """Test the get method with a location provided."""
    self.assertEqual(
        self.test_shelf, shelf_model.Shelf.get(location=self.original_location))

  def test_get_with_both(self):
    """Test the get method with a location and friendly_name provided."""
    self.assertEqual(
        self.test_shelf, shelf_model.Shelf.get(
            location=self.original_location,
            friendly_name=self.original_friendly_name))

  @mock.patch.object(shelf_model.Shelf, 'stream_to_bq', autospec=True)
  def test_edit(self, mock_stream):
    """Test that a shelf edit changes the appropriate properties."""
    new_capacity = 10
    new_friendly_name = 'NYC is the best!'
    self.test_shelf.edit(
        user_email=loanertest.USER_EMAIL, capacity=new_capacity,
        friendly_name=new_friendly_name)

    retrieved_shelf = self.test_shelf.key.get()

    self.assertEqual(retrieved_shelf.capacity, new_capacity)
    self.assertEqual(retrieved_shelf.friendly_name, new_friendly_name)
    mock_stream.assert_called_once_with(
        retrieved_shelf, loanertest.USER_EMAIL,
        shelf_model._EDIT_MSG % retrieved_shelf.identifier)

  @mock.patch.object(shelf_model.Shelf, 'stream_to_bq', autospec=True)
  @mock.patch.object(shelf_model, 'logging', autospec=True)
  def test_audit(self, mock_logging, mock_stream):
    """Test that an audit updates the appropriate properties."""
    self.testbed.mock_raiseevent.side_effect = events.EventActionsError
    test_num_of_devices = '10'
    self.test_shelf.audit(loanertest.USER_EMAIL, test_num_of_devices)
    retrieved_shelf = self.test_shelf.key.get()
    self.assertFalse(retrieved_shelf.audit_requested)
    mock_logging.info.assert_called_once_with(
        shelf_model._AUDIT_MSG, self.test_shelf.identifier, test_num_of_devices)
    mock_stream.assert_called_once_with(
        self.test_shelf, loanertest.USER_EMAIL,
        shelf_model._AUDIT_MSG % (
            self.test_shelf.identifier, test_num_of_devices))
    self.assertEqual(mock_logging.error.call_count, 1)
    self.testbed.mock_raiseevent.assert_called_once_with(
        'shelf_audited', shelf=self.test_shelf)

  @mock.patch.object(shelf_model.Shelf, 'stream_to_bq', autospec=True)
  @mock.patch.object(shelf_model, 'logging', autospec=True)
  def test_request_audit(self, mock_logging, mock_stream):
    """Test that an audit request occurrs."""
    self.test_shelf.request_audit()
    retrieved_shelf = self.test_shelf.key.get()
    self.assertTrue(retrieved_shelf.audit_requested)
    mock_logging.info.assert_called_once_with(
        shelf_model._AUDIT_REQUEST_MSG, self.test_shelf.identifier)
    mock_stream.assert_called_once_with(
        self.test_shelf, constants.DEFAULT_ACTING_USER,
        shelf_model._AUDIT_REQUEST_MSG % self.test_shelf.identifier)

  @mock.patch.object(shelf_model.Shelf, 'stream_to_bq', autospec=True)
  @mock.patch.object(shelf_model, 'logging', autospec=True)
  def test_enable(self, mock_logging, mock_stream):
    """Test the enabling of a shelf."""
    self.test_shelf.enabled = False
    shelf_key = self.test_shelf.put()
    retrieved_shelf = shelf_key.get()
    # Ensure that the shelf is now disabled
    self.assertFalse(retrieved_shelf.enabled)
    self.test_shelf.enable(loanertest.USER_EMAIL)
    retrieved_shelf = shelf_key.get()
    # Ensure that the shelf is now re-enabled
    self.assertTrue(retrieved_shelf.enabled)
    mock_logging.info.assert_called_once_with(
        shelf_model._ENABLE_MSG, self.test_shelf.identifier)
    mock_stream.assert_called_once_with(
        self.test_shelf, loanertest.USER_EMAIL,
        shelf_model._ENABLE_MSG % self.test_shelf.identifier)

  @mock.patch.object(shelf_model.Shelf, 'stream_to_bq', autospec=True)
  @mock.patch.object(shelf_model, 'logging', autospec=True)
  def test_disable(self, mock_logging, mock_stream):
    """Test the disabling of a shelf."""
    self.testbed.mock_raiseevent.side_effect = events.EventActionsError
    self.test_shelf.disable(loanertest.USER_EMAIL)
    retrieved_shelf = self.test_shelf.key.get()
    self.assertFalse(retrieved_shelf.enabled)
    mock_logging.info.assert_called_once_with(
        shelf_model._DISABLE_MSG, self.test_shelf.identifier)
    mock_stream.assert_called_once_with(
        self.test_shelf, loanertest.USER_EMAIL,
        shelf_model._DISABLE_MSG % self.test_shelf.identifier)
    self.assertEqual(mock_logging.error.call_count, 1)
    self.testbed.mock_raiseevent.assert_called_once_with(
        'shelf_disable', shelf=self.test_shelf)


if __name__ == '__main__':
  loanertest.main()
