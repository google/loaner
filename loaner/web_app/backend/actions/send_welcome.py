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

"""Action to send a welcome e-mail."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from loaner.web_app.backend.actions import base_action
from loaner.web_app.backend.lib import send_email


class SendWelcome(base_action.BaseAction):
  """Action class to send a welcome e-mail to a device assignee."""

  ACTION_NAME = 'send_welcome'
  FRIENDLY_NAME = 'Send welcome'
  ACTION_TYPE = base_action.ActionType.ASYNC

  def run(self, device=None):
    """Sends an e-mail to a new device assignee."""
    if not device:
      raise base_action.MissingDeviceError(
          'Cannot send mail. Task did not receive a device.')
    send_email.send_user_email(device, 'reminder_welcome')
