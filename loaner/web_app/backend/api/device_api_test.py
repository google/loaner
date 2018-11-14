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

"""Tests for backend.api.device_api."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import datetime

from absl.testing import parameterized
import mock

from protorpc import message_types
from google.appengine.api import datastore_errors

import endpoints

from loaner.web_app import constants
from loaner.web_app.backend.api import device_api
from loaner.web_app.backend.api import root_api
from loaner.web_app.backend.api.messages import device_messages
from loaner.web_app.backend.api.messages import shared_messages
from loaner.web_app.backend.api.messages import shelf_messages
from loaner.web_app.backend.clients import directory
from loaner.web_app.backend.lib import api_utils
from loaner.web_app.backend.models import config_model
from loaner.web_app.backend.models import device_model
from loaner.web_app.backend.models import shelf_model
from loaner.web_app.backend.testing import loanertest


class DeviceApiTest(parameterized.TestCase, loanertest.EndpointsTestCase):
  """Tests for the Device API."""

  def setUp(self):
    super(DeviceApiTest, self).setUp()
    self.service = device_api.DeviceApi()
    self.login_admin_endpoints_user()

    self.shelf = shelf_model.Shelf.enroll(
        user_email=loanertest.USER_EMAIL,
        location='NYC',
        capacity=10,
        friendly_name='GnG',
        latitude=40.6892534,
        longitude=-74.0466891,
        altitude=1.0)

    self.device = device_model.Device()
    self.device.serial_number = '123ABC'
    self.device.asset_tag = '12345'
    self.device.enrolled = True
    self.device.device_model = 'Google Pixelbook'
    self.device.due_date = datetime.datetime(2017, 11, 15)
    self.device.last_known_healthy = datetime.datetime(2017, 11, 1)
    self.device.shelf = self.shelf.key
    self.device.assigned_user = loanertest.USER_EMAIL
    self.device.assignment_date = datetime.datetime(2017, 11, 1)
    self.device.current_ou = '/'
    self.device.ou_changed_date = datetime.datetime(2017, 11, 1)
    self.device.locked = False
    self.device.lost = False
    self.device.chrome_device_id = 'unique_id_1'
    self.device.last_heartbeat = datetime.datetime(2017, 11, 1)
    self.device.damaged = False
    self.device.damaged_reason = None
    self.device.put()
    self.device.set_last_reminder(0)
    self.device.set_next_reminder(1, datetime.timedelta(hours=2))
    device_model.Device(
        serial_number='6789',
        enrolled=True,
        device_model='HP Chromebook 13 G1',
        current_ou='/',
        chrome_device_id='unique_id_2',
        shelf=self.shelf.key,
        damaged=False,
    ).put()
    self.unenrolled_device = device_model.Device(
        serial_number='4567',
        enrolled=False,
        device_model='HP Chromebook 13 G1',
        current_ou='/',
        chrome_device_id='unique_id_3',
        damaged=False,
    )
    self.unenrolled_device.put()
    self.unenrolled_device_directory = {
        'deviceId': 'unique_id',
        'serialNumber': '4567',
        'status': 'ACTIVE',
        'lastSync': datetime.datetime.utcnow(),
        'model': 'HP Chromebook 13 G1',
        'orgUnitPath': constants.ORG_UNIT_DICT['DEFAULT'],
    }

  def tearDown(self):
    super(DeviceApiTest, self).tearDown()
    self.service = None

  @mock.patch.object(directory, 'DirectoryApiClient', autospec=True)
  def test_enroll(self, mock_directoryclass):
    """Tests Enroll with mock methods."""
    mock_directoryclient = mock_directoryclass.return_value
    mock_directoryclient.get_chrome_device.return_value = (
        self.unenrolled_device)
    mock_directoryclient.get_chrome_device_by_serial.return_value = (
        self.unenrolled_device_directory)
    retrieved_device = device_model.Device.get(
        serial_number=self.unenrolled_device.serial_number)
    self.assertFalse(retrieved_device.enrolled)

    request = device_messages.DeviceRequest(
        serial_number=self.unenrolled_device.serial_number)
    with mock.patch.object(
        self.service, 'check_xsrf_token', autospec=True) as mock_xsrf_token:
      response = self.service.enroll(request)
      self.assertIsInstance(response, message_types.VoidMessage)
      retrieved_device = device_model.Device.get(
          serial_number=self.unenrolled_device.serial_number)
      self.assertTrue(retrieved_device.enrolled)
      self.assertEqual(mock_xsrf_token.call_count, 1)

  @parameterized.parameters((datastore_errors.BadValueError,),
                            (device_model.DeviceCreationError,))
  @mock.patch.object(device_model, 'Device', autospec=True)
  def test_enroll_error(self, test_error, mock_device_cls):
    mock_device_cls.enroll.side_effect = test_error
    request = device_messages.DeviceRequest(
        serial_number=self.unenrolled_device.serial_number)
    with self.assertRaises(endpoints.BadRequestException):
      self.service.enroll(request)

  @mock.patch.object(device_model, 'Device', autospec=True)
  def test_unenroll_error(self, mock_device_cls):
    mock_device_cls.get.return_value.unenroll.side_effect = (
        device_model.FailedToUnenrollError())
    request = device_messages.DeviceRequest(
        serial_number=self.unenrolled_device.serial_number)
    with self.assertRaises(endpoints.BadRequestException):
      self.service.unenroll(request)

  @mock.patch.object(directory, 'DirectoryApiClient', autospec=True)
  @mock.patch.object(root_api.Service, 'check_xsrf_token', autospec=True)
  def test_unenroll(self, mock_xsrf_token, mock_directoryclass):
    mock_directoryclient = mock_directoryclass.return_value
    mock_directoryclient.move_chrome_device_org_unit.return_value = (
        loanertest.TEST_DIR_DEVICE_DEFAULT)
    request = device_messages.DeviceRequest(
        serial_number=self.device.serial_number)
    self.assertTrue(self.device.enrolled)
    response = self.service.unenroll(request)
    self.assertFalse(self.device.enrolled)
    self.assertIsNone(self.device.assigned_user)
    self.assertIsNone(self.device.due_date)
    self.assertIsInstance(response, message_types.VoidMessage)
    self.assertEqual(mock_xsrf_token.call_count, 1)

  @mock.patch.object(directory, 'DirectoryApiClient', autospec=True)
  @mock.patch.object(root_api.Service, 'check_xsrf_token', autospec=True)
  def test_unlock(self, mock_xsrf_token, mock_directoryclass):
    self.device.lost = True
    self.device.locked = True
    self.device.put()
    mock_directoryclient = mock_directoryclass.return_value
    mock_directoryclient.move_chrome_device_org_unit.return_value = (
        loanertest.TEST_DIR_DEVICE_DEFAULT)
    request = device_messages.DeviceRequest(
        serial_number=self.device.serial_number)
    response = self.service.unlock(request)
    self.assertFalse(self.device.locked)
    self.assertFalse(self.device.lost)
    self.assertIsInstance(response, message_types.VoidMessage)
    self.assertEqual(mock_xsrf_token.call_count, 1)

  @mock.patch.object(directory, 'DirectoryApiClient', autospec=True)
  def test_unlock_directory_error(self, mock_directory_class):
    mock_directory_client = mock_directory_class.return_value
    mock_directory_client.reenable_chrome_device.side_effect = (
        directory.DirectoryRPCError)
    with self.assertRaises(endpoints.BadRequestException):
      self.service.unlock(device_messages.DeviceRequest(asset_tag='12345'))

  @mock.patch.object(directory, 'DirectoryApiClient', autospec=True)
  def test_unlock_move_ou_error(self, mock_directory_class):
    del mock_directory_class  # Unused.
    with mock.patch.object(
        self.device,
        'move_to_default_ou',
        side_effect=device_model.UnableToMoveToDefaultOUError):
      with self.assertRaises(endpoints.BadRequestException):
        self.service.unlock(device_messages.DeviceRequest(asset_tag='12345'))

  @mock.patch('__main__.device_model.Device.device_audit_check')
  def test_device_audit_check(self, mock_device_audit_check):
    request = device_messages.DeviceRequest(identifier='6765')
    self.assertRaisesRegexp(
        device_api.endpoints.NotFoundException,
        device_api._NO_DEVICE_MSG % '6765',
        self.service.device_audit_check, request)

    device_model.Device(
        serial_number='12345',
        enrolled=True,
        device_model='HP Chromebook 13 G1',
        current_ou='/',
        chrome_device_id='unique_id_1',
        damaged=False).put()
    request = device_messages.DeviceRequest(identifier='12345')
    response = self.service.device_audit_check(request)
    self.assertEqual(mock_device_audit_check.call_count, 1)
    self.assertIsInstance(response, message_types.VoidMessage)

  def test_device_audit_check_device_not_enrolled(self):
    request = device_messages.DeviceRequest(
        identifier=self.device.serial_number)
    self.device.enrolled = False
    with self.assertRaises(device_api.endpoints.BadRequestException):
      self.service.device_audit_check(request)

  def test_device_audit_check_device_damaged(self):
    request = device_messages.DeviceRequest(
        identifier=self.device.serial_number)
    self.device.damaged = True
    with self.assertRaises(device_api.endpoints.BadRequestException):
      self.service.device_audit_check(request)

  @mock.patch.object(directory, 'DirectoryApiClient', autospec=True)
  def test_get_device_not_found(self, mock_directory_class):
    mock_directory_client = mock_directory_class.return_value
    mock_directory_client.given_name.return_value = 'given name value'
    request = device_messages.DeviceRequest(identifier='not-found')
    with self.assertRaises(device_api.endpoints.NotFoundException):
      self.service.get_device(request)

  def test_get_device_unenrolled(self):
    request = device_messages.DeviceRequest(
        identifier=self.device.serial_number)
    self.device.enrolled = False
    with self.assertRaises(device_api.endpoints.BadRequestException):
      self.service.get_device(request)

  @mock.patch.object(directory, 'DirectoryApiClient', autospec=True)
  def test_get_device(self, mock_directory_class):
    mock_directory_client = mock_directory_class.return_value
    mock_directory_client.given_name.return_value = 'given name value'
    asset_tag_response = self.service.get_device(
        device_messages.DeviceRequest(asset_tag='12345'))
    chrome_device_id_response = self.service.get_device(
        device_messages.DeviceRequest(chrome_device_id='unique_id_1'))
    serial_number_response = self.service.get_device(
        device_messages.DeviceRequest(serial_number='123ABC'))
    urlkey_response = self.service.get_device(
        device_messages.DeviceRequest(urlkey=self.device.key.urlsafe()))
    identifier_response = self.service.get_device(
        device_messages.DeviceRequest(identifier='123ABC'))

    self.assertIsInstance(asset_tag_response, device_messages.Device)
    self.assertIsInstance(chrome_device_id_response, device_messages.Device)
    self.assertIsInstance(serial_number_response, device_messages.Device)
    self.assertIsInstance(urlkey_response, device_messages.Device)
    self.assertIsInstance(identifier_response, device_messages.Device)
    self.assertEqual(self.device.serial_number,
                     asset_tag_response.serial_number)
    self.assertEqual(self.device.device_model, urlkey_response.device_model)

  @mock.patch.object(directory, 'DirectoryApiClient', autospec=True)
  def test_get_device_no_permission(self, mock_directory_class):
    mock_directory_client = mock_directory_class.return_value
    mock_directory_client.given_name.return_value = 'given name value'
    email = 'random@{}'.format(loanertest.USER_DOMAIN)
    self.login_endpoints_user(email=email)
    with self.assertRaises(endpoints.UnauthorizedException):
      self.service.get_device(
          device_messages.DeviceRequest(
              serial_number=self.device.serial_number))

  @mock.patch.object(directory, 'DirectoryApiClient', autospec=True)
  def test_get_device_has_permission(self, mock_directory_class):
    mock_directory_client = mock_directory_class.return_value
    mock_directory_client.given_name.return_value = 'given name value'
    device = self.service.get_device(
        device_messages.DeviceRequest(serial_number=self.device.serial_number))
    self.assertIsInstance(device, device_messages.Device)
    self.assertEqual(device.serial_number, self.device.serial_number)

  @mock.patch.object(directory, 'DirectoryApiClient', autospec=True)
  def test_get_device_assigned_user(self, mock_directory_class):
    mock_directory_client = mock_directory_class.return_value
    mock_directory_client.given_name.return_value = 'given name value'
    email = 'random@{}'.format(loanertest.USER_DOMAIN)
    self.login_endpoints_user(email=email)
    self.device.assigned_user = email
    self.device.put()
    device = self.service.get_device(
        device_messages.DeviceRequest(serial_number=self.device.serial_number))
    self.assertIsInstance(device, device_messages.Device)
    self.assertEqual(device.serial_number, self.device.serial_number)

  @parameterized.parameters(directory.DirectoryRPCError,
                            directory.GivenNameDoesNotExistError)
  @mock.patch.object(directory, 'DirectoryApiClient', autospec=True)
  def test_get_device_directory_errors(self, test_error, mock_directory_class):
    request = device_messages.DeviceRequest(asset_tag='12345')
    mock_directory_client = mock_directory_class.return_value
    mock_directory_client.given_name.side_effect = test_error
    self.assertIsNone(self.service.get_device(request).given_name)

  @parameterized.parameters(
      (device_messages.Device(enrolled=True), 2,),
      (device_messages.Device(current_ou='/'), 2,),
      (device_messages.Device(enrolled=False), 1,),
      (device_messages.Device(
          query=shared_messages.SearchRequest(query_string='sn:6789')), 1,),
      (device_messages.Device(
          query=shared_messages.SearchRequest(query_string='at:12345')), 1,))
  def test_list_devices(self, request, response_length):
    response = self.service.list_devices(request)
    self.assertLen(response.devices, response_length)

  def test_list_devices_invalid_page_size(self):
    with self.assertRaises(endpoints.BadRequestException):
      request = device_messages.Device(page_size=0)
      self.service.list_devices(request)

  def test_list_devices_with_search_constraints(self):
    expressions = shared_messages.SearchExpression(expression='serial_number')
    expected_response = device_messages.ListDevicesResponse(
        devices=[
            device_messages.Device(serial_number='6789', guest_permitted=True)
        ],
        total_results=1,
        total_pages=1)
    request = device_messages.Device(
        query=shared_messages.SearchRequest(
            query_string='sn:6789',
            expressions=[expressions],
            returned_fields=['serial_number']))
    response = self.service.list_devices(request)
    self.assertEqual(response, expected_response)

  def test_list_devices_with_filter_message(self):
    message = device_messages.Device(
        enrolled=True, device_model='HP Chromebook 13 G1', current_ou='/')
    filters = api_utils.to_dict(message, device_model.Device)
    request = device_messages.Device(**filters)
    response = self.service.list_devices(request)
    expected_response = device_messages.ListDevicesResponse(
        devices=[
            device_messages.Device(
                serial_number='6789',
                identifier='6789',
                enrolled=True,
                device_model='HP Chromebook 13 G1',
                current_ou='/',
                locked=False,
                lost=False,
                chrome_device_id='unique_id_2',
                damaged=False,
                guest_permitted=True)
        ],
        total_results=1,
        total_pages=1)
    self.assertEqual(response, expected_response)

  @mock.patch('__main__.device_api.shelf_api.get_shelf')
  def test_list_devices_with_shelf_filter(self, mock_get_shelf):
    # Test for shelf location as filter.
    mock_get_shelf.return_value = self.shelf
    shelf_request_message = shelf_messages.ShelfRequest(
        location=self.shelf.location)
    message = shelf_messages.Shelf(shelf_request=shelf_request_message)
    request = device_messages.Device(shelf=message)
    response = self.service.list_devices(request)
    mock_get_shelf.assert_called_once_with(shelf_request_message)
    self.assertLen(response.devices, 2)

  def test_list_devices_with_offset(self):
    request = device_messages.Device(page_size=1, page_number=1)
    response = self.service.list_devices(request)
    self.assertLen(response.devices, 1)
    previouse_response = response

    # Get next page results and make sure it's not the same as last.
    request = device_messages.Device(page_size=1, page_number=2)
    response = self.service.list_devices(request)
    self.assertLen(response.devices, 1)
    self.assertNotEqual(response, previouse_response)

  def test_list_devices_inactive_no_shelf(self):
    request = device_messages.Device(enrolled=False, page_size=1)
    response = self.service.list_devices(request)
    expected_response = device_messages.ListDevicesResponse(
        devices=[
            device_messages.Device(
                serial_number=self.unenrolled_device.serial_number,
                identifier=self.unenrolled_device.serial_number,
                enrolled=self.unenrolled_device.enrolled,
                device_model=self.unenrolled_device.device_model,
                current_ou=self.unenrolled_device.current_ou,
                locked=self.unenrolled_device.locked,
                lost=self.unenrolled_device.lost,
                chrome_device_id=self.unenrolled_device.chrome_device_id,
                damaged=self.unenrolled_device.damaged,
                guest_permitted=True)
        ],
        total_results=1,
        total_pages=1)
    self.assertEqual(expected_response, response)

  @mock.patch('__main__.device_model.Device.list_by_user')
  @mock.patch.object(root_api.Service, 'check_xsrf_token', autospec=True)
  def test_list_user_devices(self, mock_xsrf_token, mock_list_by_user):
    self.login_endpoints_user()
    device2 = device_model.Device()
    device2.serial_number = '123ABC'
    device2.assigned_user = loanertest.USER_EMAIL
    device2.assignment_date = datetime.datetime(2017, 11, 1)
    device2.due_date = datetime.datetime(2017, 11, 4)
    device2.put()

    request = message_types.VoidMessage()
    mock_list_by_user.return_value = [self.device, device2]
    response = self.service.list_user_devices(request)
    self.assertEqual(response.devices[0].serial_number,
                     self.device.serial_number)
    self.assertLen(response.devices, 2)
    self.assertEqual(mock_xsrf_token.call_count, 1)
    mock_list_by_user.assert_called_once_with(loanertest.USER_EMAIL)

  @mock.patch('__main__.device_model.Device.enable_guest_mode')
  @mock.patch.object(root_api.Service, 'check_xsrf_token', autospec=True)
  def test_enable_guest_mode(self, mock_xsrf_token, mock_enableguest):
    config_model.Config.set('allow_guest_mode', True)
    self.login_endpoints_user()
    self.service.enable_guest_mode(
        device_messages.DeviceRequest(urlkey=self.device.key.urlsafe()))
    self.assertTrue(mock_enableguest.called)
    self.assertEqual(mock_xsrf_token.call_count, 1)

    mock_xsrf_token.reset_mock()
    mock_enableguest.reset_mock()
    self.service.enable_guest_mode(
        device_messages.DeviceRequest(
            chrome_device_id=self.device.chrome_device_id))
    self.assertTrue(mock_enableguest.called)
    self.assertEqual(mock_xsrf_token.call_count, 1)

    def guest_disabled_error(*args, **kwargs):
      del args, kwargs  # Unused.
      raise device_model.GuestNotAllowedError(
          device_model._GUEST_MODE_DISABLED_MSG)

    def directory_error(*args, **kwargs):
      del args, kwargs  # Unused.
      raise device_model.EnableGuestError('Directory broke, all your fault.')

    mock_enableguest.side_effect = guest_disabled_error
    with self.assertRaises(endpoints.UnauthorizedException):
      self.service.enable_guest_mode(
          device_messages.DeviceRequest(
              chrome_device_id=self.device.chrome_device_id))

    mock_enableguest.side_effect = directory_error
    with self.assertRaises(endpoints.InternalServerErrorException):
      self.service.enable_guest_mode(
          device_messages.DeviceRequest(
              chrome_device_id=self.device.chrome_device_id))

  def test_enable_guest_unassigned(self):
    config_model.Config.set('allow_guest_mode', True)
    self.device.assigned_user = None
    self.device.put()
    with self.assertRaisesRegexp(
        endpoints.UnauthorizedException,
        device_model._UNASSIGNED_DEVICE % self.device.identifier):
      self.service.enable_guest_mode(
          device_messages.DeviceRequest(urlkey=self.device.key.urlsafe()))

  @mock.patch('__main__.device_model.Device.loan_extend')
  @mock.patch.object(root_api.Service, 'check_xsrf_token', autospec=True)
  def test_extend_loan(self, mock_xsrf_token, mock_loanextend):
    tomorrow = datetime.datetime.utcnow() + datetime.timedelta(days=1)
    self.login_endpoints_user()
    self.service.extend_loan(
        device_messages.ExtendLoanRequest(
            device=device_messages.DeviceRequest(
                urlkey=self.device.key.urlsafe()),
            extend_date=tomorrow))
    mock_loanextend.assert_called_once_with(
        user_email=loanertest.USER_EMAIL, extend_date_time=tomorrow)
    self.assertEqual(mock_xsrf_token.call_count, 1)

    mock_xsrf_token.reset_mock()
    mock_loanextend.reset_mock()
    self.service.extend_loan(
        device_messages.ExtendLoanRequest(
            device=device_messages.DeviceRequest(
                chrome_device_id=self.device.chrome_device_id),
            extend_date=tomorrow))
    mock_loanextend.assert_called_once_with(
        user_email=loanertest.USER_EMAIL, extend_date_time=tomorrow)
    self.assertEqual(mock_xsrf_token.call_count, 1)

    mock_loanextend.side_effect = device_model.ExtendError
    self.assertRaises(
        device_api.endpoints.BadRequestException, self.service.extend_loan,
        device_messages.ExtendLoanRequest(
            device=device_messages.DeviceRequest(
                chrome_device_id=self.device.chrome_device_id),
            extend_date=tomorrow))

  def test_extend_loan_unassigned(self):
    self.device.assigned_user = None
    self.device.put()
    with self.assertRaisesRegexp(
        endpoints.UnauthorizedException,
        device_model._UNASSIGNED_DEVICE % self.device.identifier):
      self.service.extend_loan(
          device_messages.ExtendLoanRequest(
              device=device_messages.DeviceRequest(
                  chrome_device_id=self.device.chrome_device_id)))

  @mock.patch('__main__.device_model.Device.mark_damaged')
  @mock.patch.object(root_api.Service, 'check_xsrf_token', autospec=True)
  def test_mark_damaged(self, mock_xsrf_token, mock_markdamaged):
    self.login_endpoints_user()
    self.service.mark_damaged(
        device_messages.DamagedRequest(
            device=device_messages.DeviceRequest(
                urlkey=self.device.key.urlsafe()),
            damaged_reason='Foo'))
    mock_markdamaged.assert_called_once_with(
        user_email=loanertest.USER_EMAIL, damaged_reason='Foo')
    self.assertEqual(mock_xsrf_token.call_count, 1)

    mock_xsrf_token.reset_mock()
    mock_markdamaged.reset_mock()
    self.service.mark_damaged(
        device_messages.DamagedRequest(  # No reason given.
            device=device_messages.DeviceRequest(
                urlkey=self.device.key.urlsafe())))
    mock_markdamaged.assert_called_once_with(
        user_email=loanertest.USER_EMAIL, damaged_reason=None)
    self.assertEqual(mock_xsrf_token.call_count, 1)

  @mock.patch.object(device_model.Device, 'mark_damaged')
  @mock.patch.object(root_api.Service, 'check_xsrf_token', autospec=True)
  def test_mark_damaged__unauthorized(self, mock_xsrf, mock_markdamaged):
    del mock_xsrf  # Unused.
    self.login_endpoints_user()
    mock_markdamaged.side_effect = device_model.UnauthorizedError()
    with self.assertRaises(endpoints.UnauthorizedException):
      self.service.mark_damaged(
          device_messages.DamagedRequest(
              device=device_messages.DeviceRequest(
                  urlkey=self.device.key.urlsafe()),
              damaged_reason='Foo'))

  def test_mark_undamaged(self):
    with mock.patch.object(self.device, 'mark_undamaged') as mock_markundamaged:
      self.service.mark_undamaged(
          device_messages.DeviceRequest(urlkey=self.device.key.urlsafe()))
      mock_markundamaged.assert_called_once_with(
          user_email=loanertest.SUPER_ADMIN_EMAIL)

  @mock.patch.object(device_model.Device, 'mark_undamaged')
  def test_mark_undamaged__unauthorized(self, mock_markundamaged):
    self.login_endpoints_user()
    with mock.patch.object(self.service, 'check_xsrf_token') as mock_xsrf_token:
      mock_markundamaged.side_effect = device_model.UnauthorizedError()
      with self.assertRaises(endpoints.UnauthorizedException):
        self.service.mark_undamaged(
            device_messages.DeviceRequest(urlkey=self.device.key.urlsafe()))
      self.assertEqual(mock_xsrf_token.call_count, 1)

  @mock.patch('__main__.device_model.Device.mark_lost')
  @mock.patch.object(root_api.Service, 'check_xsrf_token', autospec=True)
  def test_mark_lost(self, mock_xsrf_token, mock_marklost):
    self.service.mark_lost(
        device_messages.DeviceRequest(urlkey=self.device.key.urlsafe()))
    mock_marklost.assert_called_once_with(
        user_email=loanertest.SUPER_ADMIN_EMAIL)
    self.assertEqual(mock_xsrf_token.call_count, 1)

  @mock.patch.object(device_model.Device, 'mark_lost')
  @mock.patch.object(root_api.Service, 'check_xsrf_token', autospec=True)
  def test_mark_lost__unauthorized(self, mock_xsrf_token, mock_marklost):
    del mock_xsrf_token  # Unused.
    mock_marklost.side_effect = device_model.UnauthorizedError()
    with self.assertRaises(endpoints.UnauthorizedException):
      self.service.mark_lost(
          device_messages.DeviceRequest(urlkey=self.device.key.urlsafe()))

  @mock.patch('__main__.device_model.Device.mark_pending_return')
  @mock.patch.object(root_api.Service, 'check_xsrf_token', autospec=True)
  def test_mark_pending_return(self, mock_xsrf_token, mock_markreturned):
    self.login_endpoints_user()
    self.service.mark_pending_return(
        device_messages.DeviceRequest(urlkey=self.device.key.urlsafe()))
    mock_markreturned.assert_called_once_with(user_email=loanertest.USER_EMAIL)
    self.assertEqual(mock_xsrf_token.call_count, 1)

  def test_mark_pending_return_unassigned(self):
    self.device.assigned_user = None
    self.device.put()
    with self.assertRaisesRegexp(
        endpoints.UnauthorizedException,
        device_model._UNASSIGNED_DEVICE % self.device.identifier):
      self.service.mark_pending_return(
          device_messages.DeviceRequest(urlkey=self.device.key.urlsafe()))

  @mock.patch('__main__.device_model.Device.resume_loan')
  @mock.patch.object(root_api.Service, 'check_xsrf_token', autospec=True)
  def test_resume_loan(self, mock_xsrf_token, mock_resume_loan):
    self.login_endpoints_user()
    self.service.resume_loan(
        device_messages.DeviceRequest(urlkey=self.device.key.urlsafe()))
    self.assertEqual(mock_resume_loan.call_count, 1)
    self.assertEqual(mock_xsrf_token.call_count, 1)

  @mock.patch.object(device_model.Device, 'resume_loan')
  @mock.patch.object(root_api.Service, 'check_xsrf_token', autospec=True)
  def test_resume_loan__unauthorized(self, mock_xsrf_token, mock_resume_loan):
    del mock_xsrf_token  # Unused.
    self.login_endpoints_user()
    mock_resume_loan.side_effect = device_model.UnauthorizedError()
    with self.assertRaises(endpoints.UnauthorizedException):
      self.service.resume_loan(
          device_messages.DeviceRequest(urlkey=self.device.key.urlsafe()))

  def test_get_device_errors(self):
    # No identifiers.
    with self.assertRaises(endpoints.BadRequestException):
      device_api._get_device(device_messages.DeviceRequest())

    # URL-safe key that is still URL-safe, but technically not a key.
    with self.assertRaises(device_api.endpoints.BadRequestException):
      device_api._get_device(device_messages.DeviceRequest(urlkey='bad-key'))


if __name__ == '__main__':
  loanertest.main()
