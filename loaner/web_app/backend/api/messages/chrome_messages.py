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

"""Chrome messages for Chrome API."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from protorpc import messages


class HeartbeatRequest(messages.Message):
  """Heartbeat Request ProtoRPC message.

  Attributes:
    device_id: str, The unique Chrome device ID of the Chrome device.
  """
  device_id = messages.StringField(1)


class HeartbeatResponse(messages.Message):
  """Heartbeat Response ProtoRPC message.

  Attributes:
    is_enrolled: bool, Determine if the device is enrolled.
    start_assignment: bool, Determine if assignment workflow should be started.
    silent_onboarding: bool, Signals to the Chrome app whether or not to onboard
        new users in silent mode.
  """
  is_enrolled = messages.BooleanField(1)
  start_assignment = messages.BooleanField(2)
  silent_onboarding = messages.BooleanField(3)
