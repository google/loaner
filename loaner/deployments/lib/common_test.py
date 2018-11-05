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

"""Tests for deployments.common."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

# Prefer Python 3 and fall back on Python 2.
# pylint:disable=g-statement-before-imports,g-import-not-at-top
try:
  import builtins
except ImportError:
  import __builtin__ as builtins
# pylint:enable=g-statement-before-imports,g-import-not-at-top

import os

from absl import flags
from absl import logging
from absl.testing import parameterized
from pyfakefs import fake_filesystem
from pyfakefs import mox3_stubout

import mock
import yaml

from absl.testing import absltest
from loaner.deployments.lib import common
from loaner.deployments.lib import utils

_EMPTY_CONFIG = """
default:
  project_id:
  client_id:
  client_secret:
  bucket:
"""

_INCORRECT_CONFIG = """
dev:
  project_id:
  client_id: test_client_id
  client_secret: test_client_secret
  bucket:
"""

_SINGLE_CONFIG = """
dev:
  project_id: test_project
  client_id: test_client_id
  client_secret: test_client_secret
  bucket:
"""

_MULTI_CONFIG = """
dev:
  project_id: test_project
  client_id: test_client_id
  client_secret: test_client_secret
  bucket:
default:
  project_id: default_project
  client_id: default_client_id
  client_secret: default_client_secret
  bucket: default_project.appspot.com
"""


class CommonTest(parameterized.TestCase, absltest.TestCase):

  def setUp(self):
    super(CommonTest, self).setUp()
    # Save the real modules for clean up.
    self.real_open = builtins.open
    # Create a fake file system and stub out builtin modules.
    self.fs = fake_filesystem.FakeFilesystem()
    self.os = fake_filesystem.FakeOsModule(self.fs)
    self.open = fake_filesystem.FakeFileOpen(self.fs)
    self.stubs = mox3_stubout.StubOutForTesting()
    self.stubs.SmartSet(builtins, 'open', self.open)
    self.stubs.SmartSet(common, 'os', self.os)

  def tearDown(self):
    super(CommonTest, self).tearDown()
    self.stubs.UnsetAll()
    builtins.open = self.real_open

  @parameterized.parameters(
      ('/this/config/file.yaml', '/this/config/file.yaml', 0),
      (os.path.join(
          os.path.dirname(os.path.abspath(__file__)), '..', 'config.yaml'),
       'config.yaml', 1),
  )
  @mock.patch.object(logging, 'debug')
  def test_get_config_file_path(
      self, expected_path, provided_path, logging_call, mock_debug):
    """Test the config file path."""
    self.fs.CreateFile(expected_path)
    test_path = common._get_config_file_path(provided_path)
    self.assertEqual(logging_call, mock_debug.call_count)
    self.assertEqual(expected_path, test_path)

  def test_config_file_validator(self):
    """Test the config file validation."""
    self.fs.CreateFile('/this/config/file.yaml')
    self.assertTrue(common._config_file_validator('/this/config/file.yaml'))

  def test_config_file_validator_error_does_not_exist(self):
    """Test the config file validation fails for invalid config files."""
    with self.assertRaises(flags.ValidationError):
      common._config_file_validator('/this/config/file.yaml')

  def test_config_file_validator_error_not_yaml(self):
    """Test the config file validation fails for invalid config files."""
    file_path = '/this/config/file.json'
    self.fs.CreateFile(file_path)
    with self.assertRaises(flags.ValidationError):
      common._config_file_validator(file_path)

  def test_get_available_configs(self):
    path = '/this/config/file.yaml'
    self.fs.CreateFile(path, contents=_MULTI_CONFIG)
    self.assertEqual(['default', 'dev'], common.get_available_configs(path))

  @parameterized.named_parameters(
      {'testcase_name': 'CustomBucketDefined', 'project_name': 'test_project',
       'bucket_name': 'bucket', 'expected_bucket_name': 'bucket'},
      {'testcase_name': 'NoBucketDefined', 'project_name': 'test_project',
       'bucket_name': None, 'expected_bucket_name': 'test_project.appspot.com'},
  )
  def test_project_config_constructor(
      self, project_name, bucket_name, expected_bucket_name):
    """Test the direct construction of ProjectConfig."""
    test_config = common.ProjectConfig(
        'dev', project_name, 'test_client_id', 'test_client_secret',
        bucket_name, '/this/config/file.yaml')
    self.assertEqual(project_name, test_config.project)
    self.assertEqual('test_client_id', test_config.client_id)
    self.assertEqual('test_client_secret', test_config.client_secret)
    self.assertEqual(expected_bucket_name, test_config.bucket)
    self.assertEqual(
        'configs/constants.json', test_config.constants_storage_path)
    self.assertEqual('/this/config/file.yaml', test_config.path)
    # Test that two objects with the same constructor args are equal.
    self.assertEqual(test_config, common.ProjectConfig(
        'dev', project_name, 'test_client_id', 'test_client_secret',
        bucket_name, '/this/config/file.yaml'))
    # Test that two object with different constructor args are not equal.
    self.assertNotEqual(test_config, common.ProjectConfig(
        'dev', project_name, 'test_client_id', 'test_client_secret',
        'INCORRECT', '/this/config/file.yaml'))
    # Test the string and representations for ProjectConfig.
    self.assertEqual(
        "ProjectConfig for project 'test_project'.", str(test_config))
    self.assertEqual(
        '<ProjectConfig(dev, {}, test_client_id, test_client_secret, {}, '
        '/this/config/file.yaml)>'.format(project_name, expected_bucket_name),
        repr(test_config))

  def test_project_config_from_yaml(self):
    """Test the construction of ProjectConfig when loaded from a config file."""
    config_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'config.yaml')
    expected_config = common.ProjectConfig(
        'dev', 'test_project', 'test_client_id', 'test_client_secret', None,
        config_file,
    )
    self.fs.CreateFile(config_file, contents=_SINGLE_CONFIG)
    test_config = common.ProjectConfig.from_yaml('dev', config_file)
    self.assertEqual(expected_config, test_config)

  def test_project_config_from_yaml_missing_fields(self):
    """Test an error is raised if a required field is missing in the config."""
    config_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'config.yaml')
    self.fs.CreateFile(config_file, contents=_INCORRECT_CONFIG)
    with self.assertRaises(common.ConfigError):
      common.ProjectConfig.from_yaml('dev', config_file)

  def test_from_prompts(self):
    expected_response = common.ProjectConfig(
        'test', 'fake_project', 'fake_client_id', 'fake_client_secret', None,
        '/this/config/file.yaml',
    )
    prompt_return = ['fake_project', 'fake_client_id', 'fake_client_secret']
    with mock.patch.object(
        utils, 'prompt_string', side_effect=prompt_return) as mock_prompt:
      self.assertEqual(
          common.ProjectConfig.from_prompts('test', '/this/config/file.yaml'),
          expected_response)
      self.assertEqual(mock_prompt.call_count, 3)

  def test_write(self):
    expected_dict = {
        'project_id': 'test_project',
        'client_id': 'test_client_id',
        'client_secret': 'test_client_secret',
        'bucket': 'test_project.appspot.com',
    }
    self.fs.CreateFile('/this/config/file.yaml', contents=_EMPTY_CONFIG)
    test_config = common.ProjectConfig(
        'asdf', 'test_project', 'test_client_id', 'test_client_secret', None,
        '/this/config/file.yaml',
    )
    test_config.write()
    with open('/this/config/file.yaml') as config_file:
      config = yaml.safe_load(config_file)
    self.assertEqual(config['asdf'], expected_dict)


if __name__ == '__main__':
  absltest.main()
