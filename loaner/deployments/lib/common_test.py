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

import __builtin__
import os

from absl import flags
from absl import logging
from absl.testing import parameterized
from pyfakefs import fake_filesystem
from pyfakefs import mox3_stubout

import mock

from absl.testing import absltest
from loaner.deployments.lib import common

_CONFIG = """
dev:
  project_id: test_project
  client_id: test_client_id
  client_secret: test_client_secret
  custom_bucket:
"""

_INCORRECT_CONFIG = """
dev:
  project_id:
  client_id: test_client_id
  client_secret: test_client_secret
  custom_bucket:
"""


class CommonTest(parameterized.TestCase, absltest.TestCase):

  def setUp(self):
    super(CommonTest, self).setUp()
    # Save the real modules for clean up.
    self.real_open = __builtin__.open
    self.real_file = __builtin__.file
    # Create a fake file system and stub out builtin modules.
    self.fs = fake_filesystem.FakeFilesystem()
    self.os = fake_filesystem.FakeOsModule(self.fs)
    self.open = fake_filesystem.FakeFileOpen(self.fs)
    self.stubs = mox3_stubout.StubOutForTesting()
    self.stubs.SmartSet(__builtin__, 'open', self.open)
    self.stubs.SmartSet(common, 'os', self.os)

  def tearDown(self):
    super(CommonTest, self).tearDown()
    self.stubs.UnsetAll()
    __builtin__.open = self.real_open
    __builtin__.file = self.real_file

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

  @parameterized.named_parameters(
      {'testcase_name': 'CustomBucketDefined', 'project_name': 'test_project',
       'bucket_name': 'bucket', 'expected_bucket_name': 'bucket'},
      {'testcase_name': 'NoBucketDefined', 'project_name': 'test_project',
       'bucket_name': None, 'expected_bucket_name': 'test_project-gng-loaner'},
  )
  def test_project_config_constructor(
      self, project_name, bucket_name, expected_bucket_name):
    """Test the direct construction of ProjectConfig."""
    test_config = common.ProjectConfig(
        project_name, 'test_client_id', 'test_client_secret', bucket_name)
    self.assertEqual(project_name, test_config.project)
    self.assertEqual('test_client_id', test_config.client_id)
    self.assertEqual('test_client_secret', test_config.client_secret)
    self.assertEqual(expected_bucket_name, test_config.bucket)
    self.assertEqual(
        '{}/configs'.format(expected_bucket_name), test_config.configs)
    # Test that two objects with the same constructor args are equal.
    self.assertEqual(test_config, common.ProjectConfig(
        project_name, 'test_client_id', 'test_client_secret', bucket_name))
    # Test that two object with different constructor args are not equal.
    self.assertNotEqual(test_config, common.ProjectConfig(
        project_name, 'test_client_id', 'test_client_secret', 'INCORRECT'))
    # Test the string and representations for ProjectConfig.
    self.assertEqual(
        'ProjectConfig for project: test_project.', str(test_config))
    self.assertEqual(
        '<ProjectConfig({}, test_client_id, test_client_secret, {})>'.format(
            project_name, expected_bucket_name), repr(test_config))

  def test_project_config_from_yaml(self):
    """Test the construction of ProjectConfig when loaded from a config file."""
    expected_config = common.ProjectConfig(
        'test_project', 'test_client_id', 'test_client_secret', None)
    config_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'config.yaml')
    self.fs.CreateFile(config_file, contents=_CONFIG)
    test_config = common.ProjectConfig.from_yaml('dev', config_file)
    self.assertEqual(expected_config, test_config)

  def test_project_config_from_yaml_missing_fields(self):
    """Test an error is raised if a required field is missing in the config."""
    config_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'config.yaml')
    self.fs.CreateFile(config_file, contents=_INCORRECT_CONFIG)
    with self.assertRaises(common.ConfigError):
      common.ProjectConfig.from_yaml('dev', config_file)


if __name__ == '__main__':
  absltest.main()
