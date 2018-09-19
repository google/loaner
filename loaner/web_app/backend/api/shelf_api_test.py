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

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from absl.testing import parameterized
import mock

from protorpc import message_types

from google.appengine.api import search

import endpoints

from loaner.web_app.backend.api import root_api  # pylint: disable=unused-import
from loaner.web_app.backend.api import shelf_api
from loaner.web_app.backend.api.messages import shared_messages
from loaner.web_app.backend.api.messages import shelf_messages
from loaner.web_app.backend.models import device_model
from loaner.web_app.backend.models import shelf_model  # pylint: disable=unused-import
from loaner.web_app.backend.testing import loanertest


class ShelfApiTest(parameterized.TestCase, loanertest.EndpointsTestCase):
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

    self.device1_key = device_model.Device(
        serial_number='12345',
        enrolled=True,
        device_model='HP Chromebook 13 G1',
        current_ou='/',
        chrome_device_id='unique_id_1',
        damaged=False,
    ).put()
    self.device2_key = device_model.Device(
        serial_number='54321',
        enrolled=True,
        device_model='HP Chromebook 13 G1',
        current_ou='/',
        chrome_device_id='unique_id_2',
        damaged=False,
    ).put()
    self.device3_key = device_model.Device(
        serial_number='67890',
        enrolled=True,
        shelf=self.shelf.key,
        device_model='HP Chromebook 13 G1',
        current_ou='/',
        chrome_device_id='unique_id_3',
        damaged=False,
    ).put()
    self.device4_key = device_model.Device(
        serial_number='ABC123',
        enrolled=True,
        shelf=self.shelf.key,
        device_model='HP Chromebook 13 G1',
        current_ou='/',
        chrome_device_id='unique_id_4',
        damaged=False,
    ).put()
    self.device_identifiers = [
        self.device1_key.get().serial_number,
        self.device2_key.get().serial_number,
        self.device3_key.get().serial_number]

  def tearDown(self):
    super(ShelfApiTest, self).tearDown()
    self.service = None

  @mock.patch('__main__.root_api.Service.check_xsrf_token')
  @mock.patch('__main__.shelf_model.Shelf.enroll')
  def test_enroll(self, mock_enroll, mock_xsrf_token):
    """Test Enroll with mock methods."""
    request = shelf_messages.EnrollShelfRequest(
        location='nyc', capacity=100, friendly_name='test', latitude=12.5,
        longitude=12.5, altitude=2.0, responsible_for_audit='precise',
        audit_interval_override=33, audit_notification_enabled=True)
    response = self.service.enroll(request)
    self.assertEqual(mock_xsrf_token.call_count, 1)
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
    self.assertEqual(mock_xsrf_token.call_count, 1)
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
    self.assertEqual(mock_xsrf_token.call_count, 1)
    self.assertEqual(self.shelf.location, 'NYC-9th')
    shelf = shelf_model.Shelf.get(friendly_name='GnG')
    self.assertEqual(shelf.location, 'NYC-9th')
    self.assertIsInstance(response, message_types.VoidMessage)

  @parameterized.parameters(
      (shelf_messages.Shelf(capacity=10), 2,),
      (shelf_messages.Shelf(enabled=False), 1,),
      (shelf_messages.Shelf(
          query=shared_messages.SearchRequest(
              query_string='enabled:True capacity:10')), 2,),
      (shelf_messages.Shelf(
          query=shared_messages.SearchRequest(
              query_string='enabled:False')), 1,))
  @mock.patch('__main__.root_api.Service.check_xsrf_token')
  def test_list_shelves(self, request, response_length, mock_xsrf_token):
    response = self.service.list_shelves(request)
    self.assertEqual(mock_xsrf_token.call_count, 1)
    self.assertLen(response.shelves, response_length)

  def test_list_shelves_invalid_page_size(self):
    with self.assertRaises(endpoints.BadRequestException):
      request = shelf_messages.Shelf(page_size=0)
      self.service.list_shelves(request)

  def test_list_shelves_with_search_constraints(self):
    expressions = shared_messages.SearchExpression(expression='location')
    expected_response = shelf_messages.ListShelfResponse(
        shelves=[shelf_messages.Shelf(
            location=self.shelf.location,
            shelf_request=shelf_messages.ShelfRequest(
                location=self.shelf.location,
                urlsafe_key=self.shelf.key.urlsafe()))],
        total_results=1, total_pages=1)
    request = shelf_messages.Shelf(
        query=shared_messages.SearchRequest(
            query_string='location:NYC',
            expressions=[expressions],
            returned_fields=['location']))
    response = self.service.list_shelves(request)
    self.assertEqual(response, expected_response)

  def test_list_shelves_with_offset(self):
    previouse_shelf_locations = []
    request = shelf_messages.Shelf(enabled=True, page_size=1, page_number=1)
    response = self.service.list_shelves(request)
    self.assertLen(response.shelves, 1)
    previouse_shelf_locations.append(response.shelves[0].location)

    # Get next page results and make sure it's not the same as last.
    request = shelf_messages.Shelf(enabled=True, page_size=1, page_number=2)
    response = self.service.list_shelves(request)
    self.assertLen(response.shelves, 1)
    self.assertNotIn(response.shelves[0], previouse_shelf_locations)
    previouse_shelf_locations.append(response.shelves[0].location)

    # Get next page results and make sure it's not the same as last 2.
    request = shelf_messages.Shelf(enabled=True, page_size=1, page_number=3)
    response = self.service.list_shelves(request)
    self.assertLen(response.shelves, 1)
    self.assertNotIn(response.shelves[0], previouse_shelf_locations)
    previouse_shelf_locations.append(response.shelves[0].location)

  @mock.patch('__main__.root_api.Service.check_xsrf_token')
  @mock.patch('__main__.shelf_api.logging.info')
  def test_audit_using_shelf_location(self, mock_logging, mock_xsrf_token):
    request = shelf_messages.ShelfAuditRequest(
        shelf_request=shelf_messages.ShelfRequest(location='NYC'),
        device_identifiers=self.device_identifiers)
    response = self.service.audit(request)
    self.assertEqual(mock_xsrf_token.call_count, 1)
    self.assertTrue(mock_logging.called)
    for identifier in self.device_identifiers:
      datastore_device = device_model.Device.get(serial_number=identifier)
      self.assertEqual(datastore_device.shelf.get().location, 'NYC')
    self.assertFalse(self.shelf.audit_requested)
    self.assertEqual(self.shelf.last_audit_by, loanertest.SUPER_ADMIN_EMAIL)
    self.assertIsInstance(response, message_types.VoidMessage)

  def test_audit_invalid_device(self):
    request = shelf_messages.ShelfAuditRequest(
        shelf_request=shelf_messages.ShelfRequest(location='NYC'),
        device_identifiers=['Invalid'])
    with self.assertRaisesRegexp(
        endpoints.NotFoundException,
        shelf_api._DEVICE_DOES_NOT_EXIST_MSG % 'Invalid'):
      self.service.audit(request)

  @mock.patch.object(device_model.Device, 'search')
  @mock.patch.object(shelf_api, 'get_shelf', autospec=True)
  def test_audit_remove_devices(
      self, mock_get_shelf, mock_model_device_search):
    shelf = self.device2_key.get()
    shelf.shelf = self.shelf.key
    shelf.put()
    mock_model_device_search.return_value = (
        search.SearchResults(
            results=[
                search.ScoredDocument(
                    doc_id=self.device2_key.urlsafe()),
                search.ScoredDocument(
                    doc_id=self.device3_key.urlsafe()),
                search.ScoredDocument(
                    doc_id=self.device4_key.urlsafe())],
            number_found=3))
    mock_get_shelf.return_value = self.shelf
    request = shelf_messages.ShelfAuditRequest(
        shelf_request=shelf_messages.ShelfRequest(location=self.shelf.location),
        device_identifiers=[self.device3_key.get().serial_number])
    self.service.audit(request)
    self.assertEqual(self.device3_key.get().shelf, self.shelf.key)
    self.assertIsNone(self.device2_key.get().shelf)
    self.assertIsNone(self.device4_key.get().shelf)

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
