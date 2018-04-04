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

import datetime

import mock

from protorpc import message_types

import endpoints

from loaner.web_app import constants
from loaner.web_app.backend.api import device_api
from loaner.web_app.backend.api import root_api
from loaner.web_app.backend.api.messages import device_message
from loaner.web_app.backend.api.messages import shelf_message
from loaner.web_app.backend.models import config_model
from loaner.web_app.backend.models import device_model
from loaner.web_app.backend.models import shelf_model
from loaner.web_app.backend.testing import loanertest


class DeviceApiTest(loanertest.EndpointsTestCase):
  """Tests for the Device API."""

  def setUp(self):
    super(DeviceApiTest, self).setUp()
    self.service = device_api.DeviceApi()
    self.login_admin_endpoints_user()

    self.shelf = shelf_model.Shelf.enroll(
        user_email=loanertest.USER_EMAIL, location='NYC', capacity=10,
        friendly_name='GnG', latitude=40.6892534, longitude=-74.0466891,
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

  def tearDown(self):
    super(DeviceApiTest, self).tearDown()
    self.service = None

  @mock.patch(
      '__main__.device_model.directory.DirectoryApiClient', autospec=True)
  @mock.patch('__main__.root_api.Service.check_xsrf_token')
  def test_enroll(self, mock_xsrf_token, mock_directoryclass):
    """Tests Enroll with mock methods."""
    mock_directoryclient = mock_directoryclass.return_value
    mock_directoryclient.get_chrome_device.return_value = (
        self.unenrolled_device)
    retrieved_device = device_model.Device.get(
        serial_number=self.unenrolled_device.serial_number)
    self.assertFalse(retrieved_device.enrolled)

    request = device_message.DeviceRequest(
        serial_number=self.unenrolled_device.serial_number)
    response = self.service.enroll(request)
    self.assertIsInstance(response, message_types.VoidMessage)
    retrieved_device = device_model.Device.get(
        serial_number=self.unenrolled_device.serial_number)
    self.assertTrue(retrieved_device.enrolled)
    mock_xsrf_token.assert_called_once()

  @mock.patch(
      '__main__.device_model.directory.DirectoryApiClient', autospec=True)
  def test_enroll_error(self, mock_directoryclass):
    err_message = 'Failed to move device'
    mock_directoryclient = mock_directoryclass.return_value
    mock_directoryclient.move_chrome_device_org_unit.side_effect = (
        device_model.directory.DirectoryRPCError(err_message))
    request = device_message.DeviceRequest(
        serial_number=self.unenrolled_device.serial_number)
    ou = constants.ORG_UNIT_DICT.get('DEFAULT')
    with self.assertRaisesRegexp(
        endpoints.BadRequestException,
        device_model._FAILED_TO_MOVE_DEVICE_MSG % (
            self.unenrolled_device.serial_number, ou, err_message)):
      self.service.enroll(request)

  @mock.patch(
      '__main__.device_model.directory.DirectoryApiClient', autospec=True)
  def test_unenroll_error(self, mock_directoryclass):
    err_message = 'Failed to move device'
    mock_directoryclient = mock_directoryclass.return_value
    mock_directoryclient.move_chrome_device_org_unit.side_effect = (
        device_model.directory.DirectoryRPCError(err_message))
    request = device_message.DeviceRequest(
        serial_number=self.unenrolled_device.serial_number)
    ou = config_model.Config.get('unenroll_ou')
    with self.assertRaisesRegexp(
        endpoints.BadRequestException,
        device_model._FAILED_TO_MOVE_DEVICE_MSG % (
            self.unenrolled_device.serial_number, ou, err_message)):
      self.service.unenroll(request)

  @mock.patch(
      '__main__.device_model.directory.DirectoryApiClient', autospec=True)
  @mock.patch('__main__.root_api.Service.check_xsrf_token')
  def test_unenroll(self, mock_xsrf_token, mock_directoryclass):
    mock_directoryclient = mock_directoryclass.return_value
    mock_directoryclient.move_chrome_device_org_unit.return_value = (
        loanertest.TEST_DIR_DEVICE_DEFAULT)
    request = device_message.DeviceRequest(
        serial_number=self.device.serial_number)
    self.assertTrue(self.device.enrolled)
    response = self.service.unenroll(request)
    self.assertFalse(self.device.enrolled)
    self.assertIsNone(self.device.assigned_user)
    self.assertIsNone(self.device.due_date)
    self.assertIsInstance(response, message_types.VoidMessage)
    mock_xsrf_token.assert_called_once()

  @mock.patch('__main__.device_model.Device.device_audit_check')
  def test_device_audit_check(self, mock_device_audit_check):
    request = device_message.DeviceRequest(unknown_identifier='6765')
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
    request = device_message.DeviceRequest(
        unknown_identifier='12345')
    response = self.service.device_audit_check(request)
    mock_device_audit_check.assert_called_once()
    self.assertIsInstance(response, message_types.VoidMessage)

  def test_device_audit_check_device_not_enrolled(self):
    request = device_message.DeviceRequest(
        unknown_identifier=self.device.serial_number)
    self.device.enrolled = False
    with self.assertRaisesRegexp(
        device_api.endpoints.BadRequestException,
        device_model._DEVICE_NOT_ENROLLED_MSG % self.device.serial_number):
      self.service.device_audit_check(request)

  def test_device_audit_check_device_damaged(self):
    request = device_message.DeviceRequest(
        unknown_identifier=self.device.serial_number)
    self.device.damaged = True
    with self.assertRaisesRegexp(
        device_api.endpoints.BadRequestException,
        device_model._DEVICE_DAMAGED_MSG %self.device.serial_number):
      self.service.device_audit_check(request)

  def test_get_device_not_enrolled(self):
    constants.ON_LOCAL = False
    request = device_message.DeviceRequest(unknown_identifier='not-enrolled')
    self.assertRaisesRegexp(
        device_api.endpoints.NotFoundException,
        device_api._NO_DEVICE_MSG % 'not-enrolled',
        self.service.get_device, request)

  def test_get_device(self):
    constants.ON_LOCAL = False
    asset_tag_response = self.service.get_device(
        device_message.DeviceRequest(asset_tag='12345'))
    chrome_device_id_response = self.service.get_device(
        device_message.DeviceRequest(chrome_device_id='unique_id_1'))
    serial_number_response = self.service.get_device(
        device_message.DeviceRequest(serial_number='123ABC'))
    urlkey_response = self.service.get_device(
        device_message.DeviceRequest(urlkey=self.device.key.urlsafe()))
    unknown_identifier_response = self.service.get_device(
        device_message.DeviceRequest(unknown_identifier='123ABC'))

    self.assertIsInstance(asset_tag_response, device_message.Device)
    self.assertIsInstance(chrome_device_id_response, device_message.Device)
    self.assertIsInstance(serial_number_response, device_message.Device)
    self.assertIsInstance(urlkey_response, device_message.Device)
    self.assertIsInstance(unknown_identifier_response, device_message.Device)
    self.assertEqual(
        self.device.serial_number, asset_tag_response.serial_number)
    self.assertEqual(
        self.device.device_model, urlkey_response.device_model)

  def test_get_device_no_shelf(self):
    chrome_device_id_response = self.service.get_device(
        device_message.DeviceRequest(chrome_device_id='unique_id_3'))
    self.assertIsNone(chrome_device_id_response.shelf)

  def test_get_device_unable_to_get_shelf(self):
    # Delete the existing shelf key from datastore.
    self.shelf.key.delete()
    # Make sure it raises the execption after deleteing the key.
    with self.assertRaisesRegexp(
        device_api.endpoints.NotFoundException,
        device_api._SHELF_NOT_FOUND_MSG % self.device.shelf.urlsafe()):
      self.service.get_device(
          device_message.DeviceRequest(
              chrome_device_id=self.device.chrome_device_id))

  def test_list_devices(self):
    request = device_message.Device(enrolled=True)
    response = self.service.list_devices(request)
    self.assertEqual(2, len(response.devices))

    # Test list_devices with current ou filter.
    request = device_message.Device(enrolled=True, current_ou='/')
    response = self.service.list_devices(request)
    self.assertEqual(2, len(response.devices))

    # Test list_devices with chrome_device_id filter.
    request = device_message.Device(
        enrolled=True, chrome_device_id='unique_id_2')
    response = self.service.list_devices(request)
    self.assertEqual(1, len(response.devices))

  def test_list_devices_with_filter_message(self):
    message = device_message.Device(
        enrolled=True, device_model='HP Chromebook 13 G1', current_ou='/')
    service = root_api.Service()
    filters = service.to_dict(message, device_model.Device)
    request = device_message.Device(**filters)
    response = self.service.list_devices(request)
    self.assertEqual(1, len(response.devices))
    self.assertEqual(response.devices[0].serial_number, '6789')

  @mock.patch('__main__.device_model.Device.list_devices')
  @mock.patch('__main__.device_api.shelf_api.get_shelf')
  def test_list_devices_with_shelf_filter(
      self, mock_get_shelf, mock_model_list_devices):
    # Test for shelf location as filter.
    mock_model_list_devices.return_value = ([self.device], None, False)
    mock_get_shelf.return_value = self.shelf
    message = shelf_message.Shelf(location=self.shelf.location)
    request = device_message.Device(shelf=message)
    response = self.service.list_devices(request)
    mock_get_shelf.assert_called_once_with(location=self.shelf.location)
    self.assertEqual(
        response.devices[0].serial_number, self.device.serial_number)

  def test_list_devices_with_page_token(self):
    request = device_message.Device(enrolled=True, page_size=1)
    response = self.service.list_devices(request)
    response_devices = []
    while response.page_token or response.additional_results:
      for device in response.devices:
        response_devices.append(device)
      request = device_message.Device(
          enrolled=True, page_size=1, page_token=response.page_token)
      response = self.service.list_devices(request)
    self.assertEqual(2, len(response_devices))

  def test_list_devices_with_malformed_page_token(self):
    """Test list devices with a fake token, raises BadRequestException."""
    request = device_message.Device(page_token='malformedtoken')
    with self.assertRaisesRegexp(
        endpoints.BadRequestException,
        root_api._MALFORMED_PAGE_TOKEN_MSG):
      self.service.list_devices(request)

  def test_list_devices_inactive_no_shelf(self):
    request = device_message.Device(enrolled=False, page_size=1)
    response = self.service.list_devices(request)
    self.assertEqual(1, len(response.devices))

  @mock.patch('__main__.device_model.Device.list_by_user')
  @mock.patch('__main__.root_api.Service.check_xsrf_token')
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
    self.assertEqual(
        response.devices[0].serial_number, self.device.serial_number)
    self.assertEqual(len(response.devices), 2)
    mock_xsrf_token.assert_called_once()
    mock_list_by_user.assert_called_once_with(loanertest.USER_EMAIL)

  @mock.patch('__main__.device_api._confirm_assignee_action', autospec=True)
  @mock.patch('__main__.device_model.Device.enable_guest_mode')
  @mock.patch('__main__.root_api.Service.check_xsrf_token')
  def test_enable_guest_mode(
      self, mock_xsrf_token, mock_enableguest, mock_confirm_assignee_action):
    config_model.Config.set('allow_guest_mode', True)
    self.login_endpoints_user()
    self.service.enable_guest_mode(
        device_message.DeviceRequest(urlkey=self.device.key.urlsafe()))
    assert mock_enableguest.called
    mock_confirm_assignee_action.assert_called_once_with(
        loanertest.USER_EMAIL, self.device)
    mock_xsrf_token.assert_called_once()

    mock_xsrf_token.reset_mock()
    mock_enableguest.reset_mock()
    self.service.enable_guest_mode(device_message.DeviceRequest(
        chrome_device_id=self.device.chrome_device_id))
    assert mock_enableguest.called
    mock_xsrf_token.assert_called_once()

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
          device_message.DeviceRequest(
              chrome_device_id=self.device.chrome_device_id))

    mock_enableguest.side_effect = directory_error
    with self.assertRaises(endpoints.InternalServerErrorException):
      self.service.enable_guest_mode(
          device_message.DeviceRequest(
              chrome_device_id=self.device.chrome_device_id))

  def test_enable_guest_unassigned(self):
    config_model.Config.set('allow_guest_mode', True)
    self.device.assigned_user = None
    self.device.put()
    with self.assertRaisesRegexp(
        endpoints.UnauthorizedException,
        device_model._UNASSIGNED_DEVICE):
      self.service.enable_guest_mode(
          device_message.DeviceRequest(urlkey=self.device.key.urlsafe()))

  @mock.patch('__main__.device_api._confirm_assignee_action', autospec=True)
  @mock.patch('__main__.device_model.Device.loan_extend')
  @mock.patch('__main__.root_api.Service.check_xsrf_token')
  def test_extend_loan(
      self, mock_xsrf_token, mock_loanextend, mock_confirm_assignee_action):
    tomorrow = datetime.datetime.utcnow() + datetime.timedelta(days=1)
    self.login_endpoints_user()
    self.service.extend_loan(device_message.ExtendLoanRequest(
        device=device_message.DeviceRequest(urlkey=self.device.key.urlsafe()),
        extend_date=tomorrow))
    mock_loanextend.assert_called_once_with(
        user_email=loanertest.USER_EMAIL, extend_date_time=tomorrow)
    mock_confirm_assignee_action.assert_called_once_with(
        loanertest.USER_EMAIL, self.device)
    mock_xsrf_token.assert_called_once()

    mock_xsrf_token.reset_mock()
    mock_loanextend.reset_mock()
    self.service.extend_loan(device_message.ExtendLoanRequest(
        device=device_message.DeviceRequest(
            chrome_device_id=self.device.chrome_device_id),
        extend_date=tomorrow))
    mock_loanextend.assert_called_once_with(
        user_email=loanertest.USER_EMAIL, extend_date_time=tomorrow)
    mock_xsrf_token.assert_called_once()

    mock_loanextend.side_effect = device_model.ExtendError
    self.assertRaises(
        device_api.endpoints.BadRequestException,
        self.service.extend_loan,
        device_message.ExtendLoanRequest(
            device=device_message.DeviceRequest(
                chrome_device_id=self.device.chrome_device_id),
            extend_date=tomorrow))

  def test_extend_loan_unassigned(self):
    self.device.assigned_user = None
    self.device.put()
    with self.assertRaisesRegexp(
        endpoints.UnauthorizedException,
        device_model._UNASSIGNED_DEVICE):
      self.service.extend_loan(
          device_message.ExtendLoanRequest(
              device=device_message.DeviceRequest(
                  chrome_device_id=self.device.chrome_device_id)))

  @mock.patch('__main__.device_api._confirm_assignee_action', autospec=True)
  @mock.patch('__main__.device_model.Device.mark_damaged')
  @mock.patch('__main__.root_api.Service.check_xsrf_token')
  def test_mark_damaged(
      self, mock_xsrf_token, mock_markdamaged, mock_confirm_assignee_action):
    self.login_endpoints_user()
    self.service.mark_damaged(device_message.DamagedRequest(
        device=device_message.DeviceRequest(urlkey=self.device.key.urlsafe()),
        damaged_reason='Foo'))
    mock_markdamaged.assert_called_once_with(
        user_email=loanertest.USER_EMAIL, damaged_reason='Foo')
    mock_confirm_assignee_action.assert_called_once_with(
        loanertest.USER_EMAIL, self.device)
    mock_xsrf_token.assert_called_once()

    mock_xsrf_token.reset_mock()
    mock_markdamaged.reset_mock()
    self.service.mark_damaged(device_message.DamagedRequest(  # No reason given.
        device=device_message.DeviceRequest(urlkey=self.device.key.urlsafe())))
    mock_markdamaged.assert_called_once_with(
        user_email=loanertest.USER_EMAIL, damaged_reason=None)
    mock_xsrf_token.assert_called_once()

  @mock.patch('__main__.device_model.Device.mark_lost')
  @mock.patch('__main__.root_api.Service.check_xsrf_token')
  def test_mark_lost(self, mock_xsrf_token, mock_marklost):
    self.service.mark_lost(device_message.DeviceRequest(
        urlkey=self.device.key.urlsafe()))
    mock_marklost.assert_called_once_with(
        user_email=loanertest.SUPER_ADMIN_EMAIL)
    mock_xsrf_token.assert_called_once()

  @mock.patch('__main__.device_api._confirm_assignee_action', autospec=True)
  @mock.patch('__main__.device_model.Device.mark_pending_return')
  @mock.patch('__main__.root_api.Service.check_xsrf_token')
  def test_mark_pending_return(
      self, mock_xsrf_token, mock_markreturned, mock_confirm_assignee_action):
    self.login_endpoints_user()
    self.service.mark_pending_return(device_message.DeviceRequest(
        urlkey=self.device.key.urlsafe()))
    mock_markreturned.assert_called_once_with(
        user_email=loanertest.USER_EMAIL)
    mock_confirm_assignee_action.assert_called_once_with(
        loanertest.USER_EMAIL, self.device)
    mock_xsrf_token.assert_called_once()

  def test_mark_pending_return_unassigned(self):
    self.device.assigned_user = None
    self.device.put()
    with self.assertRaisesRegexp(
        endpoints.UnauthorizedException,
        device_model._UNASSIGNED_DEVICE):
      self.service.mark_pending_return(
          device_message.DeviceRequest(urlkey=self.device.key.urlsafe()))

  @mock.patch('__main__.device_api._confirm_assignee_action', autospec=True)
  @mock.patch('__main__.device_model.Device.resume_loan')
  @mock.patch('__main__.root_api.Service.check_xsrf_token')
  def test_resume_loan(
      self, mock_xsrf_token, mock_resume_loan, mock_confirm_assignee_action):
    self.login_endpoints_user()
    self.service.resume_loan(device_message.DeviceRequest(
        urlkey=self.device.key.urlsafe()))
    mock_resume_loan.assert_called_once()
    mock_confirm_assignee_action.assert_called_once_with(
        loanertest.USER_EMAIL, self.device)
    mock_xsrf_token.assert_called_once()

  def test_get_device_errors(self):
    # No identifiers.
    self.assertRaisesRegexp(
        device_api.endpoints.BadRequestException,
        device_api._NO_IDENTIFIERS_MSG, device_api._get_device,
        device_message.DeviceRequest())

    # URL-safe key that is still URL-safe, but technically not a key.
    self.assertRaisesRegexp(
        device_api.endpoints.BadRequestException,
        device_api._BAD_URLKEY_MSG % 'bad-key', device_api._get_device,
        device_message.DeviceRequest(urlkey='bad-key'))

  def test_build_reminder_messages_next_reminder(self):
    _, next_reminder_message = device_api._build_reminder_messages(self.device)
    self.assertEqual(
        next_reminder_message.level, self.device.next_reminder.level)

  @mock.patch('__main__.device_model.logging.info')
  def test_build_reminder_messages_no_reminders(self, mock_logging):
    # No next_reminder
    device = device_model.Device.get(serial_number='4567')
    _, next_reminder = device_api._build_reminder_messages(device)
    self.assertIsNone(next_reminder)

    # No last_reminder
    last_reminder, _ = device_api._build_reminder_messages(device)
    self.assertIsNone(last_reminder)
    self.assertEqual(4, mock_logging.call_count)

  def test_build_reminder_messages_last_reminder(self):
    last_reminder_message, _ = device_api._build_reminder_messages(self.device)
    self.assertEqual(
        last_reminder_message.level, self.device.last_reminder.level)

  def test_build_shelf_message(self):
    message = device_api._build_shelf_message(self.shelf)
    self.assertEqual(message.location, self.shelf.location)

  def test_confirm_assignee_action(self):
    user_email = 'test@{}'.format(loanertest.USER_DOMAIN)
    with self.assertRaisesRegexp(
        device_api.endpoints.UnauthorizedException,
        device_api._ASSIGNMENT_MISMATCH_MSG):
      device_api._confirm_assignee_action(user_email, self.device)

if __name__ == '__main__':
  loanertest.main()
