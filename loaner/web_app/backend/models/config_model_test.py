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

"""Tests for backend.models.configuration_model."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import itertools

from absl.testing import parameterized

from google.appengine.api import memcache

from loaner.web_app import config_defaults
from loaner.web_app.backend.models import config_model
from loaner.web_app.backend.testing import loanertest


def _create_config_parameters():
  """Creates a config value pair for parameterized test cases.

  Yields:
    A list containing the list of configs and their values.
  """
  string_config_value = 'config value 1'
  integer_config_value = 1
  bool_config_value = True
  list_config_value = ['email1', 'email2']
  config_ids = [
      'string_config', 'integer_config', 'bool_config', 'list_config']
  config_values = [
      string_config_value,
      integer_config_value, bool_config_value, list_config_value]
  for i in itertools.izip(config_ids, config_values):
    yield [i]


class ConfigurationTest(
    parameterized.TestCase, loanertest.TestCase):

  def setUp(self):
    super(ConfigurationTest, self).setUp()

    config_model.Config(
        id='string_config', string_value='config value 1').put()
    config_model.Config(id='integer_config', integer_value=1).put()
    config_model.Config(id='bool_config', bool_value=True).put()
    config_model.Config(
        id='list_config', list_value=['email1', 'email2']).put()

  @parameterized.parameters(_create_config_parameters())
  def test_get_from_datastore(self, test_config):
    config = config_model.Config.get(test_config[0])
    self.assertEqual(config, test_config[1])

  def test_get_from_memcache(self):
    config = 'string_config'
    config_value = 'this should be read.'
    memcache.set(config, config_value)
    reference_datastore_config = config_model.Config.get_by_id(config)
    config_memcache = config_model.Config.get(config)

    self.assertEqual(config_memcache, config_value)
    self.assertEqual(
        reference_datastore_config.string_value, 'config value 1')

  @parameterized.parameters(_create_config_parameters())
  def test_get_from_default(self, test_config):
    config = 'test_config'
    config_defaults.DEFAULTS[config] = test_config[1]
    config_datastore = config_model.Config.get(config)
    self.assertEqual(config_datastore, test_config[1])
    self.assertIsNone(memcache.get(config))
    self.assertIsNone(config_model.Config.get_by_id(config))

  def test_get_nonexistent(self):
    with self.assertRaisesRegexp(KeyError, config_model._CONFIG_NOT_FOUND_MSG):
      config_model.Config.get('does_not_exist')

  @parameterized.parameters(_create_config_parameters())
  def test_set(self, test_config):
    config_defaults.DEFAULTS[test_config[0]] = test_config[1]
    config_model.Config.set(test_config[0], test_config[1])
    memcache_config = memcache.get(test_config[0])
    config = config_model.Config.get(test_config[0])

    self.assertEqual(memcache_config, test_config[1])
    self.assertEqual(config, test_config[1])

  def test_set_nonexistent(self):
    with self.assertRaisesRegexp(KeyError, config_model._CONFIG_NOT_FOUND_MSG):
      config_model.Config.set('fake', 'does_not_exist')


if __name__ == '__main__':
  loanertest.main()
