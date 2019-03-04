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

"""Tests for backend.lib.bootstrap."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import datetime
import logging
import os

import mock

from google.appengine.ext import deferred

from loaner.web_app import constants
from loaner.web_app.backend.clients import bigquery
from loaner.web_app.backend.clients import directory
from loaner.web_app.backend.lib import bootstrap
from loaner.web_app.backend.lib import datastore_yaml  # pylint: disable=unused-import
from loaner.web_app.backend.lib import utils
from loaner.web_app.backend.models import bootstrap_status_model
from loaner.web_app.backend.models import config_model
from loaner.web_app.backend.testing import loanertest


class BootstrapTest(loanertest.TestCase):
  """Tests for the datastore YAML importer lib."""

  @mock.patch.object(deferred, 'defer', autospec=True)
  def test_run_bootstrap(self, mock_defer):
    """Tests that run_bootstrap defers tasks for 2 methods."""
    mock_defer.return_value = 'fake-task'
    self.assertFalse(config_model.Config.get(
        'bootstrap_started'))
    run_status_dict = bootstrap.run_bootstrap({
        'bootstrap_bq_history': {},
        'bootstrap_datastore_yaml': {
            'yaml_input': 'fake-yaml'
        }
    })
    self.assertDictEqual(
        run_status_dict,
        {'bootstrap_bq_history':
             bootstrap._TASK_DESCRIPTIONS['bootstrap_bq_history'],
         'bootstrap_datastore_yaml':
             bootstrap._TASK_DESCRIPTIONS['bootstrap_datastore_yaml']})
    self.assertEqual(len(mock_defer.mock_calls), 2)
    self.assertTrue(config_model.Config.get('bootstrap_started'))

  @mock.patch.object(deferred, 'defer', autospec=True)
  def test_run_bootstrap_update(self, mock_defer):
    """Tests that run_bootstrap defers the correct tasks for an update."""
    mock_defer.return_value = 'fake-task'
    config_model.Config.set('running_version', '0.0.1-alpha')
    # This bootstrap task being completed would indicate that this is an update.
    bootstrap_status_model.BootstrapStatus.get_or_insert(
        'bootstrap_datastore_yaml').put()
    self.assertFalse(config_model.Config.get('bootstrap_started'))
    self.assertFalse(bootstrap._is_latest_version())
    run_status_dict = bootstrap.run_bootstrap()
    # Ensure that only _BOOTSTRAP_UPDATE_TASKS were run during an update.
    update_task_descriptions = {
        key: value for key, value in bootstrap._TASK_DESCRIPTIONS.iteritems()
        if key in bootstrap._BOOTSTRAP_UPDATE_TASKS
    }
    self.assertDictEqual(run_status_dict, update_task_descriptions)
    self.assertEqual(
        len(mock_defer.mock_calls), len(update_task_descriptions))
    self.assertTrue(config_model.Config.get('bootstrap_started'))

  @mock.patch.object(deferred, 'defer', autospec=True)
  def test_run_bootstrap_all_functions(self, mock_defer):
    """Tests that run_bootstrap defers all tasks for a new deployment."""
    mock_defer.return_value = 'fake-task'
    self.assertFalse(config_model.Config.get(
        'bootstrap_started'))
    run_status_dict = bootstrap.run_bootstrap()
    self.assertDictEqual(run_status_dict, bootstrap._TASK_DESCRIPTIONS)
    self.assertEqual(
        len(mock_defer.mock_calls), len(bootstrap._TASK_DESCRIPTIONS))
    self.assertTrue(config_model.Config.get(
        'bootstrap_started'))

  def test_run_bootstrap_bad_function(self):
    with self.assertRaises(bootstrap.Error):
      bootstrap.run_bootstrap({'bootstrap_bad_function': {}})

  @mock.patch.object(datastore_yaml, 'import_yaml', autospec=True)
  def test_manage_task_being_called(self, mock_importyaml):
    """Tests that the manage_task decorator is doing its task management."""
    del mock_importyaml  # Unused.
    bootstrap.bootstrap_datastore_yaml(user_email='foo')
    expected_model = bootstrap_status_model.BootstrapStatus.get_by_id(
        'bootstrap_datastore_yaml')
    self.assertEqual(
        expected_model.description,
        bootstrap._TASK_DESCRIPTIONS['bootstrap_datastore_yaml'])
    self.assertTrue(expected_model.success)
    self.assertLess(expected_model.timestamp, datetime.datetime.utcnow())

  @mock.patch.object(datastore_yaml, 'import_yaml', autospec=True)
  def test_manage_task_handles_exception(self, mock_importyaml):
    """Tests that the manage_task decorator kandles an exception."""
    mock_importyaml.side_effect = KeyError('task-exception')
    self.assertRaisesRegexp(
        deferred.PermanentTaskFailure,
        'bootstrap_datastore_yaml.*task-exception',
        bootstrap.bootstrap_datastore_yaml, user_email='foo')
    expected_model = bootstrap_status_model.BootstrapStatus.get_by_id(
        'bootstrap_datastore_yaml')
    self.assertFalse(expected_model.success)
    self.assertLess(expected_model.timestamp, datetime.datetime.utcnow())

  @mock.patch.object(datastore_yaml, 'import_yaml', autospec=True)
  def test_bootstrap_datastore_yaml(self, mock_importyaml):
    """Tests bootstrap_datastore_yaml."""
    bootstrap.bootstrap_datastore_yaml(user_email='foo')
    yaml_file_to_string = open(os.path.join(
        os.path.dirname(__file__), 'bootstrap.yaml')).read()
    mock_importyaml.assert_called_once_with(
        yaml_file_to_string, 'foo', True)

  @mock.patch.object(logging, 'info', autospec=True)
  @mock.patch.object(logging, 'warn', autospec=True)
  @mock.patch.object(directory, 'DirectoryApiClient', autospec=True)
  def test_bootstrap_chrome_ous(
      self, mock_directoryclass, mock_logwarn, mock_loginfo):
    mock_client = mock_directoryclass.return_value
    mock_client.get_org_unit.return_value = None
    bootstrap.bootstrap_chrome_ous(user_email='foo')

    self.assertEqual(3, mock_loginfo.call_count)

    # Everything is fine.
    mock_client.insert_org_unit.assert_has_calls([
        mock.call(path) for _, path in
        bootstrap.constants.ORG_UNIT_DICT.iteritems()
    ])

    # get_org_unit reveals an existing OU of that name.
    mock_client.reset_mock()
    mock_client.get_org_unit.return_value = {'fake': 'response'}
    bootstrap.bootstrap_chrome_ous(user_email='foo')
    self.assertEqual(mock_client.insert_org_unit.call_count, 0)
    mock_logwarn.assert_has_calls([
        mock.call(bootstrap._ORG_UNIT_EXISTS_MSG, org_unit_name) for
        org_unit_name in bootstrap.constants.ORG_UNIT_DICT
    ])

  @mock.patch.object(bigquery, 'BigQueryClient', autospec=True)
  def test_bootstrap_bq_history(self, mock_clientclass):
    """Tests bootstrap_bq_history."""
    mock_client = mock.Mock()
    mock_clientclass.return_value = mock_client
    bootstrap.bootstrap_bq_history()
    mock_client.initialize_tables.assert_called()

  @mock.patch.object(
      utils, 'load_config_from_yaml',
      return_value={'test_name': 'test_value', 'bootstrap_started': False})
  @mock.patch.object(config_model, 'Config')
  def test_bootstrap_load_config_yaml(
      self, mock_config, mock_load_config_from_yaml):
    """Tests if config_defaults.yaml is loaded into datastore."""
    mock_config.get.return_value = True
    bootstrap.bootstrap_load_config_yaml()
    mock_config.set.assert_has_calls([
        mock.call('test_name', 'test_value', False),
        mock.call('bootstrap_started', True, False)], any_order=True)

  def test_is_bootstrap_completed_true_up_to_date(self):
    config_model.Config.set('bootstrap_completed', True)
    config_model.Config.set('running_version', constants.APP_VERSION)
    self.assertTrue(bootstrap.is_bootstrap_completed())

  def test_is_bootstrap_completed_false_needs_update(self):
    config_model.Config.set('running_version', '0.0.1-alpha')
    self.assertFalse(bootstrap.is_bootstrap_completed())

  def test_is_bootstrap_started_and_completed(self):
    config_model.Config.set('bootstrap_completed', True)
    config_model.Config.set('bootstrap_started', True)
    # bootstrap_started is false (not in progress) if bootstrap completed.
    self.assertFalse(bootstrap.is_bootstrap_started())

  def test_is_new_deployment_false(self):
    config_model.Config.set('running_version', constants.APP_VERSION)
    self.assertFalse(bootstrap._is_new_deployment())

  @mock.patch.object(bootstrap, '_is_new_deployment', return_value=True)
  @mock.patch.object(bootstrap, 'is_update', autospec=True)
  def test_get_bootstrap_functions_new_deployment(
      self, mock_is_update, mock_is_new_deployment):
    # Ensure that all initial deployment tasks are included.
    self.assertTrue(
        all(task in bootstrap.get_bootstrap_functions()
            for task in bootstrap._BOOTSTRAP_INIT_TASKS))
    self.assertEqual(mock_is_update.call_count, 0)

  @mock.patch.object(bootstrap, '_is_new_deployment', return_value=False)
  def test_get_bootstrap_functions_update(self, mock_is_new_deployment):
    # Ensure that all initial deployment tasks are not included.
    self.assertFalse(
        any(task in bootstrap._BOOTSTRAP_INIT_TASKS
            for task in bootstrap.get_bootstrap_functions()))

  @mock.patch.object(bootstrap, '_is_new_deployment', return_value=False)
  def test_get_bootstrap_functions_get_all(self, mock_is_new_deployment):
    self.assertLen(
        bootstrap.get_bootstrap_functions(get_all=True),
        len(bootstrap._TASK_DESCRIPTIONS))

  @mock.patch.object(bootstrap, '_is_new_deployment', return_value=False)
  def test_get_bootstrap_functions_failed(self, mock_is_new_deployment):
    config_model.Config.set('running_version', constants.APP_VERSION)
    # Initialize all task statuses to successful.
    for task_name in bootstrap._TASK_DESCRIPTIONS.keys():
      task_entity = bootstrap_status_model.BootstrapStatus.get_or_insert(
          task_name)
      task_entity.success = True
      task_entity.put()
    # Mock 1 task failure.
    task_entity = bootstrap_status_model.BootstrapStatus.get_by_id(
        'bootstrap_datastore_yaml')
    task_entity.success = False
    task_entity.put()
    # Ensure that only failed and all update tasks are included.
    functions = bootstrap.get_bootstrap_functions()
    self.assertCountEqual(
        list(bootstrap._BOOTSTRAP_UPDATE_TASKS) + ['bootstrap_datastore_yaml'],
        functions.keys())

  @mock.patch.object(bootstrap, '_is_new_deployment', return_value=False)
  @mock.patch.object(bootstrap, 'get_bootstrap_functions', autospec=True)
  def test_get_bootstrap_task_status(
      self, mock_get_bootstrap_functions, mock_is_new_deployment):
    """Tests get_bootstrap_task_status."""
    config_model.Config.set('bootstrap_started', True)
    yesterday = datetime.datetime.utcnow() - datetime.timedelta(days=-1)

    def fake_function1():
      pass

    def fake_function2():
      pass

    mock_get_bootstrap_functions.return_value = {
        'fake_function1': fake_function1,
        'fake_function2': fake_function2
    }

    fake_entity1 = bootstrap_status_model.BootstrapStatus.get_or_insert(
        'fake_function1')
    fake_entity1.success = True
    fake_entity1.timestamp = yesterday
    fake_entity1.details = ''
    fake_entity1.put()

    fake_entity2 = bootstrap_status_model.BootstrapStatus.get_or_insert(
        'fake_function2')
    fake_entity2.success = True
    fake_entity2.timestamp = yesterday
    fake_entity2.details = ''
    fake_entity2.put()

    status = bootstrap.get_bootstrap_task_status()
    self.assertLen(status, 2)
    self.assertTrue(bootstrap.is_bootstrap_completed())

  @mock.patch.object(bootstrap, '_is_new_deployment', return_value=False)
  def test_is_latest_version_true(self, mock_is_new_deployment):
    config_model.Config.set('running_version', constants.APP_VERSION)
    self.assertTrue(bootstrap._is_latest_version())

  @mock.patch.object(bootstrap, '_is_new_deployment', return_value=True)
  def test_is_latest_version_false_new_deployment(self, mock_is_new_deployment):
    config_model.Config.set('running_version', constants.APP_VERSION)
    self.assertFalse(bootstrap._is_latest_version())

  @mock.patch.object(bootstrap, '_is_new_deployment', autospec=True)
  def test_is_latest_version_false_update(self, mock_is_new_deployment):
    # Mock the state of an application requiring an update.
    mock_is_new_deployment.return_value = False
    config_model.Config.set('bootstrap_completed', True)
    config_model.Config.set('running_version', '0.0.1-alpha')
    for task in bootstrap._TASK_DESCRIPTIONS.keys():
      fake_entity2 = bootstrap_status_model.BootstrapStatus.get_or_insert(task)
      fake_entity2.success = True
      fake_entity2.put()

    self.assertFalse(bootstrap._is_latest_version())
    # If we are not at the latest version, bootstrap should be incomplete.
    self.assertFalse(config_model.Config.get('bootstrap_completed'))
    # Update tasks should be marked as not completed when there is an update.
    for task in bootstrap._BOOTSTRAP_UPDATE_TASKS:
      status_entity = bootstrap_status_model.BootstrapStatus.get_by_id(task)
      self.assertFalse(status_entity.success)
    # All init task statuses should still be true in the case of an update.
    for task in bootstrap._BOOTSTRAP_INIT_TASKS:
      status_entity = bootstrap_status_model.BootstrapStatus.get_by_id(task)
      self.assertTrue(status_entity.success)

  @mock.patch.object(bootstrap, '_is_new_deployment', autospec=True)
  def test_is_update_new(self, mock_is_new_deployment):
    mock_is_new_deployment.return_value = True
    config_model.Config.set('running_version', '0.0')
    self.assertFalse(bootstrap.is_update())

  @mock.patch.object(bootstrap, '_is_new_deployment', autospec=True)
  def test_is_update_up_to_date(self, mock_is_new_deployment):
    config_model.Config.set('running_version', bootstrap.constants.APP_VERSION)
    self.assertFalse(bootstrap.is_update())

  @mock.patch.object(bootstrap, '_is_new_deployment', autospec=True)
  def test_is_update_needs_update(self, mock_is_new_deployment):
    # Mock the state of an application requiring an update.
    mock_is_new_deployment.return_value = False
    config_model.Config.set('running_version', '0.0.1-alpha')
    self.assertTrue(bootstrap.is_update())


if __name__ == '__main__':
  loanertest.main()
