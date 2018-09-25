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

"""General library for importing YAML to make Cloud Datastore entities."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import logging
import random
import re

import yaml
from google.appengine.ext import ndb

from loaner.web_app import constants
from loaner.web_app.backend.models import device_model
from loaner.web_app.backend.models import event_models
from loaner.web_app.backend.models import shelf_model
from loaner.web_app.backend.models import survey_models
from loaner.web_app.backend.models import template_model
from loaner.web_app.backend.models import user_model

_TIME_RE = re.compile(r'^TIME:([\+\-]{0,1}[0-9]+)([dhw])')


class Error(Exception):
  """Base class for exceptions in this module."""


class DatastoreWipeError(Error):
  """Exception raised when DS wipe requested but BOOTSTRAP_ENABLED is False."""


def import_yaml(yaml_data, user_email, wipe=False, randomize_shelving=False):
  """Imports YAML data and creates app datastore entities.

  This allows wiping of the entire datastore, so for safety this option is
  disallowed if the constants module's BOOTSTRAP_ENABLED option is False.

  Args:
    yaml_data: str, the YAML data containing device, shelf, core_event,
        custom_event, and user data.
    user_email: str, email address of the user making the request.
    wipe: bool, whether to delete the existing datastore contents. Ignored if
        constants.BOOTSTRAP_ENABLED is False.
    randomize_shelving: bool, whether to assign Devices to Shelves randomly,
        which may be useful in app testing.

  Raises:
    DatastoreWipeError: if a datastore wipe is requested but BOOTSTRAP_ENABLED
        is False.
  """
  yaml_data = yaml.load(yaml_data)

  if wipe:
    if not constants.BOOTSTRAP_ENABLED:
      raise DatastoreWipeError(
          'Requested datastore wipe disallowed. Change '
          'constants.BOOTSTRAP_ENABLED to True to permit wiping.')
    else:
      logging.info(
          'Wiping existing datastore entities for kinds found in YAML.')
      if yaml_data.get('core_events'):
        ndb.delete_multi(event_models.CoreEvent.query().fetch(keys_only=True))
      if yaml_data.get('custom_events'):
        ndb.delete_multi(event_models.CustomEvent.query().fetch(keys_only=True))
      if yaml_data.get('devices'):
        ndb.delete_multi(device_model.Device.query().fetch(keys_only=True))
      if yaml_data.get('reminder_events'):
        ndb.delete_multi(
            event_models.ReminderEvent.query().fetch(keys_only=True))
      if yaml_data.get('shelves'):
        ndb.delete_multi(shelf_model.Shelf.query().fetch(keys_only=True))
      if yaml_data.get('survey_questions'):
        ndb.delete_multi(
            survey_models.Question.query().fetch(keys_only=True))
      if yaml_data.get('templates'):
        ndb.delete_multi(template_model.Template.query().fetch(keys_only=True))
      if yaml_data.get('users'):
        ndb.delete_multi(user_model.User.query().fetch(keys_only=True))

  shelf_keys = []

  for shelf in yaml_data.get('shelves', []):
    shelf = shelf_model.Shelf.enroll(user_email, **shelf).put()
    shelf_keys.append(shelf)
  for device in yaml_data.get('devices', []):
    device = device_model.Device.enroll(user_email=user_email, **device)
    if randomize_shelving:
      device.shelf = shelf_keys[random.randint(0, len(shelf_keys) - 1)]
      device.put()
  for core_event in yaml_data.get('core_events', []):
    model = event_models.CoreEvent.create(core_event['name'])
    _import_event_dict(model, core_event)
  for shelf_audit_event in yaml_data.get('shelf_audit_events', []):
    model = event_models.ShelfAuditEvent.create()
    _import_event_dict(model, shelf_audit_event)
  for custom_event in yaml_data.get('custom_events', []):
    model = event_models.CustomEvent.create(custom_event['name'])
    _import_event_dict(model, custom_event)
  for reminder_event in yaml_data.get('reminder_events', []):
    model = event_models.ReminderEvent.create(reminder_event['level'])
    _import_event_dict(model, reminder_event)
  for question in yaml_data.get('survey_questions', []):
    question['answers'] = [
        survey_models.Answer.create(**answer) for answer in question['answers']]
    model = survey_models.Question.create(**question)
  for template in yaml_data.get('templates', []):
    template_model.Template.create(
        template['name'], template.get('title'), template.get('body'))
  for user in yaml_data.get('users', []):
    user_model.User(**user).put()


def _import_event_dict(model, event_dict):
  """Imports a YAML-derived event dictionary into a model, and put.

  Args:
    model: event_models.CoreEvent, A datastore NDB model of this class or a
        subclass.
    event_dict: dict, A configuration derived from YAML.
  """
  for prop, value in event_dict.iteritems():
    if prop not in ['actions', 'conditions', 'level', 'name']:
      setattr(model, prop, value)
    elif prop == 'actions':
      for action in value:
        model.actions.append(action)
    elif prop == 'conditions':
      for condition in value:
        condition['value'] = _interpret_time(condition['value'])
        model.conditions.append(event_models.CustomEventCondition(**condition))
  model.put()


def _interpret_time(value):
  """Interprets a string from a YAML query condition for a time-related value.

  This turns a string like 'TIME:-3d' into a datetime.timedelta three days ago.

  Args:
    value: str, a value from datastore. If the passed value is not a string,
        this method returns it as originally passed.

  Returns:
    The original value, or an interpreted one as a datetime.timedelta.
  """
  if isinstance(value, basestring):
    match = _TIME_RE.match(value)
    if match:
      qty = int(match.group(1))
      unit = match.group(2)
      return event_models.create_timedelta(qty, unit)
  return value
