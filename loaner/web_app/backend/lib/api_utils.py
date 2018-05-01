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

import endpoints

from loaner.web_app.backend.api.messages import device_message
from loaner.web_app.backend.api.messages import shelf_messages


def build_reminder_message(reminder):
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


def build_shelf_message(shelf):
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
            'Attribute (%s) was not found on the shelf with urlsafe key (%s).',
            key, shelf.key.urlsafe())

  return message
