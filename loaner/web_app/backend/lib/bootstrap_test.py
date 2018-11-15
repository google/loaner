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
import os

import mock

from google.appengine.ext import deferred  # pylint: disable=unused-import

from loaner.web_app.backend.clients import bigquery
from loaner.web_app.backend.lib import bootstrap
from loaner.web_app.backend.lib import datastore_yaml  # pylint: disable=unused-import
from loaner.web_app.backend.lib import utils
from loaner.web_app.backend.models import bootstrap_status_model
from loaner.web_app.backend.models import config_model
from loaner.web_app.backend.testing import loanertest


class BootstrapTest(loanertest.TestCase):
  """Tests for the datastore YAML importer lib."""

  @mock.patch('__main__.bootstrap.constants.BOOTSTRAP_ENABLED', True)
  @mock.patch('google.appengine.ext.deferred.defer')
  def test_run_bootstrap(self, mock_defer):
    """Tests that run_bootstrap defers tasks for all four methods."""
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
    self.assertTrue(config_model.Config.get(
        'bootstrap_started'))

  @mock.patch('__main__.bootstrap.constants.BOOTSTRAP_ENABLED', True)
  @mock.patch('google.appengine.ext.deferred.defer')
  def test_run_bootstrap_all_functions(self, mock_defer):
    """Tests that run_bootstrap defers tasks for all four methods."""
    mock_defer.return_value = 'fake-task'
    self.assertFalse(config_model.Config.get(
        'bootstrap_started'))
    run_status_dict = bootstrap.run_bootstrap()
    self.assertDictEqual(run_status_dict, bootstrap._TASK_DESCRIPTIONS)
    self.assertEqual(len(mock_defer.mock_calls), 4)
    self.assertTrue(config_model.Config.get(
        'bootstrap_started'))

  @mock.patch('__main__.bootstrap.constants.BOOTSTRAP_ENABLED', False)
  def test_run_bootstrap_while_disabled(self):
    """Tests that bootstrapping is disallowed when constant False."""
    with self.assertRaises(bootstrap.Error):
      bootstrap.run_bootstrap({'bootstrap_fake_method': {}})

  @mock.patch('__main__.bootstrap.constants.BOOTSTRAP_ENABLED', True)
  @mock.patch('__main__.bootstrap.datastore_yaml.import_yaml')
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
    self.assertTrue(expected_model.timestamp < datetime.datetime.utcnow())

  @mock.patch('__main__.bootstrap.constants.BOOTSTRAP_ENABLED', True)
  @mock.patch('__main__.bootstrap.datastore_yaml.import_yaml')
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
    self.assertTrue(expected_model.timestamp < datetime.datetime.utcnow())

  @mock.patch('__main__.bootstrap.constants.BOOTSTRAP_ENABLED', True)
  @mock.patch('__main__.bootstrap.datastore_yaml.import_yaml')
  def test_bootstrap_datastore_yaml(self, mock_importyaml):
    """Tests bootstrap_datastore_yaml."""
    bootstrap.bootstrap_datastore_yaml(user_email='foo')
    yaml_file_to_string = open(os.path.join(
        os.path.dirname(__file__), 'bootstrap.yaml')).read()
    mock_importyaml.assert_called_once_with(
        yaml_file_to_string, 'foo', True)

  @mock.patch('__main__.bootstrap.logging.info')
  @mock.patch('__main__.bootstrap.logging.warn')
  @mock.patch('__main__.bootstrap.constants.BOOTSTRAP_ENABLED', True)
  @mock.patch('__main__.bootstrap.directory.DirectoryApiClient')
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
    mock_client.insert_org_unit.assert_not_called()
    mock_logwarn.assert_has_calls([
        mock.call(bootstrap._ORG_UNIT_EXISTS_MSG, org_unit_name) for
        org_unit_name in bootstrap.constants.ORG_UNIT_DICT
    ])

  @mock.patch.object(bigquery, 'BigQueryClient')
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

  def test_is_bootstrap_completed(self):
    """Tests is_bootstrap_completed under myriad circumstances."""
    self.assertFalse(bootstrap.is_bootstrap_completed())

    bootstrap.config_model.Config.set('bootstrap_started', True)
    self.assertFalse(bootstrap.is_bootstrap_completed())

    bootstrap.config_model.Config.set('bootstrap_completed', False)
    self.assertFalse(bootstrap.is_bootstrap_completed())

    bootstrap.config_model.Config.set('bootstrap_completed', True)
    self.assertTrue(bootstrap.is_bootstrap_completed())

  def test_is_bootstrap_started(self):
    self.assertFalse(bootstrap.is_bootstrap_started())

    bootstrap.config_model.Config.set('bootstrap_started', True)
    self.assertTrue(bootstrap.is_bootstrap_started())

  @mock.patch('__main__.bootstrap.constants.BOOTSTRAP_ENABLED', True)
  @mock.patch('__main__.bootstrap.get_all_bootstrap_functions')
  def test_get_bootstrap_task_status(self, mock_getall):
    """Tests get_bootstrap_task_status."""
    yesterday = datetime.datetime.utcnow() - datetime.timedelta(days=-1)

    def fake_function1():
      pass

    def fake_function2():
      pass

    mock_getall.return_value = {
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
    fake_entity2.success = False
    fake_entity2.timestamp = yesterday
    fake_entity2.details = 'Exception raise we failed oh no.'
    fake_entity2.put()

    status = bootstrap.get_bootstrap_task_status()
    self.assertEqual(len(status), 2)


if __name__ == '__main__':
  loanertest.main()
