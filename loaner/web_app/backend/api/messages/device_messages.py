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

"""Device messages for Device API."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from protorpc import message_types
from protorpc import messages

from loaner.web_app.backend.api.messages import shared_messages
from loaner.web_app.backend.api.messages import shelf_messages
from loaner.web_app.backend.api.messages import tag_messages


class Reminder(messages.Message):
  """Reminder ProtoRPC message.

  Attributes:
    level: int, Indicates if a reminder is due, overdue, or massively overdue.
    time:  datetime, The date at which the Device's assignee was reminded.
    count: int, Indicates the number of reminders seen.
  """
  level = messages.IntegerField(1)
  time = message_types.DateTimeField(2)
  count = messages.IntegerField(3)


class DeviceRequest(messages.Message):
  """General Device request ProtoRPC message with several identifiers.

  Attributes:
    asset_tag: str, The asset tag of the Chrome device.
    chrome_device_id: str, The Chrome device id of the Chrome device.
    serial_number: str, The serial number of the Chrome device.
    urlkey: str, The URL-safe key of a device.
    identifier: str, Either an asset tag or serial number of the device.
  """
  asset_tag = messages.StringField(1)
  chrome_device_id = messages.StringField(2)
  serial_number = messages.StringField(3)
  urlkey = messages.StringField(4)
  identifier = messages.StringField(5)


class Device(messages.Message):
  """Device ProtoRPC message.

  Attributes:
    serial_number: str, The serial number of the Chrome device.
    asset_tag: str, The asset tag of the Chrome device.
    identifier: str, The computed identifier for a device. Serial number if
        asset tag is not provided.
    enrolled: bool, Indicates the enrollment status of the device.
    device_model: int, Identifies the model name of the device.
    due_date: datetime, The date that device is due for return.
    last_know_healthy: datetime, The date to indicate the last known healthy
        status.
    shelf: shelf_messages.Shelf, The message for a shelf.
    assigned_user: str, The email of the user who is assigned to the device.
    assignment_date: datetime, The date the device was assigned to a user.
    current_ou: str, The current organizational unit the device belongs to.
    ou_change_date: datetime, The date the organizational unit was changed.
    locked: bool, Indicates whether or not the device is locked.
    lost: bool, Indicates whether or not the device is lost.
    mark_pending_return_date: datetime, The date a user marked device returned.
    chrome_device_id: str, A unique device ID.
    last_heartbeat: datetime, The date of the last time the device checked in.
    damaged: bool, Indicates the if the device is damaged.
    damaged_reason: str, A string denoting the reason for being reported as
        damaged.
    last_reminder: Reminder, Level, time, and count of the last reminder
        the device had.
    next_reminder: Reminder, Level, time, and count of the next reminder.
    page_token: str, A page token to query next page results.
    page_size: int, The number of results to query for and display.
    max_extend_date: datetime, Indicates maximum extend date a device can have.
    guest_enabled: bool, Indicates if guest mode has been already enabled.
    guest_permitted: bool, Indicates if guest mode has been allowed.
    given_name: str, The given name for the user.
    query: shared_message.SearchRequest, a message containing query options to
        conduct a search on an index.
    overdue: bool, Indicates that the due date has passed.
    tags: List[tag_model.TagData], a list of TagData objects associated with the
        device.
    onboarded: bool, Indicates that the device has been fully onboarded.
  """
  serial_number = messages.StringField(1)
  asset_tag = messages.StringField(2)
  identifier = messages.StringField(3)
  urlkey = messages.StringField(4)
  enrolled = messages.BooleanField(5, default=True)
  device_model = messages.StringField(6)
  due_date = message_types.DateTimeField(7)
  last_known_healthy = message_types.DateTimeField(8)
  shelf = messages.MessageField(shelf_messages.Shelf, 9)
  assigned_user = messages.StringField(10)
  assignment_date = message_types.DateTimeField(11)
  current_ou = messages.StringField(12)
  ou_changed_date = message_types.DateTimeField(13)
  locked = messages.BooleanField(14)
  lost = messages.BooleanField(15)
  mark_pending_return_date = message_types.DateTimeField(16)
  chrome_device_id = messages.StringField(17)
  last_heartbeat = message_types.DateTimeField(18)
  damaged = messages.BooleanField(19)
  damaged_reason = messages.StringField(20)
  last_reminder = messages.MessageField(Reminder, 21)
  next_reminder = messages.MessageField(Reminder, 22)
  page_token = messages.StringField(23)
  page_size = messages.IntegerField(24, default=25)
  max_extend_date = message_types.DateTimeField(25)
  guest_enabled = messages.BooleanField(26)
  guest_permitted = messages.BooleanField(27)
  given_name = messages.StringField(28)
  query = messages.MessageField(shared_messages.SearchRequest, 29)
  overdue = messages.BooleanField(30)
  tags = messages.MessageField(tag_messages.TagData, 31, repeated=True)
  onboarded = messages.BooleanField(32)


class ListDevicesResponse(messages.Message):
  """ListDevicesResponse ProtoRPC message.

  Attributes:
    devices: List[Device], The list of devices being returned.
    has_additional_results: bool, If there are more results to be displayed.
    page_token: str, A page token that will allow be used to query for
        additional results.
  """
  devices = messages.MessageField(Device, 1, repeated=True)
  has_additional_results = messages.BooleanField(2)
  page_token = messages.StringField(3)


class DamagedRequest(messages.Message):
  """DamagedRequest ProtoRPC message.

  Attributes:
    device: DeviceRequest, A device to be fetched.
    damaged_reason: str, The reason the device is being reported as damaged.
  """
  device = messages.MessageField(DeviceRequest, 1)
  damaged_reason = messages.StringField(2)


class ExtendLoanRequest(messages.Message):
  """ExtendLoanRequest ProtoRPC message.

  Attributes:
    device: DeviceRequest, A device to be fetched.
    extend_date: datetime, The date to extend the loan for.
  """
  device = messages.MessageField(DeviceRequest, 1)
  extend_date = message_types.DateTimeField(2)


class ListUserDeviceResponse(messages.Message):
  """ListUserDeviceResponse ProtoRPC message.

  Attributes:
    devices: List[Device], The list of devices assigned to the user.
  """
  devices = messages.MessageField(Device, 1, repeated=True)


class HistoryRequest(messages.Message):
  """HistoryRequest: ProtoRPC message.

  Attributes:
    device: DeviceRequest, The device to be used for lookup.
  """
  device = messages.MessageField(DeviceRequest, 1)


class HistoryResponse(messages.Message):
  """HistoryResponse: ProtoRPC message.

  Attributes:
    devices: List[Device], The list of historical changes made to the device.
    timestamp: datetime, The date and time when the change was made.
    actor: str, The person or entity who made the change.
    summary: str, The details of the change that occurred.
  """
  devices = messages.MessageField(Device, 1, repeated=True)
  timestamp = message_types.DateTimeField(2, repeated=True)
  actor = messages.StringField(3, repeated=True)
  summary = messages.StringField(4, repeated=True)
