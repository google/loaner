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

"""Tests for backend.api.config_api."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from absl.testing import parameterized

import mock

from protorpc import message_types

from loaner.web_app.backend.api import config_api
from loaner.web_app.backend.api.messages import config_messages
from loaner.web_app.backend.lib import utils
from loaner.web_app.backend.models import config_model
from loaner.web_app.backend.testing import loanertest


class ConfigApiTest(parameterized.TestCase, loanertest.EndpointsTestCase):

  def setUp(self):
    super(ConfigApiTest, self).setUp()
    self.service = config_api.ConfigAPI()
    self.login_admin_endpoints_user()

    self.patcher_xsrf = mock.patch(
        '__main__.config_api.root_api.Service.check_xsrf_token')
    self.mock_xsrf = self.patcher_xsrf.start()

    self.existing_string_config_in_datastore = config_model.Config(
        id='test_config_string', string_value='test_config_value')

    self.existing_bool_config_in_datastore = config_model.Config(
        id='test_config_bool', bool_value=False)

    self.existing_int_config_in_datastore = config_model.Config(
        id='test_config_int', integer_value=7)

    self.existing_list_config_in_datastore = config_model.Config(
        id='test_config_list', list_value=['Group'])

    self.existing_string_config_in_datastore.put()
    self.existing_bool_config_in_datastore.put()
    self.existing_int_config_in_datastore.put()
    self.existing_list_config_in_datastore.put()

  def tearDown(self):
    super(ConfigApiTest, self).tearDown()
    self.service = None

  def test_get_config_invalid_setting(self):
    request = config_messages.GetConfigRequest(
        name='Not Valid',
        config_type=config_messages.ConfigType.STRING)
    self.assertRaisesRegexp(
        config_api.endpoints.BadRequestException,
        'No such name',
        self.service.get_config,
        request)

  def test_get_config_missing_fields(self):
    request = config_messages.GetConfigRequest()
    with self.assertRaises(config_api.endpoints.BadRequestException):
      self.service.get_config(request)

  def test_get_config_string_setting(self):
    request = config_messages.GetConfigRequest(
        name='test_config_string',
        config_type=config_messages.ConfigType.STRING)
    response = self.service.get_config(request)
    self.assertEqual(
        self.existing_string_config_in_datastore.string_value,
        response.string_value)

  def test_get_config_bool_setting(self):
    request = config_messages.GetConfigRequest(
        name='test_config_bool',
        config_type=config_messages.ConfigType.BOOLEAN)
    response = self.service.get_config(request)
    self.assertEqual(
        self.existing_bool_config_in_datastore.bool_value,
        response.boolean_value)

  def test_get_config_int_setting(self):
    request = config_messages.GetConfigRequest(
        name='test_config_int',
        config_type=config_messages.ConfigType.INTEGER)
    response = self.service.get_config(request)
    self.assertEqual(
        self.existing_int_config_in_datastore.integer_value,
        response.integer_value)

  def test_get_config_list_setting(self):
    request = config_messages.GetConfigRequest(
        name='test_config_list',
        config_type=config_messages.ConfigType.LIST)
    response = self.service.get_config(request)
    self.assertEqual(
        self.existing_list_config_in_datastore.list_value,
        response.list_value)

  @mock.patch.object(utils, 'load_config_from_yaml')
  def test_list_configs(self, mock_load_config_from_yaml):
    mock_configs = {
        'string_config': 'config value 1',
        'integer_config': 1,
        'bool_config': True,
        'list_config': ['email1', 'email2'],
    }
    mock_load_config_from_yaml.return_value = mock_configs
    request = message_types.VoidMessage()
    response = self.service.list_configs(request)

    self.assertLen(response.configs, 4)

  def test_update_config_value_does_not_exist(self):
    request = config_messages.UpdateConfigRequest(
        config=[config_messages.UpdateConfig(
            name='Does not exist!',
            config_type=config_messages.ConfigType.BOOLEAN,
            boolean_value=False)])
    self.assertRaisesRegexp(
        config_api.endpoints.BadRequestException,
        'No such name',
        self.service.update_config,
        request)

  @mock.patch.object(utils, 'load_config_from_yaml')
  def test_update_config_multi(self, mock_load_config_from_yaml):
    new_string_value = 'new_string_value'
    new_int_value = 9
    mock_load_config_from_yaml.return_value = {
        'test_config_integer': 2,
        'test_config_string': 'old_string_value',
    }
    request = config_messages.UpdateConfigRequest(
        config=[
            config_messages.UpdateConfig(
                name='test_config_integer',
                config_type=config_messages.ConfigType.INTEGER,
                integer_value=new_int_value),
            config_messages.UpdateConfig(
                name='test_config_string',
                config_type=config_messages.ConfigType.STRING,
                string_value=new_string_value)
        ])
    self.service.update_config(request)
    updated_string_value = config_model.Config.get(name='test_config_string')
    self.assertEqual(updated_string_value, new_string_value)
    updated_int_value = config_model.Config.get(name='test_config_integer')
    self.assertEqual(updated_int_value, new_int_value)

  @parameterized.parameters(
      ('test_config_list', ['email1', 'email2'], 'list_value',),
      ('test_config_integer', 5, 'integer_value',),
      ('test_config_string', 'File a ticket!', 'string_value',),
      ('test_config_bool', False, 'boolean_value',))
  @mock.patch.object(utils, 'load_config_from_yaml')
  def test_update_config(
      self, mock_config, mock_config_value, config_value_type,
      mock_load_config_from_yaml):
    mock_load_config_from_yaml.return_value = {mock_config: mock_config_value}
    request = _create_config_request(
        config_value_type, mock_config, mock_config_value)
    response = self.service.update_config(request)
    self.assertIsInstance(response, message_types.VoidMessage)
    setting_value = config_model.Config.get(name=mock_config)
    self.assertEqual(setting_value, mock_config_value)


def _create_config_request(config_value_type, mock_config, mock_config_value):
  """Creates a config_messages UpdateConfigRequest for testing.

  Args:
    config_value_type: str, the type of value.
    mock_config: str, the name of the config.
    mock_config_value: str, bool, int, list, the config value.

  Returns:
    A config_messages.UpdateConfigRequest ProtoRPC message.
  """
  if config_value_type == 'list_value':
    config = [
        config_messages.UpdateConfig(
            name=mock_config,
            config_type=config_messages.ConfigType.LIST,
            list_value=mock_config_value)]
  elif config_value_type == 'integer_value':
    config = [
        config_messages.UpdateConfig(
            name=mock_config,
            config_type=config_messages.ConfigType.INTEGER,
            integer_value=mock_config_value)]
  elif config_value_type == 'string_value':
    config = [
        config_messages.UpdateConfig(
            name=mock_config,
            config_type=config_messages.ConfigType.STRING,
            string_value=mock_config_value)]
  elif config_value_type == 'boolean_value':
    config = [
        config_messages.UpdateConfig(
            name=mock_config,
            config_type=config_messages.ConfigType.BOOLEAN,
            boolean_value=mock_config_value)]

  return config_messages.UpdateConfigRequest(config=config)


if __name__ == '__main__':
  loanertest.main()
