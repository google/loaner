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

"""Tests for backend.actions.lock_device."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import mock

from loaner.web_app.backend.models import device_model
from loaner.web_app.backend.testing import loanertest


class LockDeviceTest(loanertest.ActionTestCase):
  """Test the LockDevice Action class."""

  def setUp(self):
    self.testing_action = 'lock_device'
    super(LockDeviceTest, self).setUp()

  def test_run__no_device(self):
    self.assertRaisesRegexp(  # Raises generic because imported != loaded.
        Exception, '.*did not receive a device.*', self.action.run)

  @mock.patch('__main__.device_model.Device.lock')
  def test_run_success(self, mock_lock):
    device = device_model.Device(
        serial_number='123456', chrome_device_id='123',
        next_reminder=device_model.Reminder(level=0))

    self.action.run(device=device)
    self.assertEqual(mock_lock.call_count, 1)


if __name__ == '__main__':
  loanertest.main()
