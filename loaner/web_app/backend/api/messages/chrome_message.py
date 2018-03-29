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

"""Chrome messages."""

from protorpc import message_types
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
    start_assignment: bool, Determine if assignmenet workflow should be started.
  """
  is_enrolled = messages.BooleanField(1)
  start_assignment = messages.BooleanField(2)


class LoanRequest(messages.Message):
  """Chrome Loan Request ProtoRPC message.

  Attributes:
    device_id: str, The unique Chrome device ID of the Chrome device.
    need_name: bool, If given name should be returned.
  """
  device_id = messages.StringField(1)
  need_name = messages.BooleanField(2)


class LoanResponse(messages.Message):
  """Chrome Loan information Response ProtoRPC message.

  Attributed:
    due_date: datetime, The due date for the device.
    max_extend_date: datetime, The max date a loan can be extended.
    given_name: str, The given name for the user.
    guest_permitted: bool, If guest mode can be enabled.
    guest_enabled: bool, If guest mode is enabled.
  """
  due_date = message_types.DateTimeField(1)
  max_extend_date = message_types.DateTimeField(2)
  given_name = messages.StringField(3)
  guest_permitted = messages.BooleanField(4)
  guest_enabled = messages.BooleanField(5)
