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

"""Event model classes for the loaner project."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import datetime

from absl import logging

from google.appengine.api import datastore_errors
from google.appengine.ext import ndb

_BAD_FILTER_MSG = (
    'Skipping Custom Event %s: invalid filter (%s) in a %s condition.')
_TIME_UNIT_IN_SECONDS = {
    'h': 3600,
    'd': 86400,
    'w': 604800,
}


class Error(Exception):
  """General Error class for this module."""


class BadTimeUnitError(Error):
  """Error raised if a TIME value is not valid."""


class ExistingEventError(Error):
  """Error raised when an event of a requested name already exists."""


class CoreEvent(ndb.Model):
  """Datastore model representing core event class.

  Attributes:
    description: A description for an Event.
    actions: Contains the friendly names of Actions.
    enabled: A boolean indicating whether the event is enabled.
  """
  description = ndb.TextProperty()
  actions = ndb.StringProperty(repeated=True)
  enabled = ndb.BooleanProperty(default=True)

  @classmethod
  def create(cls, name, description=None):
    """Creates a new Event entity.

    Args:
      name: str, The name of the new event.
      description: str, The description of the new event.

    Returns:
      The new event entity.

    Raises:
      TypeError: if the name is not a string.
      ExistingEventError: if there's already one with that name.
    """
    if not isinstance(name, basestring):
      raise TypeError('The name of the Event must be a string.')
    if cls.get_by_id(str(name)):
      raise ExistingEventError(
          'Cannot create Event because one with that name exists.')
    event = cls(description=description, id=name)
    event.put()
    return event

  @classmethod
  def get(cls, name):
    """Gets a CoreEvent (or subclass) entity by name.

    Args:
      name: str, The name of the new event.

    Returns:
      The CoreEvent (or subclass) model from datastore, or None.
    """
    return cls.get_by_id(name)

  @property
  def name(self):
    return self.key.id()


class ShelfAuditEvent(CoreEvent):
  """Datastore model representing an event for shelf audit checks.

  Only one such event is needed for the app, and its entity exists only to store
  the set of actions to take when the app raises the event.
  """

  @classmethod
  def create(cls, actions=None):  # pylint: disable=arguments-differ
    """Creates a ShelfAuditEvent model.

    Since the app only needs one such event, this overwites any existing shelf
    audit event.

    Args:
      actions: list of action name strings.

    Returns:
      The ShelfAuditEvent model.
    """
    if not actions:
      actions = []
    actions.append('request_shelf_audit')
    shelf_audit_event = cls(actions=actions, id='shelf_needs_audit')
    shelf_audit_event.put()
    return shelf_audit_event


class CustomEventCondition(ndb.Model):
  """Datastore model representing a condition from which to build an ndb.Query.

  Attributes:
    name: str, Names a property on the NDB model.
    opsymbol: str, Specifies a comparison operator.
    value: pickle, Contains the actual value, which could be anything.
  """
  name = ndb.StringProperty(required=True)
  opsymbol = ndb.StringProperty(required=True)
  value = ndb.PickleProperty(required=True)

  def get_filter(self):
    return ndb.query.FilterNode(
        self.name, self.opsymbol, _apply_timedelta(self.value))

  def match(self, entity):
    """Determines whether an entity matches the condition.

    This is for manually running a condition on an entity outside an NDB query.

    Args:
      entity: a Datastore entity on which to test a match of this condition.

    Returns:
       True if the entity matches, else False.
    """
    entity_value = getattr(entity, self.name)
    condition_value = _apply_timedelta(self.value)
    if self.opsymbol in ['<', '<=', '>', '>='] and entity_value is None:
      # Unset properties are set to None, and so are treated as 0 in
      # comparisons; we prefer to filter.
      return False
    elif (
        (self.opsymbol == '<' and entity_value < condition_value) or
        (self.opsymbol == '<=' and entity_value <= condition_value) or
        (self.opsymbol == '==' and entity_value == condition_value) or
        (self.opsymbol == '!=' and entity_value != condition_value) or
        (self.opsymbol == '>' and entity_value > condition_value) or
        (self.opsymbol == '>=' and entity_value >= condition_value)):
      return True
    else:
      return False


class CustomEvent(CoreEvent):
  """Datastore model representing a custom event class.

  Note that the rules of NDB queries apply (e.g., including more than one
    inequality filter will result in a BadRequestError).

  Attribues:
    model: The name of the NDB model on which the app queries.
    conditions: Triplet of objects the cron job uses with the model to build an
      NDB query.
  """
  model = ndb.StringProperty(choices=['Device', 'Shelf'])
  conditions = ndb.StructuredProperty(CustomEventCondition, repeated=True)

  @classmethod
  def get_all_enabled(cls):
    """Retrieves all enabled entities of this class."""
    return cls.query(cls.enabled == True).fetch()  # pylint: disable=g-explicit-bool-comparison,singleton-comparison

  def _build_query_components(self):
    """Builds a dict containing a query and other useful objects.

    Returns:
      A dict containing the following keys:
        query: an NDB query with as many filters as can be made from the event's
            conditions. This will be limited by Datastore's limitation to having
            no more than one inequality filter.
        less_than_properties: a list of strings containing the names of
            properties in the event's conditions using the < or <= operators.
            This allows a cron job to filter entities that do not have these
            properties set, which unfortunately matches < for queries).
        extra_inequality_conditions: a list of inequality CustomEventConditions
            that could not be used because of the aforementioned Datastore
            limitation.
    """
    less_than_properties = []
    query_filters = []
    extra_inequality_conditions = []
    inequality_filter_seen = False

    for condition in self.conditions:
      if condition.opsymbol in ['<', '<=']:
        less_than_properties.append(condition.name)

      inequality_filter = condition.opsymbol in ['<', '<=', '!=', '>', '>=']

      if inequality_filter:
        if inequality_filter_seen:
          extra_inequality_conditions.append(condition)
          continue
        else:
          inequality_filter_seen = True

      query_filters.append(condition.get_filter())

    return {
        'query': ndb.Query(
            kind=self.model, filters=ndb.query.ConjunctionNode(*query_filters)),
        'less_than_properties': less_than_properties,
        'extra_inequality_conditions': extra_inequality_conditions}

  def get_matching_entities(self):
    """Yields entities that match the event's conditions.

    Yields:
      Entities from a datastore query based on the custom event's conditions
      (some filtered post-query in cases where a query would otherwise have of
      multiple inequality filters).
    """
    query_components = self._build_query_components()
    try:
      for entity in query_components['query'].fetch():

        # Drop entities the query fetched because None is less than the value.
        has_null_less = False
        for less_than_condition in query_components['less_than_properties']:
          if getattr(entity, less_than_condition) is None:
            has_null_less = True
        if has_null_less:
          continue

        # Drop entities that don't match an extra inequality filter (i.e., a
        # condition discarded for the query due to a Datastore limitation).
        has_unmatched_condition = False
        for condition in query_components['extra_inequality_conditions']:
          if not condition.match(entity):
            has_unmatched_condition = True
        if has_unmatched_condition:
          continue

        yield entity

    except datastore_errors.BadArgumentError as e:
      logging.error(
          '%s %s has a bad query. Error: %s',
          self.__class__.__name__, self.name, str(e.message))


class ReminderEvent(CustomEvent):
  """Datastore model representing a custom event for reminders.

  Attributes:
    template: The name of the HTML template that should be used to populate the
      reminder.
    interval: The interval in days to wait before sending a repeated reminder
      for the same level.
    repeat_interval: Boolean indicating if a reminder should be repeated.
  """
  template = ndb.StringProperty()
  interval = ndb.IntegerProperty(default=0)
  repeat_interval = ndb.BooleanProperty(default=False)

  @property
  def level(self):
    """Pseudo-property to express Reminder level as an int."""
    return int(self.key.id())

  @classmethod
  def create(cls, level):
    """Creates a ReminderEvent model for a particular reminder level.

    Uses the level as the ID in the NDB key, and puts prior to returning.

    Args:
      level: int, the level of the reminder event.

    Returns:
      The ReminderrEvent model.

    Raises:
      TypeError: if the level is not an int.
      ExistingEventError: if there's already one with that level.
    """
    if not isinstance(level, int):
      raise TypeError('The level of the Reminder Event must be an int.')
    if cls.get_by_id(str(level)):
      raise ExistingEventError(
          'Cannot create Reminder Event because one for that level exists.')
    reminder_event = cls(
        model='Device', actions=['send_reminder'], id=str(level))
    reminder_event.put()
    return reminder_event

  @classmethod
  def get(cls, level):
    """Gets a ReminderEvent model for a particular reminder level.

    Args:
      level: int, the level of the reminder event.

    Returns:
      The ReminderEvent model.

    Raises:
      TypeError if the level is not an int.
    """
    if not isinstance(level, int):
      raise TypeError('The level of the Reminder Event must be an int.')
    return super(ReminderEvent, cls).get_by_id(str(level))

  @property
  def name(self):
    return self.make_name(self.key.id())

  @staticmethod
  def make_name(level):
    return 'reminder_level_%s' % str(level)


def _apply_timedelta(value):
  """Applies timedelta value to the current UTC time.

  Args:
    value: any type, taken from pickled CustomEventCondition value.

  Returns:
    The original value, or in the case of a timedelta, a datetime based on now
    with the timedelta applied.
  """
  if isinstance(value, datetime.timedelta):
    return datetime.datetime.utcnow() + value
  return value


def create_timedelta(qty, unit):
  """Creates a timedelta with quantity and units specified.

  Args:
    qty: int, the quantity of time, which can be positive or negative.
    unit: str, the initial of the time unit, 'h', 'd', or 'w'.

  Returns:
    The requested timedelta.

  Raises:
    BadTimeUnitError: if the unit does not exist.
  """
  try:
    return datetime.timedelta(seconds=_TIME_UNIT_IN_SECONDS[unit] * qty)
  except KeyError:
    raise BadTimeUnitError('Invalid unit "{}".'.format(unit))
