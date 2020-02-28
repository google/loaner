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

# Lint as: python3
"""Tests for web_app.backend.api.messages.device_messages."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import datetime

from loaner.web_app.backend.api.messages import device_messages
from absl.testing import absltest


class DeviceMessagesPy23MigrationTest(absltest.TestCase):

  def testReminder(self):
    now = datetime.datetime.now()
    reminder = device_messages.Reminder(level=2, time=now, count=4)

    self.assertEqual(reminder.level, 2)
    self.assertEqual(reminder.time, now)
    self.assertEqual(reminder.count, 4)

  def testDeviceRequest(self):
    device_request = device_messages.DeviceRequest(
        asset_tag='FAKE-TAG',
        chrome_device_id='FAKE-CHROME-DEVICE-ID',
        serial_number='FAKE-SERIAL-NUMBER',
        urlkey='FAKE-URL-KEY',
        identifier='FAKE-IDENTIFIER')

    self.assertEqual(device_request.asset_tag, 'FAKE-TAG')
    self.assertEqual(device_request.chrome_device_id, 'FAKE-CHROME-DEVICE-ID')
    self.assertEqual(device_request.serial_number, 'FAKE-SERIAL-NUMBER')
    self.assertEqual(device_request.urlkey, 'FAKE-URL-KEY')
    self.assertEqual(device_request.identifier, 'FAKE-IDENTIFIER')

  def testDevice(self):
    due_date = datetime.datetime.now()
    last_heartbeat = datetime.datetime.now()
    assignment_date = datetime.datetime.now()
    ou_changed_date = datetime.datetime.now()
    last_known_healthy = datetime.datetime.now()
    mark_pending_return_date = datetime.datetime.now()
    max_extend_date = datetime.datetime.now()

    device = device_messages.Device(
        serial_number='FAKE-SERIAL-NUMBER',
        asset_tag='FAKE-TAG',
        identifier='FAKE-IDENTIFIER',
        urlkey='FAKE-URL-KEY',
        enrolled=False,
        device_model='FAKE-DEVICE-MODEL',
        due_date=due_date,
        last_known_healthy=last_known_healthy,
        assigned_user='FAKE-ASSIGNED-USER',
        assignment_date=assignment_date,
        current_ou='FAKE-CURRENT-OU',
        ou_changed_date=ou_changed_date,
        locked=True,
        lost=True,
        mark_pending_return_date=mark_pending_return_date,
        chrome_device_id='FAKE-CHROME-DEVICE-ID',
        last_heartbeat=last_heartbeat,
        damaged=True,
        damaged_reason='FAKE-DAMAGED-REASON',
        page_token='FAKE-PAGE-TOKEN',
        page_size=50,
        max_extend_date=max_extend_date,
        guest_enabled=False,
        guest_permitted=True,
        given_name='FAKE-GIVEN-NAME',
        overdue=True,
        onboarded=True)

    self.assertTrue(device.lost)
    self.assertTrue(device.locked)
    self.assertTrue(device.overdue)
    self.assertTrue(device.damaged)
    self.assertFalse(device.enrolled)
    self.assertTrue(device.onboarded)
    self.assertEqual(device.page_size, 50)
    self.assertFalse(device.guest_enabled)
    self.assertTrue(device.guest_permitted)
    self.assertEqual(device.due_date, due_date)

    self.assertEqual(device.asset_tag, 'FAKE-TAG')
    self.assertEqual(device.urlkey, 'FAKE-URL-KEY')
    self.assertEqual(device.identifier, 'FAKE-IDENTIFIER')
    self.assertEqual(device.current_ou, 'FAKE-CURRENT-OU')
    self.assertEqual(device.page_token, 'FAKE-PAGE-TOKEN')
    self.assertEqual(device.given_name, 'FAKE-GIVEN-NAME')
    self.assertEqual(device.last_heartbeat, last_heartbeat)
    self.assertEqual(device.assignment_date, assignment_date)
    self.assertEqual(device.ou_changed_date, ou_changed_date)
    self.assertEqual(device.max_extend_date, max_extend_date)
    self.assertEqual(device.device_model, 'FAKE-DEVICE-MODEL')
    self.assertEqual(device.serial_number, 'FAKE-SERIAL-NUMBER')
    self.assertEqual(device.assigned_user, 'FAKE-ASSIGNED-USER')
    self.assertEqual(device.damaged_reason, 'FAKE-DAMAGED-REASON')
    self.assertEqual(device.last_known_healthy, last_known_healthy)
    self.assertEqual(device.chrome_device_id, 'FAKE-CHROME-DEVICE-ID')
    self.assertEqual(device.mark_pending_return_date, mark_pending_return_date)

  def testListDevicesResponse(self):
    device1 = device_messages.Device(serial_number='FAKE-DEVICE-SERIAL-1')
    device2 = device_messages.Device(serial_number='FAKE-DEVICE-SERIAL-2')
    list_device_resp = device_messages.ListDevicesResponse(
        devices=[device1, device2],
        has_additional_results=True,
        page_token='FAKE-PAGE-TOKEN')

    self.assertTrue(list_device_resp.has_additional_results)
    self.assertEqual(list_device_resp.devices[0].serial_number,
                     'FAKE-DEVICE-SERIAL-1')
    self.assertEqual(list_device_resp.devices[1].serial_number,
                     'FAKE-DEVICE-SERIAL-2')
    self.assertEqual(list_device_resp.page_token, 'FAKE-PAGE-TOKEN')

  def testDamagedRequest(self):
    device = device_messages.DeviceRequest(asset_tag='FAKE-TAG')
    damaged_request = device_messages.DamagedRequest(
        device=device, damaged_reason='FAKE-DAMAGED-REASON')

    self.assertEqual(damaged_request.device.asset_tag, 'FAKE-TAG')
    self.assertEqual(damaged_request.damaged_reason, 'FAKE-DAMAGED-REASON')

  def testExtendLoanRequest(self):
    now = datetime.datetime.now()
    device = device_messages.DeviceRequest(asset_tag='FAKE-TAG')
    extend_loan_req = device_messages.ExtendLoanRequest(
        device=device, extend_date=now)

    self.assertEqual(extend_loan_req.extend_date, now)
    self.assertEqual(extend_loan_req.device.asset_tag, 'FAKE-TAG')

  def testListUserDeviceResponse(self):
    device1 = device_messages.Device(serial_number='FAKE-DEVICE-SERIAL-1')
    device2 = device_messages.Device(serial_number='FAKE-DEVICE-SERIAL-2')

    list_device_resp = device_messages.ListUserDeviceResponse(
        devices=[device1, device2])

    self.assertEqual(list_device_resp.devices[0].serial_number,
                     'FAKE-DEVICE-SERIAL-1')
    self.assertEqual(list_device_resp.devices[1].serial_number,
                     'FAKE-DEVICE-SERIAL-2')

  def testHistoryRequest(self):
    hist_req = device_messages.HistoryRequest(
        device=device_messages.DeviceRequest(asset_tag='FAKE-DEVICE-TAG'))

    self.assertEqual(hist_req.device.asset_tag, 'FAKE-DEVICE-TAG')

  def testHistoryResponse(self):
    now = datetime.datetime.now()
    device1 = device_messages.Device(serial_number='FAKE-DEVICE-SERIAL-1')
    device2 = device_messages.Device(serial_number='FAKE-DEVICE-SERIAL-2')

    hist_resp = device_messages.HistoryResponse(
        devices=[device1, device2],
        timestamp=[now],
        actor=['FAKE-ACTOR-1'],
        summary=['FAKE-SUMMARY-1', 'FAKE-SUMMARY-2'])

    self.assertListEqual(hist_resp.timestamp, [now])
    self.assertListEqual(hist_resp.actor, ['FAKE-ACTOR-1'])
    self.assertListEqual(hist_resp.summary,
                         ['FAKE-SUMMARY-1', 'FAKE-SUMMARY-2'])
    self.assertEqual(hist_resp.devices[0].serial_number, 'FAKE-DEVICE-SERIAL-1')
    self.assertEqual(hist_resp.devices[1].serial_number, 'FAKE-DEVICE-SERIAL-2')

if __name__ == '__main__':
  absltest.main()
