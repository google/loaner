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

"""Tests for backend.models.device_model."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import datetime

import freezegun
import mock

from google.appengine.api import datastore_errors
from google.appengine.api import search
from google.appengine.ext import deferred

from loaner.web_app import constants
from loaner.web_app.backend.clients import directory
from loaner.web_app.backend.models import config_model
from loaner.web_app.backend.models import device_model
from loaner.web_app.backend.models import shelf_model
from loaner.web_app.backend.testing import loanertest


class DeviceModelTest(loanertest.EndpointsTestCase):
  """Tests for the Device class."""

  def setUp(self):
    super(DeviceModelTest, self).setUp()
    self.shelf = shelf_model.Shelf.enroll(
        user_email=loanertest.USER_EMAIL, location='MTV', capacity=10,
        friendly_name='MTV office')
    device_model.Device(
        serial_number='12321', enrolled=True,
        device_model='HP Chromebook 13 G1', current_ou='/',
        shelf=self.shelf.key, chrome_device_id='unique_id_1',
        damaged=False).put()
    device_model.Device(
        serial_number='67890', enrolled=True,
        device_model='Google Pixelbook', current_ou='/',
        shelf=self.shelf.key, chrome_device_id='unique_id_2',
        damaged=False).put()
    device_model.Device(
        serial_number='Void', enrolled=False,
        device_model='HP Chromebook 13 G1', current_ou='/',
        shelf=self.shelf.key, chrome_device_id='unique_id_8',
        damaged=False).put()
    self.device = device_model.Device.get(serial_number='12321')
    self.device2 = device_model.Device.get(serial_number='67890')
    self.device3 = device_model.Device.get(serial_number='Void')

  def test_get_search_index(self):
    self.assertIsInstance(device_model.Device.get_index(), search.Index)

  def test_validate_asset_tag_required_on_enroll(self):
    config_model.Config.set('use_asset_tags', True)
    with self.assertRaisesWithLiteralMatch(
        datastore_errors.BadValueError, device_model._ASSET_TAGS_REQUIRED_MSG):
      device_model.Device.enroll(
          serial_number='test_serial', user_email=loanertest.USER_EMAIL)

  def enroll_test_device(self, device_to_enroll):
    self.patcher_directory = mock.patch.object(
        directory, 'DirectoryApiClient', autospec=True)
    self.mock_directoryclass = self.patcher_directory.start()
    self.addCleanup(self.patcher_directory.stop)
    self.mock_directoryclient = self.mock_directoryclass.return_value
    self.mock_directoryclient.get_chrome_device_by_serial.return_value = (
        device_to_enroll)
    default_ou = device_model.constants.ORG_UNIT_DICT.get('DEFAULT')
    self.test_device = device_model.Device.enroll(
        '123ABC', loanertest.USER_EMAIL, '123456')
    if device_to_enroll.get('orgUnitPath') != default_ou:
      assert self.mock_directoryclient.move_chrome_device_org_unit.called

  def test_identifier(self):

    # Devices without an asset tag should return the serial number.
    self.device.asset_tag = None
    self.assertEqual(self.device.serial_number, self.device.identifier)

    # Devices with an asset tag should return the asset tag.
    self.device.asset_tag = '123456'
    self.assertEqual(self.device.asset_tag, self.device.identifier)

  def test_enroll_new_device(self):
    self.enroll_test_device(loanertest.TEST_DIR_DEVICE1)
    self.enroll_test_device(loanertest.TEST_DIR_DEVICE_DEFAULT)

    self.test_device.set_last_reminder(0)
    self.assertEqual(self.test_device.last_reminder.level, 0)
    self.assertEqual(self.test_device.last_reminder.count, 1)
    self.assertIsInstance(
        self.test_device.last_reminder.time, datetime.datetime)

    # Check that count increments on second reminder of same level.
    self.test_device.set_last_reminder(0)
    self.assertEqual(self.test_device.last_reminder.level, 0)
    self.assertEqual(self.test_device.last_reminder.count, 2)

    next_reminder_delta = datetime.timedelta(hours=2)
    self.test_device.set_next_reminder(1, next_reminder_delta)
    self.assertTrue(self.test_device.next_reminder.time)
    self.assertEqual(self.test_device.next_reminder.level, 1)
    self.testbed.mock_raiseevent.assert_any_call(
        'device_enroll', device=self.test_device)

  @mock.patch.object(directory, 'DirectoryApiClient', autospec=True)
  def test_enroll_new_device_error(self, mock_directoryclass):
    err_message = 'Failed to move device'
    mock_directoryclient = mock_directoryclass.return_value
    mock_directoryclient.move_chrome_device_org_unit.side_effect = (
        directory.DirectoryRPCError(err_message))
    ou = constants.ORG_UNIT_DICT.get('DEFAULT')
    with self.assertRaisesRegexp(
        device_model.DeviceCreationError,
        device_model._FAILED_TO_MOVE_DEVICE_MSG % (
            '2346777', ou, err_message)):
      device_model.Device.enroll('2346777', loanertest.USER_EMAIL)

  @mock.patch.object(device_model.Device, 'to_document', autospec=True)
  @mock.patch.object(device_model, 'logging', autospec=True)
  @mock.patch.object(directory, 'DirectoryApiClient', autospec=True)
  def test_enroll_unenrolled_device(
      self, mock_directoryclass, mock_logging, mock_to_document):
    mock_directoryclient = mock_directoryclass.return_value
    mock_directoryclient.move_chrome_device_org_unit.return_value = (
        loanertest.TEST_DIR_DEVICE_DEFAULT)
    device = device_model.Device()
    device.enrolled = False
    device.model = 'HP Chromebook 13 G1'
    device.serial_number = '123ABC'
    device.chrome_device_id = 'unique_id'
    device.put()

    self.assertEqual(mock_to_document.call_count, 1)

    device = device_model.Device.enroll('123ABC', loanertest.USER_EMAIL)

    self.assertEqual(mock_logging.info.call_count, 2)

    retrieved_device = device_model.Device.get(serial_number='123ABC')
    self.assertTrue(retrieved_device.enrolled)
    self.testbed.mock_raiseevent.assert_any_call('device_enroll', device=device)

  @mock.patch.object(device_model, 'logging', autospec=True)
  @mock.patch.object(directory, 'DirectoryApiClient', autospec=True)
  def test_enroll_unenrolled_locked_device(
      self, mock_directoryclass, mock_logging):
    mock_directoryclient = mock_directoryclass.return_value
    mock_directoryclient.move_chrome_device_org_unit.return_value = (
        loanertest.TEST_DIR_DEVICE_DEFAULT)
    device = device_model.Device()
    device.locked = True
    device.enrolled = False
    device.model = 'HP Chromebook 13 G1'
    device.serial_number = '123ABC'
    device.chrome_device_id = 'unique_id'
    device.put()

    device = device_model.Device.enroll('123ABC', loanertest.USER_EMAIL)

    self.assertEqual(mock_logging.info.call_count, 3)

    retrieved_device = device_model.Device.get(serial_number='123ABC')
    self.assertTrue(retrieved_device.enrolled)
    self.testbed.mock_raiseevent.assert_any_call(
        'device_enroll_lost_or_locked', device=device)

  @mock.patch.object(device_model, 'logging', autospec=True)
  @mock.patch.object(directory, 'DirectoryApiClient', autospec=True)
  def test_enroll_unenrolled_lost_device(
      self, mock_directoryclass, mock_logging):
    mock_directoryclient = mock_directoryclass.return_value
    mock_directoryclient.move_chrome_device_org_unit.return_value = (
        loanertest.TEST_DIR_DEVICE_DEFAULT)
    device = device_model.Device()
    device.lost = True
    device.enrolled = False
    device.model = 'HP Chromebook 13 G1'
    device.serial_number = '123ABC'
    device.chrome_device_id = 'unique_id'
    device.put()

    device = device_model.Device.enroll('123ABC', loanertest.USER_EMAIL)

    self.assertEqual(mock_logging.info.call_count, 2)

    retrieved_device = device_model.Device.get(serial_number='123ABC')
    self.assertTrue(retrieved_device.enrolled)
    self.testbed.mock_raiseevent.assert_any_call(
        'device_enroll_lost_or_locked', device=device)

  @mock.patch.object(directory, 'DirectoryApiClient', autospec=True)
  def test_enroll_move_ou_error(self, mock_directoryclass):
    device = device_model.Device()
    device.enrolled = False
    device.model = 'HP Chromebook 13 G1'
    device.serial_number = '5467FD'
    device.chrome_device_id = 'unique_id_09'
    device.current_ou = 'not_default'
    device.put()
    err_message = 'Failed to move device'
    mock_directoryclient = mock_directoryclass.return_value
    mock_directoryclient.move_chrome_device_org_unit.side_effect = (
        directory.DirectoryRPCError(err_message))
    ou = constants.ORG_UNIT_DICT['DEFAULT']
    with self.assertRaisesRegexp(
        device_model.DeviceCreationError,
        device_model._FAILED_TO_MOVE_DEVICE_MSG % (
            '5467FD', ou, err_message)):
      device_model.Device.enroll('5467FD', loanertest.USER_EMAIL)

  @mock.patch.object(directory, 'DirectoryApiClient', autospec=True)
  def test_enroll_no_device_error(self, mock_directoryclass):
    serial_number = '5467FD'
    mock_directoryclient = mock_directoryclass.return_value
    mock_directoryclient.get_chrome_device_by_serial.side_effect = (
        directory.DeviceDoesNotExistError(
            directory._NO_DEVICE_MSG % serial_number))
    with self.assertRaisesRegexp(
        device_model.DeviceCreationError,
        directory._NO_DEVICE_MSG % serial_number):
      device_model.Device.enroll(serial_number, loanertest.USER_EMAIL)

  def test_unenroll_error(self):
    err_message = 'Failed to move device'
    self.enroll_test_device(loanertest.TEST_DIR_DEVICE_DEFAULT)
    self.mock_directoryclient.reset_mock()
    self.mock_directoryclient.move_chrome_device_org_unit.side_effect = (
        directory.DirectoryRPCError(err_message))
    unenroll_ou = config_model.Config.get('unenroll_ou')
    with self.assertRaisesRegexp(
        device_model.FailedToUnenrollError,
        device_model._FAILED_TO_MOVE_DEVICE_MSG % (
            self.test_device.identifier, unenroll_ou, err_message)):
      self.test_device.unenroll(loanertest.USER_EMAIL)

  def test_unenroll(self):
    self.enroll_test_device(loanertest.TEST_DIR_DEVICE_DEFAULT)
    self.test_device.unenroll(loanertest.USER_EMAIL)

    self.assertEqual(self.test_device.enrolled, False)
    self.assertEqual(self.test_device.assigned_user, None)
    self.assertEqual(self.test_device.assignment_date, None)
    self.assertEqual(self.test_device.due_date, None)
    self.assertEqual(self.test_device.last_reminder, None)
    self.assertEqual(self.test_device.next_reminder, None)
    self.assertEqual(self.test_device.current_ou, '/')
    self.assertEqual(self.test_device.mark_pending_return_date, None)
    self.mock_directoryclient.move_chrome_device_org_unit.assert_any_call(
        device_id=u'unique_id', org_unit_path='/')

  def test_list_by_user(self):
    self.device.assigned_user = loanertest.SUPER_ADMIN_EMAIL
    self.device.put()
    self.device2.assigned_user = loanertest.SUPER_ADMIN_EMAIL
    self.device2.put()
    devices = device_model.Device.list_by_user(loanertest.SUPER_ADMIN_EMAIL)
    self.assertListEqual(
        [device.serial_number for device in devices],
        [self.device.serial_number, self.device2.serial_number])

  def test_list_by_user_with_pending_return(self):
    self.device.assigned_user = loanertest.SUPER_ADMIN_EMAIL
    self.device.put()
    self.device2.assigned_user = loanertest.SUPER_ADMIN_EMAIL
    self.device2.mark_pending_return_date = datetime.datetime.utcnow()
    self.device2.put()
    devices = device_model.Device.list_by_user(loanertest.SUPER_ADMIN_EMAIL)
    self.assertListEqual(
        [device.serial_number for device in devices],
        [self.device.serial_number])

  @mock.patch.object(directory, 'DirectoryApiClient', autospec=True)
  def test_create_unenrolled(self, mock_directoryclass):
    """Test creating an unenrolled device."""
    mock_directoryclient = mock_directoryclass.return_value
    mock_directoryclient.get_chrome_device.return_value = (
        loanertest.TEST_DIR_DEVICE1)
    created_device = device_model.Device.create_unenrolled(
        loanertest.TEST_DIR_DEVICE1[directory.DEVICE_ID],
        loanertest.USER_EMAIL)

    self.assertEqual(
        created_device.serial_number,
        loanertest.TEST_DIR_DEVICE1[directory.SERIAL_NUMBER])

    mock_directoryclient.get_chrome_device.assert_called_with(
        loanertest.TEST_DIR_DEVICE1[directory.DEVICE_ID])
    retrieved_device = device_model.Device.get(
        chrome_device_id=loanertest.TEST_DIR_DEVICE1[directory.DEVICE_ID])
    self.assertFalse(retrieved_device.enrolled)

  @mock.patch.object(directory, 'DirectoryApiClient', autospec=True)
  def test_create_unenrolled_incomplete_info(self, mock_directoryclass):
    """Test create unenrolled without all info, raises DeviceCreationError."""
    mock_directoryclient = mock_directoryclass.return_value
    mock_directoryclient.get_chrome_device.return_value = {
        directory.SERIAL_NUMBER: ''}

    with self.assertRaisesRegexp(
        device_model.DeviceCreationError,
        device_model._DIRECTORY_INFO_INCOMPLETE_MSG):
      device_model.Device.create_unenrolled(
          loanertest.TEST_DIR_DEVICE1[directory.DEVICE_ID],
          loanertest.USER_EMAIL)

  def test_get(self):
    test_devices = [
        device_model.Device(
            asset_tag='asset_tag_{}'.format(str(number)),
            chrome_device_id='chrome_id_{}'.format(str(number)),
            serial_number='serial_number_{}'.format(str(number))
        ) for number in xrange(3)]

    for device in test_devices:
      device.put()

    with self.assertRaises(device_model.DeviceIdentifierError):
      device_model.Device.get()  # No args.

    self.assertEqual(
        device_model.Device.get(asset_tag='asset_tag_0').serial_number,
        'serial_number_0')
    self.assertEqual(
        device_model.Device.get(serial_number='serial_number_1').asset_tag,
        'asset_tag_1')
    self.assertEqual(
        device_model.Device.get(chrome_device_id='chrome_id_2').asset_tag,
        'asset_tag_2')

    # Unknown_identifier is can take either an asset tag or serial number.
    self.assertEqual(
        device_model.Device.get(unknown_identifier='asset_tag_0').asset_tag,
        'asset_tag_0')
    self.assertEqual(
        device_model.Device.get(
            unknown_identifier='serial_number_1').serial_number,
        'serial_number_1')

  def test_calculate_return_dates(self):
    now = datetime.datetime.utcnow()
    self.enroll_test_device(loanertest.TEST_DIR_DEVICE_DEFAULT)
    self.test_device.assigned_user = loanertest.USER_EMAIL
    self.test_device.assignment_date = now
    config_model.Config.set('loan_duration', 3)
    config_model.Config.set('maximum_loan_duration', 14)

    dates = self.test_device.calculate_return_dates()

    self.assertIsInstance(dates, device_model.ReturnDates)
    self.assertEqual(dates.default, now + datetime.timedelta(days=3))
    self.assertEqual(dates.max, now + datetime.timedelta(days=14))

  def test_calculate_return_dates_raises_if_not_assigned(self):
    self.enroll_test_device(loanertest.TEST_DIR_DEVICE_DEFAULT)
    self.test_device.assigned_user = None
    self.test_device.put()

    with self.assertRaisesRegexp(
        device_model.ReturnDatesCalculationError,
        device_model._NOT_ASSIGNED_MSG):
      self.test_device.calculate_return_dates()

  @mock.patch.object(device_model, 'events', autospec=True)
  def test_loan_assign(self, mock_events):
    self.enroll_test_device(loanertest.TEST_DIR_DEVICE_DEFAULT)
    self.test_device.shelf = self.shelf.key
    self.test_device.put()

    self.assertEqual(mock_events.raise_event.call_count, 1)
    mock_events.reset_mock()

    self.test_device.loan_assign(loanertest.SUPER_ADMIN_EMAIL)

    retrieved_device = device_model.Device.get(serial_number='123ABC')
    self.assertEqual(
        retrieved_device.assigned_user, loanertest.SUPER_ADMIN_EMAIL)
    self.assertTrue(retrieved_device.assignment_date)
    self.assertEqual(retrieved_device.mark_pending_return_date, None)
    self.assertEqual(
        retrieved_device.due_date,
        self.test_device.calculate_return_dates().default)
    self.assertIsNone(self.test_device.shelf)

    self.assertEqual(mock_events.raise_event.call_count, 2)
    mock_events.reset_mock()

    # Start new assignment
    self.test_device.loan_assign(loanertest.USER_EMAIL)
    retrieved_device = device_model.Device.get(serial_number='123ABC')
    self.assertEqual(retrieved_device.assigned_user, loanertest.USER_EMAIL)
    self.assertEqual(mock_events.raise_event.call_count, 4)

  def test_resume_loan(self):
    """Test that a loan resumes when marked as pending return."""
    self.enroll_test_device(loanertest.TEST_DIR_DEVICE_DEFAULT)
    self.test_device.mark_pending_return_date = datetime.datetime.utcnow()
    self.test_device.resume_loan(loanertest.USER_EMAIL)
    self.assertIsNone(self.test_device.mark_pending_return_date)

  @mock.patch.object(device_model.Device, 'resume_loan', autospec=True)
  def test_loan_resumes_if_late(self, mock_resume_loan):
    """Tests loan resumption within and outside the post-return grace period."""
    config_model.Config.set('return_grace_period', 15)
    self.enroll_test_device(loanertest.TEST_DIR_DEVICE_DEFAULT)

    assign_time = datetime.datetime(year=2017, month=1, day=1)
    resume_time = datetime.datetime(year=2017, month=1, day=2)
    within_grace_period = datetime.timedelta(
        minutes=config_model.Config.get('return_grace_period') - 1)
    beyond_grace_period = datetime.timedelta(
        minutes=config_model.Config.get('return_grace_period') + 1)

    with freezegun.freeze_time(assign_time):
      self.test_device.loan_assign(loanertest.USER_EMAIL)

    # User reports pending return.
    with freezegun.freeze_time(resume_time):
      self.test_device.mark_pending_return(loanertest.USER_EMAIL)

    # Heartbeat arrives a minute before end of grace period, s'allright.
    with freezegun.freeze_time(resume_time + within_grace_period):
      self.test_device.loan_resumes_if_late(loanertest.USER_EMAIL)
      assert mock_resume_loan.call_count == 0

    # Heartbeat arrives a minute later, no dice.
    with freezegun.freeze_time(resume_time + beyond_grace_period):
      self.test_device.loan_resumes_if_late(loanertest.USER_EMAIL)
      assert mock_resume_loan.call_count == 1

  def test_loan_assign_unenrolled(self):
    self.enroll_test_device(loanertest.TEST_DIR_DEVICE_DEFAULT)
    self.test_device.enrolled = False
    self.test_device.put()
    self.assertRaises(
        device_model.AssignmentError, self.test_device.loan_assign,
        'jessicajones@{}'.format(loanertest.USER_DOMAIN))

  def test_extend(self):
    now = datetime.datetime(year=2017, month=1, day=1)
    self.enroll_test_device(loanertest.TEST_DIR_DEVICE_DEFAULT)
    config_model.Config.set('loan_duration', 3)
    config_model.Config.set('maximum_loan_duration', 14)
    requested_extension = datetime.datetime(year=2017, month=1, day=5)

    with freezegun.freeze_time(now):
      self.test_device.loan_assign(loanertest.USER_EMAIL)
      self.test_device.loan_extend(loanertest.USER_EMAIL, requested_extension)

    self.assertEqual(self.test_device.due_date, requested_extension)

  def test_extend_unassigned(self):
    self.enroll_test_device(loanertest.TEST_DIR_DEVICE_DEFAULT)
    with self.assertRaisesWithLiteralMatch(
        device_model.UnassignedDeviceError,
        device_model._UNASSIGNED_DEVICE):
      self.test_device.loan_extend(
          loanertest.USER_EMAIL, datetime.datetime.utcnow())

  def test_extend_past_date(self):
    now = datetime.datetime(year=2017, month=1, day=1)
    self.enroll_test_device(loanertest.TEST_DIR_DEVICE_DEFAULT)
    config_model.Config.set('loan_duration', 3)
    config_model.Config.set('maximum_loan_duration', 14)
    requested_extension = datetime.datetime(year=2016, month=1, day=1)

    with freezegun.freeze_time(now):
      self.test_device.loan_assign('test@{}'.format(loanertest.USER_DOMAIN))
      self.assertRaises(
          device_model.ExtendError, self.test_device.loan_extend,
          'test@{}'.format(loanertest.USER_DOMAIN), requested_extension)

  def test_extend_outside_range(self):
    now = datetime.datetime(year=2017, month=1, day=1)
    self.enroll_test_device(loanertest.TEST_DIR_DEVICE_DEFAULT)
    config_model.Config.set('loan_duration', 3)
    config_model.Config.set('maximum_loan_duration', 14)
    requested_extension = datetime.datetime(year=2017, month=3, day=1)

    with freezegun.freeze_time(now):
      self.test_device.loan_assign(loanertest.USER_EMAIL)
      self.assertRaises(
          device_model.ExtendError, self.test_device.loan_extend,
          'test@{}'.format(loanertest.USER_DOMAIN), requested_extension)

  @mock.patch.object(device_model.Device, 'unlock', autospec=True)
  def test_loan_return(self, mock_unlock):
    user_email = loanertest.USER_EMAIL
    self.enroll_test_device(loanertest.TEST_DIR_DEVICE_DEFAULT)
    self.test_device.assigned_user = user_email
    self.test_device.assignment_date = (
        datetime.datetime(year=2017, month=1, day=1))
    self.test_device.due_date = (
        datetime.datetime(year=2017, month=1, day=5))
    self.test_device.lost = True
    self.test_device.locked = True

    self.test_device._loan_return(user_email)

    retrieved_device = device_model.Device.get(serial_number='123ABC')
    self.assertIsNone(retrieved_device.assigned_user)
    self.assertIsNone(retrieved_device.assignment_date)
    self.assertIsNone(retrieved_device.due_date)
    self.assertFalse(retrieved_device.lost)
    self.assertIsNone(retrieved_device.last_reminder)
    self.assertIsNone(retrieved_device.next_reminder)
    self.assertEqual(mock_unlock.call_count, 1)

  def test_lock_and_unlock(self):
    self.enroll_test_device(loanertest.TEST_DIR_DEVICE_DEFAULT)
    self.test_device.lock(loanertest.USER_EMAIL)
    retrieved_device = device_model.Device.get(serial_number='123ABC')
    self.mock_directoryclient.disable_chrome_device.assert_called_with(
        self.test_device.chrome_device_id)
    self.assertTrue(retrieved_device.locked)

    self.mock_directoryclient.reset_mock()
    self.test_device.unlock(loanertest.USER_EMAIL)
    retrieved_device = device_model.Device.get(serial_number='123ABC')
    self.mock_directoryclient.reenable_chrome_device.assert_called_with(
        self.test_device.chrome_device_id)
    self.assertFalse(retrieved_device.locked)

  @mock.patch.object(device_model, 'logging', autospec=True)
  def test_already_locked_device(self, mock_logging):
    self.enroll_test_device(loanertest.TEST_DIR_DEVICE_DEFAULT)
    self.mock_directoryclient.disable_chrome_device.side_effect = (
        directory.DeviceAlreadyDisabledError)
    self.test_device.lock(loanertest.USER_EMAIL)
    self.assertEqual(mock_logging.error.call_count, 1)

  def test_record_heartbeat(self):
    self.enroll_test_device(loanertest.TEST_DIR_DEVICE_DEFAULT)
    now = datetime.datetime(year=2017, month=1, day=1)
    with freezegun.freeze_time(now):
      self.test_device.record_heartbeat()
      self.assertEqual(now, self.test_device.last_heartbeat)
      self.assertEqual(now, self.test_device.last_known_healthy)

  def test_mark_pending_return(self):
    self.enroll_test_device(loanertest.TEST_DIR_DEVICE_DEFAULT)
    self.test_device.assigned_user = loanertest.USER_EMAIL
    self.test_device.put()
    self.test_device.mark_pending_return(loanertest.USER_EMAIL)
    self.assertTrue(isinstance(
        self.test_device.mark_pending_return_date, datetime.datetime))

  def test_mark_pending_return_unassigned(self):
    self.enroll_test_device(loanertest.TEST_DIR_DEVICE_DEFAULT)
    with self.assertRaisesWithLiteralMatch(
        device_model.UnassignedDeviceError,
        device_model._UNASSIGNED_DEVICE):
      self.test_device.mark_pending_return(loanertest.USER_EMAIL)

  def test_mark_damaged_without_reason(self):
    self.enroll_test_device(loanertest.TEST_DIR_DEVICE_DEFAULT)
    self.test_device.mark_damaged(user_email=loanertest.USER_EMAIL)
    self.assertTrue(self.test_device.damaged)
    self.assertEqual(self.test_device.damaged_reason, 'No reason provided')

  def test_mark_damaged_with_reason(self):
    reason = 'Broken usb port'
    self.enroll_test_device(loanertest.TEST_DIR_DEVICE_DEFAULT)
    self.test_device.mark_damaged(
        user_email=loanertest.USER_EMAIL, damaged_reason=reason)
    self.assertTrue(self.test_device.damaged)
    self.assertEqual(self.test_device.damaged_reason, reason)

  def test_mark_lost(self):
    self.enroll_test_device(loanertest.TEST_DIR_DEVICE_DEFAULT)
    with mock.patch.object(
        self.test_device, 'lock', autospec=True) as mock_lock:
      self.test_device.mark_lost(user_email=loanertest.USER_EMAIL)
      self.assertTrue(self.test_device.lost)
      self.assertEqual(mock_lock.call_count, 1)

  @mock.patch.object(deferred, 'defer', autospec=True)
  def test_enable_guest_mode_allowed(self, mock_defer):
    now = datetime.datetime(year=2017, month=1, day=1)
    config_model.Config.set('allow_guest_mode', True)
    self.enroll_test_device(loanertest.TEST_DIR_DEVICE_DEFAULT)

    with freezegun.freeze_time(now):
      self.test_device.assigned_user = loanertest.USER_EMAIL
      self.test_device.put()
      self.test_device.enable_guest_mode(loanertest.USER_EMAIL)
      self.assertEqual(
          device_model.constants.ORG_UNIT_DICT['GUEST'],
          self.test_device.current_ou)
      self.assertEqual(now, self.test_device.ou_changed_date)
      config_model.Config.set(
          'guest_mode_timeout_in_hours', 12)
      countdown = datetime.timedelta(
          hours=config_model.Config.get(
              'guest_mode_timeout_in_hours')).total_seconds()
      mock_defer.assert_called_once_with(
          self.test_device._disable_guest_mode, loanertest.USER_EMAIL,
          _countdown=countdown)

  def test_enable_guest_mode_unassigned(self):
    config_model.Config.set('allow_guest_mode', False)
    self.enroll_test_device(loanertest.TEST_DIR_DEVICE_DEFAULT)
    with self.assertRaisesWithLiteralMatch(
        device_model.UnassignedDeviceError,
        device_model._UNASSIGNED_DEVICE):
      self.test_device.enable_guest_mode(loanertest.USER_EMAIL)

  def test_enable_guest_mode_not_allowed(self):
    config_model.Config.set('allow_guest_mode', False)
    self.enroll_test_device(loanertest.TEST_DIR_DEVICE_DEFAULT)
    self.test_device.assigned_user = loanertest.USER_EMAIL
    self.test_device.put()
    with self.assertRaisesWithLiteralMatch(
        device_model.GuestNotAllowedError,
        device_model._GUEST_MODE_DISABLED_MSG):
      self.test_device.enable_guest_mode(loanertest.USER_EMAIL)
    self.assertEqual(
        device_model.constants.ORG_UNIT_DICT['DEFAULT'],
        self.test_device.current_ou)

  def test_enable_guest_mode_failure(self):
    self.enroll_test_device(loanertest.TEST_DIR_DEVICE_DEFAULT)
    self.test_device.assigned_user = loanertest.USER_EMAIL
    self.test_device.put()
    self.mock_directoryclient.reset_mock()
    self.mock_directoryclient.move_chrome_device_org_unit.side_effect = (
        directory.DirectoryRPCError('Guest move failed.'))
    config_model.Config.set('allow_guest_mode', True)

    with self.assertRaisesWithLiteralMatch(
        device_model.EnableGuestError,
        'Guest move failed.'):
      self.test_device.enable_guest_mode(loanertest.USER_EMAIL)
    self.assertNotEqual(
        device_model.constants.ORG_UNIT_DICT['GUEST'],
        self.test_device.current_ou)

  def test_disable_guest_mode(self):
    now = datetime.datetime(year=2017, month=1, day=1)
    self.enroll_test_device(loanertest.TEST_DIR_DEVICE_DEFAULT)
    self.test_device.current_ou = constants.ORG_UNIT_DICT['GUEST']
    self.test_device.assigned_user = loanertest.USER_EMAIL
    self.test_device.put()

    with freezegun.freeze_time(now):
      self.test_device._disable_guest_mode(loanertest.USER_EMAIL)
      self.assertEqual(
          constants.ORG_UNIT_DICT['DEFAULT'],
          self.test_device.current_ou)
      self.assertEqual(now, self.test_device.ou_changed_date)

  def test_disable_guest_mode_fail_to_move(self):
    self.enroll_test_device(loanertest.TEST_DIR_DEVICE_DEFAULT)
    self.test_device.current_ou = constants.ORG_UNIT_DICT['GUEST']
    self.test_device.assigned_user = loanertest.USER_EMAIL
    self.test_device.put()
    err_message = 'Failed to move device'
    self.mock_directoryclient.reset_mock()
    self.mock_directoryclient.move_chrome_device_org_unit.side_effect = (
        directory.DirectoryRPCError(err_message))
    with self.assertRaisesRegexp(
        device_model.UnableToMoveToDefaultOUError,
        device_model._FAILED_TO_MOVE_DEVICE_MSG % (
            self.test_device.identifier, constants.ORG_UNIT_DICT['DEFAULT'],
            err_message)):
      self.test_device._disable_guest_mode(loanertest.USER_EMAIL)

  def test_disable_guest_mode_no_change(self):
    self.enroll_test_device(loanertest.TEST_DIR_DEVICE_DEFAULT)
    self.mock_directoryclient.reset_mock()
    self.test_device._disable_guest_mode(loanertest.USER_EMAIL)
    self.assertFalse(self.mock_directoryclient.called)

  def test_device_audit_check_device_not_active(self):
    self.enroll_test_device(loanertest.TEST_DIR_DEVICE_DEFAULT)
    self.test_device.enrolled = False
    with self.assertRaisesRegexp(
        device_model.DeviceNotEnrolledError,
        device_model.DEVICE_NOT_ENROLLED_MSG % (
            self.test_device.identifier)):
      self.test_device.device_audit_check()

  def test_device_audit_check_device_is_damaged(self):
    self.enroll_test_device(loanertest.TEST_DIR_DEVICE_DEFAULT)
    self.test_device.damaged = True
    with self.assertRaisesRegexp(
        device_model.UnableToMoveToShelfError,
        device_model._DEVICE_DAMAGED_MSG % (
            self.test_device.identifier)):
      self.test_device.device_audit_check()

  def test_place_device_on_shelf_is_not_active(self):
    self.enroll_test_device(loanertest.TEST_DIR_DEVICE_DEFAULT)
    self.shelf.enabled = False
    self.shelf.put()
    self.assertRaisesRegexp(
        device_model.UnableToMoveToShelfError, 'Unable to check device',
        self.test_device.move_to_shelf, self.shelf, loanertest.USER_EMAIL)

  @mock.patch.object(device_model, 'logging', autospec=True)
  def test_move_to_shelf(self, mock_logging):
    self.enroll_test_device(loanertest.TEST_DIR_DEVICE_DEFAULT)
    now = datetime.datetime(year=2017, month=1, day=1)
    with freezegun.freeze_time(now):
      self.test_device.move_to_shelf(
          shelf=self.shelf, user_email=loanertest.USER_EMAIL)
      self.assertTrue(self.test_device.is_on_shelf)
      self.assertEqual(mock_logging.info.call_count, 2)
      self.assertEqual(now, self.test_device.last_known_healthy)

  def test_remove_from_shelf(self):
    self.enroll_test_device(loanertest.TEST_DIR_DEVICE_DEFAULT)
    self.test_device.shelf = self.shelf.key
    self.assertTrue(self.test_device.shelf is not None)
    self.test_device.remove_from_shelf(
        shelf=self.shelf, user_email=loanertest.USER_EMAIL)
    self.assertIsNone(self.test_device.shelf)


if __name__ == '__main__':
  loanertest.main()
