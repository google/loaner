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

"""Module for loading Actions for the loaner project."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import inspect
import logging
import os
import pkgutil

from loaner.web_app.backend.actions import base_action

_DUPLICATE_ACTION_MSG = (
    'Cannot load Action %s: there is already an Action of that name.')
_INSTANTIATION_ERROR_MSG = 'Error instantiating class %s in module %s: %s'
_CACHED_ACTIONS = None


def load_actions(filters=None, log_exceptions=True):
  """Loads Actions from the actions directory, and instantiates them.

  Args:
    filters: list, strings with names of action classes to load. Loader will
        skip classes not listed. In the absence of this list no filters are
        applied.
    log_exceptions: bool, whether to supress exceptions and log their messages
        instead.

  Returns:
    A dictionary of actions, with their names as keys and instaniated Action
    classes as their values.

  Raises:
    AttributeError: if log_exceptions is False and Action classes are missing
        ACTION_NAME or FRIENDLY_NAME attributes, or the run method.
  """
  global _CACHED_ACTIONS
  if _CACHED_ACTIONS:
    return _CACHED_ACTIONS
  actions = {base_action.ActionType.SYNC: {}, base_action.ActionType.ASYNC: {}}
  importer = pkgutil.ImpImporter(os.path.abspath(
      os.path.join(os.path.dirname(__file__), '..', 'actions')))
  for module_name, module in importer.iter_modules():
    del module  # Not used.
    if module_name.endswith('_test') or module_name.startswith('base_action'):
      continue
    try:
      loaded_module = importer.find_module(module_name).load_module(module_name)
    except ImportError:
      logging.info('Error importing module %s', module_name)
      continue
    for obj_name, obj in inspect.getmembers(loaded_module):
      if inspect.isclass(obj) and issubclass(obj, base_action.BaseAction):
        if filters and obj.ACTION_NAME not in filters:
          continue
        # Defaults to async for backward compatibility.
        action_type = getattr(obj, 'ACTION_TYPE', base_action.ActionType.ASYNC)
        try:
          action = obj()
        except AttributeError as e:
          error_message = _INSTANTIATION_ERROR_MSG % (
              obj_name, module_name, e.message)
          if log_exceptions:
            logging.warning(error_message)
            continue
          else:
            raise AttributeError(error_message)
        if (
            action.ACTION_NAME in actions[base_action.ActionType.SYNC] or
            action.ACTION_NAME in actions[base_action.ActionType.ASYNC]):
          logging.warning(_DUPLICATE_ACTION_MSG, obj.ACTION_NAME)
          continue
        actions[action_type][action.ACTION_NAME] = action
  _CACHED_ACTIONS = actions
  return actions
