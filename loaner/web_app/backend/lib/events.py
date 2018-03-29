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

"""Module for raising and managing Events for the loaner project."""

import logging
import pickle

from google.appengine.api import memcache
from google.appengine.api import taskqueue

from loaner.web_app.backend.models import event_models

_NO_ACTIONS_MSG = 'No actions for event %s.'


class Error(Exception):
  """General Error class for this module."""


class NoEventsError(Error):
  """Error raised if there are no Events configured in datastore."""


def raise_event(event_name, device=None, shelf=None):
  """Raises an Event by creating a task.

  Args:
    event_name: str, the name of the Event.
    device: a Device model, or None.
    shelf: a Shelf model, or None.
  """
  event_actions = get_actions_for_event(event_name)
  if event_actions:
    for action in event_actions:
      task_params = {'action_name': action}
      if device:
        task_params['device'] = device
      if shelf:
        task_params['shelf'] = shelf
      taskqueue.add(
          queue_name='process-action',
          payload=pickle.dumps(task_params),
          target='default')
  else:
    logging.info(_NO_ACTIONS_MSG, event_name)


def get_actions_for_event(event_name):
  """Gets all Action mappings for a given Event.

  Args:
    event_name: str, the name of the Event.

  Returns:
    A list of actions for the Event, or None.

  Raises:
    NoEventsError: if there are no Events to be found in datastore.
  """
  all_mappings = get_all_event_action_mappings()
  if not all_mappings:
    raise NoEventsError(
        'There are no events; run bootstrap to add the default ones.')
  return all_mappings.get(event_name)


def get_all_event_action_mappings():
  """Gets all Event-Action mappings and memcaches them if necessary."""
  all_mappings = memcache.get('event_action_mappings')
  if not all_mappings:
    all_mappings = {
        event.name: event.actions
        for event in (
            event_models.CoreEvent.query().fetch() +
            event_models.ShelfAuditEvent.query().fetch() +
            event_models.CustomEvent.query().fetch() +
            event_models.ReminderEvent.query().fetch()
        )
    }
    memcache.set(key='event_action_mappings', value=all_mappings)
  return all_mappings
