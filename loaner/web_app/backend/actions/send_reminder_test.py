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

"""Tests for backend.actions.send_reminder."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from absl.testing import parameterized
import mock

from loaner.web_app.backend.lib import send_email
from loaner.web_app.backend.models import config_model
from loaner.web_app.backend.models import device_model
from loaner.web_app.backend.models import event_models
from loaner.web_app.backend.testing import loanertest


class SendReminderTest(loanertest.ActionTestCase, parameterized.TestCase):
  """Test the SendReminder Action class."""

  def setUp(self):
    self.testing_action = 'send_reminder'
    super(SendReminderTest, self).setUp()

  def test_run_no_device(self):
    self.assertRaisesRegexp(  # Raises generic because imported != loaded.
        Exception, '.*did not receive a device.*', self.action.run)

  def test_run_no_next_reminder(self):
    device = device_model.Device(serial_number='123456', chrome_device_id='123')
    self.assertRaisesRegexp(  # Raises generic because imported != loaded.
        Exception, '.*without next_reminder.*', self.action.run, device=device)

  def test_run_no_event(self):
    device = device_model.Device(  # Raises generic because imported != loaded.
        serial_number='123456', next_reminder=device_model.Reminder(level=0))
    self.assertRaisesRegexp(
        Exception, '.*no ReminderEvent.*', self.action.run, device=device)

  @parameterized.named_parameters(
      {'testcase_name': 'send_reminder_email', 'config_return': True,
       'send_email_call_count': 1},
      {'testcase_name': 'no_reminder_email', 'config_return': False,
       'send_email_call_count': 0},
  )
  def test_run_success(self, config_return, send_email_call_count):
    device = device_model.Device(
        serial_number='123456', chrome_device_id='123',
        next_reminder=device_model.Reminder(level=0))
    with mock.patch.object(
        config_model.Config, 'get', return_value=config_return):
      with mock.patch.object(send_email, 'send_user_email') as mock_sendemail:
        event_models.ReminderEvent.create(0)
        self.assertFalse(device.last_reminder)

        self.action.run(device=device)
        device = device.key.get()
        self.assertTrue(device.last_reminder)
        self.assertEqual(mock_sendemail.call_count, send_email_call_count)


if __name__ == '__main__':
  loanertest.main()
