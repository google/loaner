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

"""Deferred tasks for bootstrapping the GnG app."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import datetime
import functools
import inspect
import logging
import os
import sys

from google.appengine.ext import deferred

from loaner.web_app import constants
from loaner.web_app.backend.clients import bigquery
from loaner.web_app.backend.clients import directory
from loaner.web_app.backend.lib import datastore_yaml
from loaner.web_app.backend.lib import user
from loaner.web_app.backend.lib import utils
from loaner.web_app.backend.models import bootstrap_status_model
from loaner.web_app.backend.models import config_model


_ORG_UNIT_EXISTS_MSG = 'Org unit %s already exists, so cannot create.'
_TASK_DESCRIPTIONS = {
    'bootstrap_datastore_yaml': 'Importing datastore YAML file',
    'bootstrap_chrome_ous': 'Creating Chrome OUs in Directory',
    'bootstrap_bq_history': 'Configuring datastore history tables in BigQuery',
    'bootstrap_load_config_yaml': 'Loading config_defaults.yaml into datastore.'
}


class Error(Exception):
  """Exception raised when master method called but ENABLE_BOOTSTRAP False."""


def managed_task(task_function):
  """Decorator to manage task methods.

  This records the status of the task in an entity and raises the
  deferred.PermanentTaskFailure exception to prevent tasks from repeating upon
  failure. In such cases, the exception message is recorded to the entity.

  Args:
    task_function: function, to be managed by the decorator.

  Returns:
    Wrapped function.

  Raises:
    deferred.PermanentTaskFailure: if anything at all goes wrong.
  """
  @functools.wraps(task_function)
  def wrapper(*args, **kwargs):
    """Wrapper for managed task decorator."""
    status_entity = bootstrap_status_model.BootstrapStatus.get_or_insert(
        task_function.__name__)
    status_entity.description = _TASK_DESCRIPTIONS.get(
        task_function.__name__, task_function.__name__)
    status_entity.timestamp = datetime.datetime.utcnow()
    try:
      task_function(*args, **kwargs)
      status_entity.success = True
      status_entity.details = None
      status_entity.put()
    except Exception as e:
      status_entity.success = False
      status_entity.details = '{} {}'.format(str(type(e)), str(e))
      status_entity.put()
      raise deferred.PermanentTaskFailure(
          'Task {} failed; error: {}'.format(
              task_function.__name__, status_entity.details))

  return wrapper


@managed_task
def bootstrap_datastore_yaml(wipe=True, **kwargs):
  """Bootstraps arbitrary datastore entities from supplied YAML input.

  Args:
    wipe: bool, whether to wipe all existing datastore models for any model
        contained in the YAML.
    **kwargs: keyword args including a user_email with which to run the
        datastore methods (required for BigQuery streaming).
  """
  with open(
      os.path.join(os.path.dirname(__file__), 'bootstrap.yaml')) as yaml_file:
    datastore_yaml.import_yaml(yaml_file.read(), kwargs['user_email'], wipe)


@managed_task
def bootstrap_chrome_ous(**kwargs):
  """Bootstraps Chrome device OUs.

  Args:
    **kwargs: keyword args including a user_email with which to run the
        Directory API client methods (required for BigQuery streaming).
  """
  logging.info('Requesting delegated admin for bootstrap')
  client = directory.DirectoryApiClient(user_email=kwargs['user_email'])
  for org_unit_name, org_unit_path in constants.ORG_UNIT_DICT.iteritems():
    logging.info(
        'Creating org unit %s at path %s ...', org_unit_name, org_unit_path)
    if client.get_org_unit(org_unit_path):
      logging.warn(_ORG_UNIT_EXISTS_MSG, org_unit_name)
    else:
      client.insert_org_unit(org_unit_path)


@managed_task
def bootstrap_bq_history(**kwargs):
  """Bootstraps BigQuery history tables for archival purposes.

  Args:
    **kwargs: keyword args including a user_email with which to run the
        Directory API client methods (required for BigQuery streaming).
  """
  del kwargs  # Unused, but comes by default.
  client = bigquery.BigQueryClient()
  client.initialize_tables()


@managed_task
def bootstrap_load_config_yaml(**kwargs):
  """Loads config_defaults.yaml into datastore.

  Args:
    **kwargs: Unused, but required for bootstrap tasks.
  """
  del kwargs  # Unused, but comes by default.
  config_defaults = utils.load_config_from_yaml()
  for name, value in config_defaults.iteritems():
    if name == 'bootstrap_started':
      config_model.Config.set(name, config_model.Config.get(name), False)
    else:
      config_model.Config.set(name, value, False)


def get_all_bootstrap_functions():
  """Helper function that gets all functions starting with bootstrap_."""
  return {
      k: v
      for k, v in dict(
          inspect.getmembers(sys.modules[__name__], inspect.isfunction))
      .iteritems() if k.startswith('bootstrap_')
  }


def _run_function_as_task(all_functions_list, function_name, kwargs=None):
  """Runs a specific function and its kwargs as an AppEngine task.

  Args:
    all_functions_list: string list, A list with all function names that are
        registered as bootstrap functions on the Loaner app.
    function_name: string, A specific function that should be ran as a task.
    kwargs: dict, Optional kwargs to be passed to the function that will run.

  Returns:
    The deferred task from AppEngine taskqueue.

  Raises:
    Error: if requested bootstrap method is not allowed or does not exist.
  """
  logging.debug('Running %s as a task.', function_name)
  function = all_functions_list.get(function_name)
  if function is None:
    raise Error(
        'Requested bootstrap method {} does not exist.'.format(function_name))
  if not kwargs:
    kwargs = {}
  kwargs['user_email'] = user.get_user_email()
  return deferred.defer(function, **kwargs)


def run_bootstrap(requested_tasks=None):
  """Run one or more bootstrap functions.

  Args:
    requested_tasks: dict, wherein the keys are function names and the
        values are keyword arg dicts. If no functions are passed, runs all
        bootstrap functions with no specific kwargs.

  Returns:
    A dictionary of started tasks, with the task names as keys and the values
    being task descriptions as found in _TASK_DESCRIPTIONS.

  Raises:
    Error: If bootstrap is not enabled for this app.
  """
  if not constants.BOOTSTRAP_ENABLED:
    raise Error(
        'Requested bootstrap method(s) disallowed. Change '
        'constants.ENABLE_BOOTSTRAP to True to allow this.')

  config_model.Config.set('bootstrap_started', True)

  all_bootstrap = get_all_bootstrap_functions()

  run_status_dict = {}
  if requested_tasks:
    for function_name, kwargs in requested_tasks.iteritems():
      _run_function_as_task(all_bootstrap, function_name, kwargs)
      run_status_dict[function_name] = _TASK_DESCRIPTIONS.get(
          function_name, function_name)
  else:
    logging.debug('Running all functions as no specific function was passed.')
    for function_name in all_bootstrap:
      _run_function_as_task(all_bootstrap, function_name)
      run_status_dict[function_name] = _TASK_DESCRIPTIONS.get(
          function_name, function_name)

  return run_status_dict


def is_bootstrap_completed():
  """Gets the general status of the app bootstrap.

  This first checks bootstrap_started, and if that is True it returns the value
  of bootstrap_completed.

  Returns:
    True if the bootstrap is complete, else False.
  """
  try:
    if config_model.Config.get('bootstrap_started'):
      return config_model.Config.get(
          'bootstrap_completed')
    else:
      return False
  except KeyError:
    return False


def is_bootstrap_started():
  """Checks to see if bootstrap has started.

  Returns:
    True if the bootstrap has started, else False.
  """
  return config_model.Config.get('bootstrap_started')


def is_bootstrap_enabled():
  """Checks if bootstrap is enabled in the configuration settings."""
  return constants.BOOTSTRAP_ENABLED


def get_bootstrap_task_status():
  """Gets the status of all bootstrap tasks.

  Additionally this sets the overall completion status if all tasks were
  successful.

  Returns:
    Dictionary with task names as the keys and values being sub-dictionaries
        containing data derived from the datastore entities. If there is no data
        for any given task, its place is held by an empty dict.
  """
  bootstrap_completed = True
  bootstrap_task_status = {}
  for function_name in get_all_bootstrap_functions():
    status_entity = bootstrap_status_model.BootstrapStatus.get_by_id(
        function_name)
    if status_entity:
      bootstrap_task_status[function_name] = status_entity.to_dict()
    else:
      bootstrap_task_status[function_name] = {}
    if not bootstrap_task_status[function_name].get('success'):
      bootstrap_completed = False
  config_model.Config.set('bootstrap_completed', bootstrap_completed)
  return bootstrap_task_status
