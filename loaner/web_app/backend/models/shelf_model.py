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

"""A model representing a shelf."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import datetime

from absl import logging

from google.appengine.api import datastore_errors
from google.appengine.ext import ndb

from loaner.web_app import constants
from loaner.web_app.backend.lib import events
from loaner.web_app.backend.models import base_model
from loaner.web_app.backend.models import config_model

_AUDIT_MSG = 'Marking shelf with name %s as audited with %s device(s).'
_AUDIT_REQUEST_MSG = 'Requesting audit for shelf with name %s.'
_CREATE_NEW_SHELF_MSG = 'Creating a new shelf with name %s.'
_DISABLE_MSG = 'Disabling shelf with name %s.'
_EDIT_MSG = 'Updating information for shelf with name %s.'
_ENABLE_MSG = 'Enabling shelf with name %s.'
_ENROLL_MSG = 'Enrolling shelf with name %s.'
_LAT_LONG_MSG = 'You must provide both latitude and longitude.'
_REACTIVATE_MSG = 'Reactivating shelf with name %s.'
_NEGATIVE_CAPACITY_MSG = 'Capacity must be greater than 0.'
_EVENT_ACTION_ERROR_MSG = (
    'The following error occurred while trying to perform the action (%s): %s')


class Error(Exception):
  """Base class for exceptions."""


class EnrollmentError(Error):
  """Raised when shelf enrollment fails."""


def _validate_capacity(prop_name, value):
  """Validate that the capacity is greater than 0.

  Args:
    prop_name: str, the name of the property to validate.
    value: int, the value of the property to validate.

  Raises:
    datastore_errors.BadValueError: when the value provided is less than 1.
  """
  del prop_name  # Unused.
  if value < 1:
    raise datastore_errors.BadValueError(_NEGATIVE_CAPACITY_MSG)


class Shelf(base_model.BaseModel):
  """Model representing a shelf.

  Attributes:
    enabled: A boolean indicating if the shelf is enabled or not.
    friendly_name: A string for the friendly name of the shelf.
    location: A string for the location of the shelf.
    lat_long: A geographical point represented by floating-point.
    altitude: A float indicating the floor.
    capacity: An integer for the amount of devices a shelf can hold.
    audit_interval_override: An integer for the number of hours to allow a shelf
        to remain unaudited, overriding the global shelf_audit_interval setting.
    audit_notification_enabled: A boolean indicating if an audit is enabled for
        the shelf.
    audit_requested: A boolean indicating if an audit has been requested.
    responsible_for_audit: A string for the party responsible for audits.
    last_audit_time: A datetime indicating the last audit time.
    last_audit_by: A string indicating the last user to audit the shelf.
  """
  enabled = ndb.BooleanProperty(default=True)
  friendly_name = ndb.StringProperty()
  location = ndb.StringProperty(required=True)
  lat_long = ndb.GeoPtProperty()
  altitude = ndb.FloatProperty()
  capacity = ndb.IntegerProperty(required=True, validator=_validate_capacity)
  audit_interval_override = ndb.IntegerProperty()
  audit_notification_enabled = ndb.BooleanProperty()
  audit_requested = ndb.BooleanProperty(default=False)
  responsible_for_audit = ndb.StringProperty()
  last_audit_time = ndb.DateTimeProperty()
  last_audit_by = ndb.StringProperty()

  _INDEX_NAME = constants.SHELF_INDEX_NAME
  _SEARCH_PARAMETERS = {
      'l': 'location',
      'f': 'friendly_name',
      'fn': 'friendly_name',
  }

  @property
  def identifier(self):
    return self.friendly_name or self.location

  @property
  def latitude(self):
    if not self.lat_long:
      return None
    return self.lat_long.lat

  @property
  def longitude(self):
    if not self.lat_long:
      return None
    return self.lat_long.lon

  @property
  def audited(self):
    """If the shelf has been audited.

    Returns:
      True if the shelf has been audited within the threshold.
    """
    return datetime.datetime.utcnow() < (
        self.last_audit_time + datetime.timedelta(
            hours=config_model.Config.get('audit_interval')))

  def _post_put_hook(self, future):
    """Overrides the _post_put_hook method."""
    del future  # Unused.
    index = Shelf.get_index()
    index.put(self.to_document())

  @classmethod
  def enroll(
      cls, user_email, location, capacity, friendly_name=None,
      latitude=None, longitude=None, altitude=None, responsible_for_audit=None,
      audit_notification_enabled=True, audit_interval_override=None):
    """Creates a new shelf or reactivates an existing one.

    Args:
      user_email: str, email of the user enrolling the shelf.
      location: str, location description of a shelf.
      capacity: int, maximum shelf capacity.
      friendly_name: str, optional, friendly name for a shelf.
      latitude: float, optional, latitude. Required if long provided.
      longitude: float, optional, longitude. Required if lat provided.
      altitude: int, optional, altitude of the shelf.
      responsible_for_audit: str, optional, string email (if email enabled) or
          other modifier (eg ticket queue) for the party responsible for
          auditing this shelf.
      audit_notification_enabled: bool, optional, enable or disable shelf audit
          notifications.
      audit_interval_override: An integer for the number of hours to allow a
          shelf to remain unaudited, overriding the global shelf_audit_interval
          setting.

    Returns:
      The newly created or reactivated shelf.

    Raises:
      EnrollmentError: If enrollment fails.
    """
    if bool(latitude) ^ bool(longitude):
      raise EnrollmentError(_LAT_LONG_MSG)

    shelf = cls.get(location=location, friendly_name=friendly_name)
    if shelf:
      shelf.enabled = True
      shelf.capacity = capacity
      shelf.friendly_name = friendly_name
      shelf.altitude = altitude
      shelf.responsible_for_audit = responsible_for_audit
      if latitude is not None and longitude is not None:
        shelf.lat_long = ndb.GeoPt(latitude, longitude)
      shelf.audit_interval_override = audit_interval_override
      logging.info(_REACTIVATE_MSG, shelf.identifier)
    else:
      shelf = cls(
          location=location,
          capacity=capacity,
          friendly_name=friendly_name,
          altitude=altitude,
          audit_notification_enabled=audit_notification_enabled,
          responsible_for_audit=responsible_for_audit,
          audit_interval_override=audit_interval_override)
      if latitude is not None and longitude is not None:
        shelf.lat_long = ndb.GeoPt(latitude, longitude)
      logging.info(_CREATE_NEW_SHELF_MSG, shelf.identifier)
    event_action = 'shelf_enroll'
    try:
      shelf = events.raise_event(event_action, shelf=shelf)
    except events.EventActionsError as err:
      # For any action that is implemented for shelf_enroll that is required for
      # the rest of the logic an error should be raised. If all actions are not
      # required, eg sending a notification email only, the error should only be
      # logged.
      logging.error(_EVENT_ACTION_ERROR_MSG, event_action, err)
    shelf.put()
    shelf.stream_to_bq(user_email, _ENROLL_MSG % shelf.identifier)
    return shelf

  @classmethod
  def get(cls, location=None, friendly_name=None):
    """Returns a shelf object.

    Args:
      location: str, the location for a shelf.
      friendly_name: str, the friendly_name for a shelf.

    Returns:
      A shelf object.
    """
    if friendly_name:
      shelf = cls.query(cls.friendly_name == friendly_name).get()
    else:
      shelf = cls.query(cls.location == location).get()
    return shelf

  def edit(self, user_email, **params):
    """Edit shelf with given params.

    Args:
      user_email: str, email of the user editing the shelf.
      **params: parameters to edit.
    """
    self.populate(**params)
    self.put()
    self.stream_to_bq(user_email, _EDIT_MSG % self.identifier)

  def audit(self, user_email, num_of_devices):
    """Marks a shelf audited.

    Args:
      user_email: str, email of the user auditing the shelf.
      num_of_devices: int, the number of devices on shelf.
    """
    self.last_audit_time = datetime.datetime.utcnow()
    self.last_audit_by = user_email
    self.audit_requested = False
    logging.info(_AUDIT_MSG, self.identifier, num_of_devices)
    event_action = 'shelf_audited'
    try:
      self = events.raise_event(event_action, shelf=self)
    except events.EventActionsError as err:
      # For any action that is implemented for shelf_audited that is required
      # for the rest of the logic an error should be raised. If all
      # actions are not required, eg sending a notification email only,
      # the error should only be logged.
      logging.error(_EVENT_ACTION_ERROR_MSG, event_action, err)
    self.put()
    self.stream_to_bq(
        user_email, _AUDIT_MSG % (self.identifier, num_of_devices))

  def request_audit(self):
    """Requests an audit by marking a shelf as audit_requested."""
    self.audit_requested = True
    logging.info(_AUDIT_REQUEST_MSG, self.identifier)
    self.put()
    self.stream_to_bq(
        constants.DEFAULT_ACTING_USER, _AUDIT_REQUEST_MSG % self.identifier)

  def enable(self, user_email):
    """Marks a shelf as enabled.

    Args:
      user_email: str, email of the user enabling the shelf.
    """
    self.enabled = True
    logging.info(_ENABLE_MSG, self.identifier)
    self.put()
    self.stream_to_bq(user_email, _ENABLE_MSG % self.identifier)

  def disable(self, user_email):
    """Marks a shelf as disabled.

    Args:
      user_email: str, email of the user disabling the shelf.
    """
    self.enabled = False
    logging.info(_DISABLE_MSG, self.identifier)
    event_action = 'shelf_disable'
    try:
      self = events.raise_event(event_action, shelf=self)
    except events.EventActionsError as err:
      # For any action that is implemented for shelf_disable that is required
      # for the rest of the logic an error should be raised. If all
      # actions are not required, eg sending a notification email only,
      # the error should only be logged.
      logging.error(_EVENT_ACTION_ERROR_MSG, event_action, err)
    self.put()
    self.stream_to_bq(user_email, _DISABLE_MSG % self.identifier)
