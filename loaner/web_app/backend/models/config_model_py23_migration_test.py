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

# Lint as: python3
"""Tests for web_app.backend.models.config_model_py23_migration."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import mock
from loaner.web_app.backend.models import config_model
from absl.testing import absltest


class ConfigModelPy23MigrationTest(absltest.TestCase):

  def testConfigProperties(self):
    self.assertEqual(True, config_model.Config.bool_value)
    self.assertEqual('test', config_model.Config.string_value)
    self.assertEqual(1, config_model.Config.integer_value)
    self.assertEqual('test', config_model.Config.list_value)

  @mock.patch.object(config_model.memcache, 'get')
  def testGetMemcacheConfig(self, mock_get):
    mock_get.return_value = 'mock_memcache'
    config_model.Config.get('test_name')
    mock_get.assert_called_with('test_name')

  @mock.patch.object(config_model.memcache, 'set')
  @mock.patch.object(config_model.Config, 'get_by_id')
  @mock.patch.object(config_model.memcache, 'get')
  def testGet(self, mock_get, mock_get_by_id, mock_set):
    mock_get.return_value = ''
    mock_get_by_id.return_value = mock.MagicMock(
        string_value='test_string',
        integer_value=10,
        bool_value=True,
        list_value=['test_list'])
    mock_set.return_value = 'test_memcache'
    config_model.Config.get('test_name')
    mock_get.assert_called_with('test_name')
    mock_get_by_id.assert_called_with('test_name', use_memcache=False)
    mock_set.assert_called_with('test_name', 'test_string')

  @mock.patch.object(config_model.memcache, 'set')
  @mock.patch.object(config_model.Config, 'get_by_id')
  @mock.patch.object(config_model.memcache, 'get')
  def testGetwithInt(self, mock_get, mock_get_by_id, mock_set):
    mock_get.return_value = ''
    mock_get_by_id.return_value = mock.MagicMock(
        string_value='',
        integer_value=10,
        bool_value=True,
        list_value=['test_list'])
    mock_set.return_value = 'test_memcache'
    config_model.Config.get('test_name')
    mock_get.assert_called_with('test_name')
    mock_get_by_id.assert_called_with('test_name', use_memcache=False)
    mock_set.assert_called_with('test_name', 10)

  @mock.patch.object(config_model.memcache, 'set')
  @mock.patch.object(config_model.Config, 'get_by_id')
  @mock.patch.object(config_model.memcache, 'get')
  def testGetwithBool(self, mock_get, mock_get_by_id, mock_set):
    mock_get.return_value = ''
    mock_get_by_id.return_value = mock.MagicMock(
        string_value='',
        integer_value=0,
        bool_value=True,
        list_value=['test_list'])
    mock_set.return_value = 'test_memcache'
    config_model.Config.get('test_name')
    mock_get.assert_called_with('test_name')
    mock_get_by_id.assert_called_with('test_name', use_memcache=False)
    mock_set.assert_called_with('test_name', True)

  @mock.patch.object(config_model.memcache, 'set')
  @mock.patch.object(config_model.Config, 'get_by_id')
  @mock.patch.object(config_model.memcache, 'get')
  def testGetwithList(self, mock_get, mock_get_by_id, mock_set):
    mock_get.return_value = ''
    mock_get_by_id.return_value = mock.MagicMock(
        string_value='',
        integer_value=0,
        bool_value=None,
        list_value=['test_list'])
    mock_set.return_value = 'test_memcache'
    config_model.Config.get('test_name')
    mock_get.assert_called_with('test_name')
    mock_get_by_id.assert_called_with('test_name', use_memcache=False)
    mock_set.assert_called_with('test_name', ['test_list'])

  @mock.patch.object(config_model.Config, 'set')
  @mock.patch.object(config_model.utils, 'load_config_from_yaml')
  @mock.patch.object(config_model.Config, 'get_by_id')
  @mock.patch.object(config_model.memcache, 'get')
  def testGetwithonly(self, mock_get, mock_get_by_id, mock_yaml,
                      mock_config_set):
    mock_get.return_value = ''
    mock_get_by_id.return_value = ''
    mock_yaml.return_value = {'test_name': 'name'}
    config_model.Config.get('test_name')
    mock_config_set.assert_called_with('test_name', 'name')

  @mock.patch.object(config_model.memcache, 'set')
  @mock.patch.object(config_model.Config, 'get_or_insert')
  @mock.patch.object(config_model.utils, 'load_config_from_yaml')
  def testSetWithStringValue(self, mock_yaml, mock_get_insert, mock_set):
    mock_yaml.return_value = {'test': 'test_value'}
    stored_config_mock = mock.Mock()
    stored_config_mock.string_value = 'test_value'
    stored_config_mock.is_global = True
    mock_get_insert.return_value = stored_config_mock

    config_model.Config.set('test', 'test_value')
    mock_set.assert_called_with('test', 'test_value')
    mock_yaml.assert_called()
    mock_get_insert.assert_called_with('test')

  @mock.patch.object(config_model.memcache, 'set')
  @mock.patch.object(config_model.Config, 'get_or_insert')
  @mock.patch.object(config_model.utils, 'load_config_from_yaml')
  def testSetWithIntValue(self, mock_yaml, mock_get_insert, mock_set):
    mock_yaml.return_value = {'test': 'test_value'}
    stored_config_mock = mock.Mock()
    stored_config_mock.string_value = 'test_value'
    stored_config_mock.is_global = True
    mock_get_insert.return_value = stored_config_mock
    config_model.Config.set('test', 1)
    mock_set.assert_called_with('test', 1)
    mock_yaml.assert_called()
    mock_get_insert.assert_called_with('test')
    config_model.Config.set('test', [1])

  @mock.patch.object(config_model.memcache, 'set')
  @mock.patch.object(config_model.Config, 'get_or_insert')
  @mock.patch.object(config_model.utils, 'load_config_from_yaml')
  def testSetWithListValue(self, mock_yaml, mock_get_insert, mock_set
                          ):
    mock_yaml.return_value = {'test': 'test_value'}
    stored_config_mock = mock.Mock()
    stored_config_mock.string_value = 'test_value'
    stored_config_mock.is_global = True
    mock_get_insert.return_value = stored_config_mock
    config_model.Config.set('test', [1])
    mock_set.assert_called_with('test', [1])
    mock_yaml.assert_called()
    mock_get_insert.assert_called_with('test')


if __name__ == '__main__':
  absltest.main()
