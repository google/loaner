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

"""Tests for backend.api.shelf_api."""

import datetime

import mock

from protorpc import message_types

import endpoints

from loaner.web_app.backend.api import root_api  # pylint: disable=unused-import
from loaner.web_app.backend.api import shelf_api
from loaner.web_app.backend.api.messages import shelf_messages
from loaner.web_app.backend.models import device_model
from loaner.web_app.backend.models import shelf_model  # pylint: disable=unused-import
from loaner.web_app.backend.testing import loanertest


class ShelfApiTest(loanertest.EndpointsTestCase):
  """Test for the Shelf API."""

  def setUp(self):
    super(ShelfApiTest, self).setUp()
    self.patcher_directory = mock.patch(
        '__main__.device_model.directory.DirectoryApiClient')
    self.mock_directoryclass = self.patcher_directory.start()
    self.addCleanup(self.patcher_directory.stop)
    self.service = shelf_api.ShelfApi()
    self.login_admin_endpoints_user()
    self.patcher_xsrf = mock.patch(
        '__main__.shelf_api.root_api.Service.check_xsrf_token')
    self.shelf = shelf_model.Shelf.enroll(
        user_email=loanertest.USER_EMAIL, location='NYC', capacity=10,
        friendly_name='GnG', latitude=40.6892534, longitude=-74.0466891,
        altitude=1.0)
    shelf1 = shelf_model.Shelf.enroll(
        user_email=loanertest.USER_EMAIL, location='MTV', capacity=20)
    shelf2 = shelf_model.Shelf.enroll(
        user_email=loanertest.USER_EMAIL, location='SAO', capacity=10)
    self.disabled_shelf = shelf_model.Shelf.enroll(
        user_email=loanertest.USER_EMAIL, location='SVL', capacity=10,
        friendly_name='Bay')
    self.disabled_shelf.disable(loanertest.USER_EMAIL)
    self.shelf_locations = [
        self.shelf.location, shelf1.location, shelf2.location,
        self.disabled_shelf.location]

    self.device1 = device_model.Device(
        serial_number='12345',
        enrolled=True,
        device_model='HP Chromebook 13 G1',
        current_ou='/',
        chrome_device_id='unique_id_1',
        damaged=False,
    ).put()
    self.device2 = device_model.Device(
        serial_number='54321',
        enrolled=True,
        device_model='HP Chromebook 13 G1',
        current_ou='/',
        chrome_device_id='unique_id_2',
        damaged=False,
    ).put()
    self.device3 = device_model.Device(
        serial_number='67890',
        enrolled=True,
        shelf=self.shelf.key,
        device_model='HP Chromebook 13 G1',
        current_ou='/',
        chrome_device_id='unique_id_3',
        damaged=False,
    ).put()
    self.device4 = device_model.Device(
        serial_number='ABC123',
        enrolled=True,
        shelf=self.shelf.key,
        device_model='HP Chromebook 13 G1',
        current_ou='/',
        chrome_device_id='unique_id_4',
        damaged=False,
    ).put()
    self.device_identifiers = [
        self.device1.get().serial_number, self.device2.get().serial_number,
        self.device3.get().serial_number]

  def tearDown(self):
    super(ShelfApiTest, self).tearDown()
    self.service = None

  @mock.patch('__main__.root_api.Service.check_xsrf_token')
  @mock.patch('__main__.shelf_model.Shelf.enroll')
  def test_enroll(self, mock_enroll, mock_xsrf_token):
    """Test Enroll with mock methods."""
    request = shelf_messages.EnrollShelfRequest(
        location='nyc', capacity=100, friendly_name='test', latitude=12.5,
        longitude=12.5, altitude=2.0, responsible_for_audit='precise')
    response = self.service.enroll(request)
    mock_xsrf_token.assert_called_once()
    self.assertIsInstance(response, message_types.VoidMessage)

  def test_enroll_bad_request(self):
    request = shelf_messages.EnrollShelfRequest(capacity=10)
    with self.assertRaisesRegexp(
        shelf_api.endpoints.BadRequestException,
        'Entity has uninitialized properties'):
      self.service.enroll(request)
    request = shelf_messages.EnrollShelfRequest(
        location='nyc', capacity=10, latitude=12.5)
    with self.assertRaisesRegexp(
        shelf_api.endpoints.BadRequestException,
        shelf_model._LAT_LONG_MSG):
      self.service.enroll(request)

  @mock.patch('__main__.root_api.Service.check_xsrf_token')
  def test_get_by_location(self, mock_xsrf_token):
    request = shelf_messages.ShelfRequest(location='NYC')
    response = self.service.get(request)
    mock_xsrf_token.assert_called_once()
    self.assertEqual(self.shelf.location, response.location)
    self.assertEqual(self.shelf.friendly_name, response.friendly_name)

  def test_disable_by_location(self):
    request = shelf_messages.ShelfRequest(location='NYC')
    self.assertTrue(self.shelf.enabled)
    response = self.service.disable(request)
    self.assertFalse(self.shelf.enabled)
    self.assertIsInstance(response, message_types.VoidMessage)

  @mock.patch('__main__.root_api.Service.check_xsrf_token')
  def test_update_using_location(self, mock_xsrf_token):
    request = shelf_messages.UpdateShelfRequest(
        shelf_request=shelf_messages.ShelfRequest(location='NYC'),
        location='NYC-9th')
    response = self.service.update(request)
    mock_xsrf_token.assert_called_once()
    self.assertEqual(self.shelf.location, 'NYC-9th')
    shelf = shelf_model.Shelf.get(friendly_name='GnG')
    self.assertEqual(shelf.location, 'NYC-9th')
    self.assertIsInstance(response, message_types.VoidMessage)

  @mock.patch('__main__.root_api.Service.check_xsrf_token')
  def test_list_shelves(self, mock_xsrf_token):
    request = shelf_messages.Shelf(enabled=True)
    response = self.service.list_shelves(request)
    mock_xsrf_token.assert_called_once()
    self.assertEqual(3, len(response.shelves))

  def test_list_shelves_with_page_token(self):
    request = shelf_messages.Shelf(enabled=True, page_size=1)
    response_shelves = []
    while True:
      response = self.service.list_shelves(request)
      for shelf in response.shelves:
        self.assertTrue(shelf.location in self.shelf_locations)
        response_shelves.append(shelf)
      request = shelf_messages.Shelf(
          enabled=True, page_size=1, page_token=response.page_token)
      if not response.additional_results:
        break
    self.assertEqual(len(response_shelves), 3)

  @mock.patch('__main__.root_api.Service.check_xsrf_token')
  @mock.patch('__main__.shelf_api.logging.info')
  def test_audit_using_shelf_location(self, mock_logging, mock_xsrf_token):
    request = shelf_messages.ShelfAuditRequest(
        shelf_request=shelf_messages.ShelfRequest(location='NYC'),
        device_identifiers=self.device_identifiers)
    response = self.service.audit(request)
    mock_xsrf_token.assert_called_once()
    mock_logging.assert_called()
    for identifier in self.device_identifiers:
      datastore_device = device_model.Device.get(serial_number=identifier)
      self.assertEqual(datastore_device.shelf.get().location, 'NYC')
    self.assertFalse(self.shelf.audit_requested)
    self.assertEqual(self.shelf.last_audit_by, loanertest.SUPER_ADMIN_EMAIL)
    self.assertIsInstance(response, message_types.VoidMessage)

  def test_audit_invlid_device(self):
    request = shelf_messages.ShelfAuditRequest(
        shelf_request=shelf_messages.ShelfRequest(location='NYC'),
        device_identifiers=['Invalid'])
    with self.assertRaisesRegexp(
        endpoints.NotFoundException,
        shelf_api._DEVICE_DOES_NOT_EXIST_MSG % 'Invalid'):
      self.service.audit(request)

  def test_audit_unable_to_move_to_shelf(self):
    self.shelf.capacity = len(device_model.Device.list_devices(
        shelf=self.shelf.key))
    request = shelf_messages.ShelfAuditRequest(
        shelf_request=shelf_messages.ShelfRequest(location=self.shelf.location),
        device_identifiers=self.device_identifiers)
    with self.assertRaises(endpoints.BadRequestException):
      self.service.audit(request)

  @mock.patch('__main__.device_model.Device.list_devices')
  @mock.patch('__main__.shelf_api.get_shelf')
  def test_audit_remove_devices(
      self, mock_get_shelf, mock_model_list_devices):
    shelf = self.device2.get()
    shelf.shelf = self.shelf.key
    shelf.put()
    mock_model_list_devices.return_value = (
        [self.device2.get().key, self.device3.get().key,
         self.device4.get().key], None, False)
    mock_get_shelf.return_value = self.shelf
    request = shelf_messages.ShelfAuditRequest(
        shelf_request=shelf_messages.ShelfRequest(location=self.shelf.location),
        device_identifiers=[self.device3.get().serial_number])
    self.service.audit(request)
    self.assertEqual(self.device3.get().shelf, self.shelf.key)
    self.assertEqual(self.device2.get().shelf, None)
    self.assertEqual(self.device4.get().shelf, None)

  def test_build_shelf_message(self):
    """Test building a shelf message from a shelf dictionary."""
    now = datetime.datetime.utcnow()
    test_data = {
        'enabled': True, 'friendly_name': 'New York', 'location': 'NYC',
        'latitude': 40.04, 'longitude': 50.05, 'altitude': 10.01,
        'capacity': 10, 'audit_notification_enabled': False,
        'audit_requested': True, 'responsible_for_audit': 'me',
        'last_audit_time': now, 'last_audit_by': 'you'}
    expected_response = shelf_messages.Shelf(
        enabled=True, friendly_name='New York', location='NYC',
        latitude=40.04, longitude=50.05, altitude=10.01, capacity=10,
        audit_notification_enabled=False, audit_requested=True,
        responsible_for_audit='me', last_audit_time=now, last_audit_by='you')
    response = shelf_api._build_shelf_message(test_data)
    self.assertEqual(response, expected_response)

  def test_get_shelf_urlsafe_key(self):
    """Test getting a shelf using the urlsafe key."""
    request = shelf_messages.ShelfRequest(urlsafe_key=self.shelf.key.urlsafe())
    shelf = shelf_api.get_shelf(request)
    self.assertEqual(shelf, self.shelf)

  def test_get_shelf_using_location(self):
    """Test getting a shelf using the location."""
    request = shelf_messages.ShelfRequest(location=self.shelf.location)
    shelf = shelf_api.get_shelf(request)
    self.assertEqual(shelf, self.shelf)

  def test_get_shelf_using_location_error(self):
    """Test getting a shelf with an invalid location."""
    request = shelf_messages.ShelfRequest(location='Not_Valid')
    with self.assertRaisesRegexp(
        endpoints.NotFoundException,
        shelf_api._SHELF_DOES_NOT_EXIST_MSG % request.location):
      shelf_api.get_shelf(request)


if __name__ == '__main__':
  loanertest.main()
