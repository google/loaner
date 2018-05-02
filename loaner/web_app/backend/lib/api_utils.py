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

from absl import logging

from protorpc import messages

from google.appengine.api import datastore_errors
from google.appengine.datastore import datastore_query
from google.appengine.ext import ndb

import endpoints

from loaner.web_app.backend.api.messages import device_message
from loaner.web_app.backend.api.messages import shelf_messages

_CORRUPT_KEY_MSG = 'The key provided for submission was not found.'
_MALFORMED_PAGE_TOKEN_MSG = 'The page token provided is incorrect.'


def build_device_message_from_model(device, guest_permitted):
  """Builds a device_message.Device ProtoRPC message.

  Args:
    device: device_model.Device, a device entity to convert into a message.
    guest_permitted: bool, whether or not guest is permitted for this
        organization.

  Returns:
    A populated device_message.Device ProtoRPC message.
  """
  message = device_message.Device(
      guest_enabled=device.guest_enabled,
      guest_permitted=guest_permitted)
  if device.is_assigned:
    message.max_extend_date = device.calculate_return_dates().max
  for key in device._properties:  # pylint: disable=protected-access
    value = getattr(device, key, None)
    try:
      setattr(message, key, value)
    except messages.ValidationError as err:
      logging.info(err)
      if key == 'shelf':
        setattr(message, key, build_shelf_message_from_model(value.get()))
      elif key.endswith('reminder'):
        setattr(message, key, build_reminder_message_from_model(value))
      else:
        logging.warning(
            'Attribute (%s) was not found on the device (%s).',
            key, device)

  return message


def build_reminder_message_from_model(reminder):
  """Builds a next- or last-reminder ProtoRPC message.

  Args:
    reminder: device_model.Reminder, the reminder from a device.

  Returns:
    A device_message.Reminder message with the respective properties.
  """
  message = device_message.Reminder()
  try:
    for key in reminder._properties:  # pylint:disable=protected-access
      value = getattr(reminder, key, None)
      setattr(message, key, value)
  except AttributeError:
    # This will occur when the reminder is None, we return an empty message.
    return None

  return message


def build_shelf_message_from_model(shelf):
  """Builds a shelf_messages.Shelf ProtoRPC message.

  Args:
    shelf: shelf_model.Shelf, the shelf to build a message for.

  Returns:
    A shelf_messages.Shelf ProtoRPC message for the given shelf.
  """
  message = shelf_messages.Shelf()
  # Get and build the shelf request message.
  try:
    message.shelf_request = shelf_messages.ShelfRequest(
        location=shelf.location, urlsafe_key=shelf.key.urlsafe())
  except AttributeError as err:
    logging.warning(err)
    raise endpoints.NotFoundException(err)
  # Build the shelf message from the model.
  for key in shelf._properties:  # pylint:disable=protected-access
    value = getattr(shelf, key, None)
    try:
      setattr(message, key, value)
    except AttributeError as err:
      if key == 'lat_long':
        setattr(message, 'latitude', getattr(shelf.lat_long, 'lat', None))
        setattr(message, 'longitude', getattr(shelf.lat_long, 'lon', None))
      else:
        logging.warning(
            'Attribute (%s) was not found on the shelf with urlsafe key (%s). '
            'Error: %s.', key, shelf.key.urlsafe(), err)

  return message


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
