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
"""Tests for web_app.backend.api.messages.chrome_messages."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from loaner.web_app.backend.api.messages import chrome_messages
from absl.testing import absltest


class ChromeMessagesPy23MigrationTest(absltest.TestCase):

  def testHeartbeatRequest(self):
    chrome = chrome_messages.HeartbeatRequest(device_id='1')
    self.assertEqual(chrome.device_id, '1')

  def testHeartbeatResponse(self):
    chrome = chrome_messages.HeartbeatResponse(
        is_enrolled=True, start_assignment=True, silent_onboarding=True)
    self.assertEqual(chrome.is_enrolled, True)
    self.assertEqual(chrome.start_assignment, True)
    self.assertEqual(chrome.silent_onboarding, True)


if __name__ == '__main__':
  absltest.main()
