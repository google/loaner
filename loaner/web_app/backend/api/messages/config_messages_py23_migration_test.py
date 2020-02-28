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
"""Tests for web_app.backend.api.messages.config_messages."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from loaner.web_app.backend.api.messages import config_messages
from absl.testing import absltest


class ConfigMessagesPy23MigrationTest(absltest.TestCase):

  def testGetConfigRequest(self):
    config = config_messages.GetConfigRequest(
        name='test', config_type=config_messages.ConfigType(1))
    self.assertEqual(config.name, 'test')
    self.assertEqual(config.config_type.name, 'STRING')

  def testConfigResponse(self):
    config = config_messages.ConfigResponse(
        name='test',
        string_value='test',
        integer_value=1,
        boolean_value=False,
        list_value=['test'])
    self.assertEqual(config.name, 'test')
    self.assertEqual(config.string_value, 'test')
    self.assertEqual(config.integer_value, 1)
    self.assertEqual(config.boolean_value, False)
    self.assertEqual(config.list_value, ['test'])

  def testListConfigsResponse(self):
    config = config_messages.ListConfigsResponse(
        configs=[config_messages.ConfigResponse(name='test')])
    self.assertEqual(config.configs[0].name, 'test')

  def testUpdateConfigRequest(self):
    config = config_messages.UpdateConfigRequest(
        config=[config_messages.UpdateConfig(name='test')])
    self.assertEqual(config.config[0].name, 'test')

  def testUpdateConfig(self):
    config = config_messages.UpdateConfig(
        name='test',
        config_type=config_messages.ConfigType(1),
        integer_value=1,
        boolean_value=False,
        list_value=['test'])
    self.assertEqual(config.name, 'test')
    self.assertEqual(config.config_type.name, 'STRING')
    self.assertEqual(config.integer_value, 1)
    self.assertEqual(config.boolean_value, False)
    self.assertEqual(config.list_value, ['test'])

if __name__ == '__main__':
  absltest.main()
