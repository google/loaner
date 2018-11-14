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

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import logging
import pickle

from google.appengine.api import taskqueue

from loaner.web_app.backend.actions import base_action
from loaner.web_app.backend.lib import action_loader
from loaner.web_app.backend.models import event_models

_NO_ACTIONS_MSG = 'No actions for event %s.'
_CACHED_EVENT_ACTION_MAPPINGS = None


class Error(Exception):
  """General Error class for this module."""


class NoEventsError(Error):
  """Error raised if there are no Events configured in datastore."""


class EventActionsError(Error):
  """Raised when the event actions raised an error."""


def raise_event(event_name, device=None, shelf=None):
  """Raises an Event, running its sync and async Actions.

  This function runs sync Actions serially, accumulating changes from each
  action, and then kicks off async Actions via a single task that will spawn
  more tasks for additional actions. Supply either a device or shelf arg, but
  not both.

  Args:
    event_name: str, the name of the Event.
    device: a Device model.
    shelf: a Shelf model.

  Returns:
    The original model, optionally modified by sync actions.

  Raises:
    base_action.MissingModelError: if this method is called with neither device
        nor shelf.
    base_action.RedundantModelError: if this method is called with both device
        and shelf.
    EventActionsError: if the actions raised an error.
  """
  event_actions = get_actions_for_event(event_name)
  event_actions.sort()
  event_async_actions = []
  actions_dict = action_loader.load_actions()
  model = device or shelf
  if not event_actions:
    logging.info(_NO_ACTIONS_MSG, event_name)
  else:
    action_kwargs = {}
    if device:
      action_kwargs['device'] = device
    if shelf:
      action_kwargs['shelf'] = shelf

    if not action_kwargs:
      raise base_action.MissingModelError(
          'No model passed to raise_event. You must supply either a device or '
          'shelf arg.')
    if len(action_kwargs) > 1:
      raise base_action.RedundantModelError(
          'Redundant models passed to raise_event. You must supply either a '
          'device or a shelf, but not both.')
    errors = []
    for action in event_actions:
      if action in actions_dict[base_action.ActionType.SYNC]:
        try:
          model = actions_dict[base_action.ActionType.SYNC][action].run(
              **action_kwargs)
        except base_action.Error as error:
          errors.append(error)
          logging.error(
              'Skipping Action "%s" because it raised an exception: %s',
              action, str(error))
      elif action in actions_dict[base_action.ActionType.ASYNC]:
        event_async_actions.append(action)
      else:
        logging.error(
            'Skipping Action %r because it is not loaded in the application.',
            action)
    if errors:
      raise EventActionsError(errors)
    if event_async_actions:
      action_kwargs['async_actions'] = event_async_actions
      taskqueue.add(
          queue_name='process-action',
          payload=pickle.dumps(action_kwargs),
          target='default')

  return model


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
  """Gets all Event-Action mappings and caches them if necessary."""
  global _CACHED_EVENT_ACTION_MAPPINGS
  if not _CACHED_EVENT_ACTION_MAPPINGS:
    _CACHED_EVENT_ACTION_MAPPINGS = {
        event.name: event.actions
        for event in (
            event_models.CoreEvent.query().fetch() +
            event_models.ShelfAuditEvent.query().fetch() +
            event_models.CustomEvent.query().fetch() +
            event_models.ReminderEvent.query().fetch()
        )
    }
  return _CACHED_EVENT_ACTION_MAPPINGS
