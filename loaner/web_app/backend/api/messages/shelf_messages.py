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

"""Shelf messages for Shelf API."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from protorpc import message_types
from protorpc import messages

from loaner.web_app.backend.api.messages import shared_messages


class ShelfRequest(messages.Message):
  """Get or disable Shelf Request ProtoRPC message.

  Attributes:
    location: str, The location of the shelf.
    urlsafe_key: str, The urlsafe representation of the ndb.Key for the
        requested shelf.
  """
  location = messages.StringField(1)
  urlsafe_key = messages.StringField(2)


class Shelf(messages.Message):
  """Shelf ProtoRPC message.

  Attributes:
    enabled: bool, Indicates if the shelf is enabled or not.
    friendly_name: str, The friendly name of the shelf.
    location: str, The location of the shelf.
    identifier: str, the computed identifier for a shelf. Location if
        Friendly name is not provided.
    latitude: float, A geographical point represented by floating-point.
    longitude: float, A geographical point represented by floating-point.
    altitude: float, Indicates the floor.
    capacity: int, The amount of devices a shelf can hold.
    audit_notification_enabled: bool, Indicates if an audit is enabled for
        the shelf.
    audit_requested: bool, Indicates if an audit has been requested.
    responsible_for_audit: str, The party responsible for audits.
    last_audit_time: datetime,  Indicates the last audit time.
    last_audit_by: str, Indicates the last user to audit the shelf.
    page_size: int, The number of results to query for and display.
    page_number: int, The page index to offset the results.
    shelf_request: ShelfRequest, A message containing the unique identifier to
        be used to retrieve the shelf.
    query: shared_message.SearchRequest, a message containing query options to
        conduct a search on an index.
    audit_interval_override: str, The audit interval override (in hours).
  """
  enabled = messages.BooleanField(1, default=True)
  friendly_name = messages.StringField(2)
  location = messages.StringField(3)
  identifier = messages.StringField(4)
  latitude = messages.FloatField(5)
  longitude = messages.FloatField(6)
  altitude = messages.FloatField(7)
  capacity = messages.IntegerField(8)
  audit_notification_enabled = messages.BooleanField(9)
  audit_requested = messages.BooleanField(10)
  responsible_for_audit = messages.StringField(11)
  last_audit_time = message_types.DateTimeField(12)
  last_audit_by = messages.StringField(13)
  page_size = messages.IntegerField(14, default=10)
  page_number = messages.IntegerField(15, default=1)
  shelf_request = messages.MessageField(ShelfRequest, 16)
  query = messages.MessageField(shared_messages.SearchRequest, 17)
  audit_interval_override = messages.IntegerField(18)


class EnrollShelfRequest(messages.Message):
  """EnrollShelfRequest ProtoRPC message.

  Attributes:
    friendly_name: str, The friendly name of the shelf.
    location: str, The location of the shelf.
    latitude: float, A geographical point represented by floating-point.
    longitude: float, A geographical point represented by floating-point.
    altitude: float, Indicates the floor.
    capacity: int, The amount of devices a shelf can hold.
    audit_notification_enabled: bool, Indicates if an audit is enabled for
        the shelf.
    responsible_for_audit: str, The party responsible for audits.
    audit_interval_override: int, The audit interval override (in hours).
  """
  friendly_name = messages.StringField(1)
  location = messages.StringField(2, required=True)
  latitude = messages.FloatField(3)
  longitude = messages.FloatField(4)
  altitude = messages.FloatField(5)
  capacity = messages.IntegerField(6, required=True)
  audit_notification_enabled = messages.BooleanField(7)
  responsible_for_audit = messages.StringField(8)
  audit_interval_override = messages.IntegerField(9)


class UpdateShelfRequest(messages.Message):
  """UpdateShelfRequest ProtoRPC message.

  Attributes:
    shelf_request: ShelfRequest, A message containing the unique identifier to
        be used to retrieve the shelf.
    current_location: str, The current location of the shelf being requested.
    friendly_name: str, The friendly name of the shelf.
    location: str, The location of the shelf.
    latitude: float, A geographical point represented by floating-point.
    longitude: float, A geographical point represented by floating-point.
    altitude: float, Indicates the floor.
    audit_interval_override: int, The audit interval override (in hours).
    responsible_for_audit: str, The party responsible for audits.
    audit_notification_enabled: bool, Indicates if an audit is enabled for
        the shelf.
  """
  shelf_request = messages.MessageField(ShelfRequest, 1)
  friendly_name = messages.StringField(2)
  location = messages.StringField(3)
  capacity = messages.IntegerField(4)
  latitude = messages.FloatField(5)
  longitude = messages.FloatField(6)
  altitude = messages.FloatField(7)
  audit_interval_override = messages.IntegerField(8)
  responsible_for_audit = messages.StringField(9)
  audit_notification_enabled = messages.BooleanField(10)


class ListShelfResponse(messages.Message):
  """List Shelf Response ProtoRPC message.

  Attributes:
    shelves: List[Shelf], The list of shelves being returned.
    total_results: int, The total number of results for a query.
    total_pages: int, The total number of pages needed to display all of the
        results.
  """
  shelves = messages.MessageField(Shelf, 1, repeated=True)
  total_results = messages.IntegerField(2)
  total_pages = messages.IntegerField(3)


class ShelfAuditRequest(messages.Message):
  """ShelfAuditRequest ProtoRPC message.

  Attributes:
    shelf_request: ShelfRequest, A message containing the unique identifier to
        be used to retrieve the shelf.
    device_identifiers: List[str], A list of device serial numbers to perform a
        device audit on.
  """
  shelf_request = messages.MessageField(ShelfRequest, 1)
  device_identifiers = messages.StringField(2, repeated=True)
