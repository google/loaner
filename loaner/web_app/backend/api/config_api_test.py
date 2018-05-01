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

import mock

from protorpc import message_types

from loaner.web_app import config_defaults
from loaner.web_app.backend.api import config_api
from loaner.web_app.backend.api.messages import config_message
from loaner.web_app.backend.models import config_model
from loaner.web_app.backend.testing import loanertest


class ConfigApiTest(loanertest.EndpointsTestCase):

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
    request = config_message.GetConfigRequest(
        name='Not Valid',
        config_type=config_message.ConfigType.STRING)
    self.assertRaisesRegexp(
        config_api.endpoints.BadRequestException,
        'No such name',
        self.service.get_config,
        request)

  def test_get_config_missing_fields(self):
    request = config_message.GetConfigRequest()
    with self.assertRaises(config_api.endpoints.BadRequestException):
      self.service.get_config(request)

  def test_get_config_string_setting(self):
    request = config_message.GetConfigRequest(
        name='test_config_string',
        config_type=config_message.ConfigType.STRING)
    response = self.service.get_config(request)
    self.assertEqual(
        self.existing_string_config_in_datastore.string_value,
        response.string_value)

  def test_get_config_bool_setting(self):
    request = config_message.GetConfigRequest(
        name='test_config_bool',
        config_type=config_message.ConfigType.BOOLEAN)
    response = self.service.get_config(request)
    self.assertEqual(
        self.existing_bool_config_in_datastore.bool_value,
        response.boolean_value)

  def test_get_config_int_setting(self):
    request = config_message.GetConfigRequest(
        name='test_config_int',
        config_type=config_message.ConfigType.INTEGER)
    response = self.service.get_config(request)
    self.assertEqual(
        self.existing_int_config_in_datastore.integer_value,
        response.integer_value)

  def test_get_config_list_setting(self):
    request = config_message.GetConfigRequest(
        name='test_config_list',
        config_type=config_message.ConfigType.LIST)
    response = self.service.get_config(request)
    self.assertEqual(
        self.existing_list_config_in_datastore.list_value,
        response.list_value)

  def test_list_configs(self):
    request = message_types.VoidMessage()
    response = self.service.list_configs(request)

    # Make sure that the response contains all of the config in
    # config.py.
    self.assertTrue(
        len(response.configs),
        len(config_defaults.DEFAULTS))
    for response_config in response.configs:
      self.assertTrue(
          response_config.name in
          config_defaults.DEFAULTS)

  def test_update_config_bad_request(self):
    request = config_message.UpdateConfigRequest()
    with self.assertRaises(config_api.endpoints.BadRequestException):
      self.service.update_config(request)

  def test_update_config_value_does_not_exist(self):
    request = config_message.UpdateConfigRequest(
        name='Does not exist!',
        config_type=config_message.ConfigType.BOOLEAN,
        boolean_value=False)
    self.assertRaisesRegexp(
        config_api.endpoints.BadRequestException,
        'No such name',
        self.service.update_config,
        request)

  def test_update_config_boolean(self):
    mock_config = 'test_config_bool'
    mock_config_value = False
    config_defaults.DEFAULTS[mock_config] = mock_config_value
    request = config_message.UpdateConfigRequest(
        name=mock_config,
        config_type=config_message.ConfigType.BOOLEAN,
        boolean_value=mock_config_value)
    response = self.service.update_config(request)
    self.assertIsInstance(response, message_types.VoidMessage)
    setting_value = config_model.Config.get(name=mock_config)
    self.assertEqual(setting_value, mock_config_value)

  def test_update_config_string(self):
    mock_config = 'test_config_string'
    mock_config_value = 'File a ticket!'
    config_defaults.DEFAULTS[mock_config] = mock_config_value
    request = config_message.UpdateConfigRequest(
        name=mock_config,
        config_type=config_message.ConfigType.STRING,
        string_value=mock_config_value)
    response = self.service.update_config(request)
    self.assertIsInstance(response, message_types.VoidMessage)
    setting_value = config_model.Config.get(name=mock_config)
    self.assertEqual(setting_value, mock_config_value)

  def test_update_config_integer(self):
    mock_config = 'test_config_integer'
    mock_config_value = 5
    config_defaults.DEFAULTS[mock_config] = mock_config_value
    request = config_message.UpdateConfigRequest(
        name=mock_config,
        config_type=config_message.ConfigType.INTEGER,
        integer_value=mock_config_value)
    response = self.service.update_config(request)
    self.assertIsInstance(response, message_types.VoidMessage)
    setting_value = config_model.Config.get(name=mock_config)
    self.assertEqual(setting_value, mock_config_value)

  def test_update_config_list(self):
    mock_config = 'test_config_list'
    mock_config_value = ['email1', 'email2']
    config_defaults.DEFAULTS[mock_config] = mock_config_value
    request = config_message.UpdateConfigRequest(
        name=mock_config,
        config_type=config_message.ConfigType.LIST,
        list_value=mock_config_value)
    response = self.service.update_config(request)
    self.assertIsInstance(response, message_types.VoidMessage)
    setting_value = config_model.Config.get(name=mock_config)
    self.assertEqual(setting_value, mock_config_value)


if __name__ == '__main__':
  loanertest.main()
