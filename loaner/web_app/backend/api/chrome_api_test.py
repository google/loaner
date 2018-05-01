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

"""Tests for backend.api.chrome_api."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import datetime

import freezegun
import mock

import endpoints

from loaner.web_app.backend.api import chrome_api
from loaner.web_app.backend.api.messages import chrome_message
from loaner.web_app.backend.clients import directory  # pylint: disable=unused-import
from loaner.web_app.backend.models import config_model
from loaner.web_app.backend.models import device_model
from loaner.web_app.backend.testing import loanertest

UNIQUE_ID = 'unique_id'
ASSET_TAG = 'ABCDEF'
SERIAL_NUMBER = '123456'


class ChromeEndpointsTest(loanertest.EndpointsTestCase):
  """Tests the Chrome endpoints api."""

  def setUp(self):
    super(ChromeEndpointsTest, self).setUp()
    self.patcher_directory = mock.patch('__main__.directory.DirectoryApiClient')
    self.mock_directoryclass = self.patcher_directory.start()
    self.mock_directoryclient = self.mock_directoryclass.return_value
    self.addCleanup(self.patcher_directory.stop)
    self.service = chrome_api.ChromeApi()
    self.login_endpoints_user()
    self.chrome_request = chrome_message.HeartbeatRequest(device_id=UNIQUE_ID)

  def tearDown(self):
    super(ChromeEndpointsTest, self).tearDown()
    self.service = None

  def create_device(self, enrolled=True, assigned_user=None, asset_tag=None):
    loan_resumes_if_late_patcher = mock.patch.object(
        device_model.Device, 'loan_resumes_if_late')
    loan_resumes_if_late_patcher.start()
    self.device = device_model.Device(
        asset_tag=asset_tag,
        serial_number=SERIAL_NUMBER,
        enrolled=enrolled,
        device_model='HP Chromebook 13 G1',
        current_ou='/',
        chrome_device_id=UNIQUE_ID)
    self.device.put()

    self.mock_loan_resumes_if_late = self.device.loan_resumes_if_late

    if assigned_user:
      self.device.loan_assign(assigned_user)

  def test_heartbeat_no_device_id(self):
    """Tests heartbeat without a request.device_id."""
    with self.assertRaisesRegexp(
        endpoints.BadRequestException,
        chrome_api._NO_DEVICE_ID_MSG):
      self.service.heartbeat(chrome_message.HeartbeatRequest())

  def test_heartbeat_unassigned_device(self):
    """Tests heartbeat processing for a unassigned, enrolled device."""
    self.create_device()

    response = self.service.heartbeat(self.chrome_request)
    self.assertIsInstance(response, chrome_message.HeartbeatResponse)
    self.assertEqual(response.is_enrolled, True)
    self.assertEqual(response.start_assignment, True)
    assert not self.mock_loan_resumes_if_late.called

  def test_heartbeat_assigned_device(self):
    """Tests heartbeat processing for an assigned, enrolled device."""
    self.create_device(
        assigned_user='previous-user{}'.format(loanertest.USER_DOMAIN))

    response = self.service.heartbeat(self.chrome_request)
    self.assertIsInstance(response, chrome_message.HeartbeatResponse)
    self.assertEqual(response.is_enrolled, True)
    self.assertEqual(response.start_assignment, True)
    device = device_model.Device.get(chrome_device_id=UNIQUE_ID)
    self.assertEqual(device.assigned_user, loanertest.USER_EMAIL)
    assert not self.mock_loan_resumes_if_late.called

  def test_heartbeat_assignment_unchanged(self):
    """Tests heartbeat processing for an unchanged assignment."""
    self.create_device(assigned_user=loanertest.USER_EMAIL)

    response = self.service.heartbeat(self.chrome_request)
    self.assertIsInstance(response, chrome_message.HeartbeatResponse)
    self.assertEqual(response.is_enrolled, True)
    self.assertEqual(response.start_assignment, False)
    self.mock_loan_resumes_if_late.assert_called_once_with(
        loanertest.USER_EMAIL)

  def test_heartbeat_unenrolled_device_with_entity(self):
    """Tests heartbeat processing for an unenrolled device with an entity."""
    self.create_device(enrolled=False)

    response = self.service.heartbeat(self.chrome_request)
    self.assertIsInstance(response, chrome_message.HeartbeatResponse)
    self.assertEqual(response.is_enrolled, False)
    self.assertEqual(response.start_assignment, False)
    device = device_model.Device.get(chrome_device_id=UNIQUE_ID)
    self.assertEqual(device.assigned_user, None)
    assert not self.mock_loan_resumes_if_late.called

  def test_heartbeat_unenrolled_device_without_entity(self):
    """Tests heartbeat processing for an unenrolled device with no entity."""
    self.mock_directoryclient.get_chrome_device.return_value = (
        loanertest.TEST_DIR_DEVICE1)

    response = self.service.heartbeat(self.chrome_request)
    self.assertIsInstance(response, chrome_message.HeartbeatResponse)
    self.assertEqual(response.is_enrolled, False)
    self.assertEqual(response.start_assignment, False)

    device = device_model.Device.get(chrome_device_id=UNIQUE_ID)
    self.assertEqual(device.serial_number, SERIAL_NUMBER)
    self.assertEqual(device.assigned_user, None)
    self.assertTrue(device.last_heartbeat)

  def test_heartbeat_nonexistent_device(self):
    """Tests heartbeat processing for a nonexistent (in directory) device."""
    self.mock_directoryclient.get_chrome_device.return_value = None

    self.assertRaisesRegexp(
        endpoints.NotFoundException,
        'Device ID not found in org.',
        self.service.heartbeat, self.chrome_request)

  def test_get_loan(self):
    """Tests the get loan function for an existing device."""
    given_name = 'Dare Devil'
    self.mock_directoryclient.given_name.return_value = given_name
    now = datetime.datetime(year=2017, month=1, day=1)
    with freezegun.freeze_time(now):
      config_model.Config.set('loan_duration', 3)
      config_model.Config.set('maximum_loan_duration', 14)
      # Set guest mode to unpermitted.
      config_model.Config.set('allow_guest_mode', False)
      self.create_device(assigned_user=loanertest.USER_EMAIL)

      response = self.service.get_loan(
          chrome_message.LoanRequest(
              device_id=UNIQUE_ID, need_name=True))
      self.assertIsInstance(response, chrome_message.LoanResponse)
      self.assertEqual(response.due_date, now + datetime.timedelta(days=3))
      self.assertEqual(
          response.max_extend_date, now + datetime.timedelta(days=14))
      self.assertEqual(response.given_name, given_name)
      self.assertFalse(response.guest_permitted)
      self.assertFalse(response.guest_enabled)

  def test_get_loan_with_no_given_name(self):
    """Tests the get loan function when the user has no given name."""
    self.mock_directoryclient.given_name.side_effect = (
        directory.GivenNameDoesNotExistError('No name!'))
    now = datetime.datetime(year=2017, month=1, day=1)
    with freezegun.freeze_time(now):
      config_model.Config.set('loan_duration', 3)
      config_model.Config.set('maximum_loan_duration', 14)
      # Set guest mode to permitted.
      config_model.Config.set('allow_guest_mode', True)
      self.create_device(assigned_user=loanertest.USER_EMAIL)

      response = self.service.get_loan(
          chrome_message.LoanRequest(device_id=UNIQUE_ID, need_name=True))
      self.assertIsInstance(response, chrome_message.LoanResponse)
      self.assertEqual(response.due_date, now + datetime.timedelta(days=3))
      self.assertEqual(
          response.max_extend_date, now + datetime.timedelta(days=14))
      self.assertIsNone(response.given_name)
      self.assertTrue(response.guest_permitted)
      self.assertFalse(response.guest_enabled)

  def test_get_loan_without_given_name(self):
    """Tests the get loan function when the given name is not needed."""
    self.mock_directoryclient.given_name.side_effect = (
        directory.DirectoryRPCError('No name!'))
    now = datetime.datetime(year=2017, month=1, day=1)
    with freezegun.freeze_time(now):
      config_model.Config.set('loan_duration', 3)
      config_model.Config.set('maximum_loan_duration', 14)
      self.create_device(assigned_user=loanertest.USER_EMAIL)

      response = self.service.get_loan(
          chrome_message.LoanRequest(device_id=UNIQUE_ID, need_name=False))
      self.assertIsInstance(response, chrome_message.LoanResponse)
      self.assertEqual(response.due_date, now + datetime.timedelta(days=3))
      self.assertEqual(
          response.max_extend_date, now + datetime.timedelta(days=14))
      self.assertIsNone(response.given_name)
      self.assertFalse(response.guest_enabled)

  def test_get_loan_no_device_id(self):
    """Tests get loan without a request.device_id."""
    with self.assertRaisesRegexp(
        endpoints.BadRequestException,
        chrome_api._NO_DEVICE_ID_MSG):
      self.service.get_loan(chrome_message.LoanRequest())

  def test_get_loan_no_device_found(self):
    """Tests get loan for a device not in datastore."""
    with self.assertRaisesRegexp(
        endpoints.NotFoundException,
        chrome_api._NOT_GNG_MSG):
      self.service.get_loan(
          chrome_message.LoanRequest(device_id='non_unique_id'))


if __name__ == '__main__':
  loanertest.main()
