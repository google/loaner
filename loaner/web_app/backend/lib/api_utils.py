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

"""Utilities for the api modules."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from google.appengine.api import datastore_errors
from google.appengine.datastore import datastore_query
from google.appengine.ext import ndb

import endpoints

from loaner.web_app.backend.api.messages import device_messages
from loaner.web_app.backend.api.messages import shelf_messages
from loaner.web_app.backend.models import device_model

_CORRUPT_KEY_MSG = 'The key provided for submission was not found.'
_MALFORMED_PAGE_TOKEN_MSG = 'The page token provided is incorrect.'


def build_device_message_from_model(device, guest_permitted):
  """Builds a device_messages.Device ProtoRPC message.

  Args:
    device: device_model.Device, a device entity to convert into a message.
    guest_permitted: bool, whether or not guest is permitted for this
        organization.

  Returns:
    A populated device_messages.Device ProtoRPC message.
  """
  message = device_messages.Device(
      serial_number=device.serial_number,
      asset_tag=device.asset_tag,
      identifier=device.identifier,
      enrolled=device.enrolled,
      device_model=device.device_model,
      due_date=device.due_date,
      last_known_healthy=device.last_known_healthy,
      assigned_user=device.assigned_user,
      assignment_date=device.assignment_date,
      current_ou=device.current_ou,
      ou_changed_date=device.ou_changed_date,
      locked=device.locked,
      lost=device.lost,
      mark_pending_return_date=device.mark_pending_return_date,
      chrome_device_id=device.chrome_device_id,
      last_heartbeat=device.last_heartbeat,
      damaged=device.damaged,
      damaged_reason=device.damaged_reason,
      guest_enabled=device.guest_enabled,
      guest_permitted=guest_permitted,
      overdue=device.overdue,
  )
  if device.last_reminder:
    message.last_reminder = build_reminder_message_from_model(
        device.last_reminder)
  if device.next_reminder:
    message.next_reminder = build_reminder_message_from_model(
        device.next_reminder)
  if device.is_assigned:
    message.max_extend_date = device_model.calculate_return_dates(
        device.assignment_date).max
  if device.shelf:
    message.shelf = build_shelf_message_from_model(device.shelf.get())
  return message


def build_reminder_message_from_model(reminder):
  """Builds a next- or last-reminder ProtoRPC message.

  Args:
    reminder: device_model.Reminder, the reminder from a device.

  Returns:
    A device_messages.Reminder message with the respective properties.
  """
  return device_messages.Reminder(
      level=reminder.level,
      time=reminder.time,
      count=reminder.count)


def build_shelf_message_from_model(shelf):
  """Builds a shelf_messages.Shelf ProtoRPC message.

  Args:
    shelf: shelf_model.Shelf, the shelf to build a message for.

  Returns:
    A shelf_messages.Shelf ProtoRPC message for the given shelf.
  """
  return shelf_messages.Shelf(
      shelf_request=shelf_messages.ShelfRequest(
          location=shelf.location, urlsafe_key=shelf.key.urlsafe()),
      enabled=shelf.enabled,
      friendly_name=shelf.friendly_name,
      location=shelf.location,
      identifier=shelf.identifier,
      latitude=shelf.latitude,
      longitude=shelf.longitude,
      altitude=shelf.altitude,
      capacity=shelf.capacity,
      audit_notification_enabled=shelf.audit_notification_enabled,
      audit_requested=shelf.audit_requested,
      responsible_for_audit=shelf.responsible_for_audit,
      last_audit_time=shelf.last_audit_time,
      last_audit_by=shelf.last_audit_by,
  )


def to_dict(entity, model_class):
  """Builds a dictionary of filtered properties of an NDB model.

  Args:
    entity: An instance of an NDB Model or a ProtoRPC message.
    model_class: NDB model to use for iterating its properties.

  Returns:
    A dictionary with filter properties.
  """
  dictionary = {}
  for key in model_class._properties:  # pylint: disable=protected-access
    value = None
    if key == 'lat_long':
      try:
        value = ndb.GeoPt(
            getattr(entity, 'latitude', None),
            getattr(entity, 'longitude', None))
      except datastore_errors.BadValueError:
        # BadValueError was raised when getattr returned None for latitude and
        # longitude. No need to set ndb.GeoPt as the values were None.
        pass
    else:
      value = getattr(entity, key, None)

    if value is not None and value != []:  # pylint: disable=g-explicit-bool-comparison
      dictionary[key] = value
  return dictionary


def get_datastore_cursor(urlsafe_cursor):
  """Builds a datastore.Cursor from a urlsafe cursor.

  Args:
    urlsafe_cursor: str, The urlsafe representation of a datastore.Cursor.

  Returns:
    datastore.Cursor instance.

  Raises:
    endpoints.BadRequestException: if the creation of the datastore.Cursor
        fails.
  """
  try:
    return datastore_query.Cursor(urlsafe=urlsafe_cursor)
  except datastore_errors.BadValueError:
    raise endpoints.BadRequestException(_MALFORMED_PAGE_TOKEN_MSG)


def get_ndb_key(urlsafe_key):
  """Builds an ndb.Key from a urlsafe key.

  Args:
    urlsafe_key: str, A urlsafe ndb.Key to cast into an ndb.Key.

  Returns:
    An ndb.Key instance.

  Raises:
    endpoints.BadRequestException: if the creation of the ndb.Key fails.
  """
  try:
    return ndb.Key(urlsafe=urlsafe_key)
  except Exception:  # pylint: disable=broad-except
    raise endpoints.BadRequestException(_CORRUPT_KEY_MSG)
