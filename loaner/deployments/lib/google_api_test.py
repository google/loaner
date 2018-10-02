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

"""Tests for deployments.lib.google_api."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from absl.testing import parameterized

import mock

from absl.testing import absltest
from loaner.deployments.lib import auth
from loaner.deployments.lib import common
from loaner.deployments.lib import google_api


class GoogleApiTest(parameterized.TestCase, absltest.TestCase):

  def setUp(self):
    super(GoogleApiTest, self).setUp()
    self.config = common.ProjectConfig(
        'TEST_KEY', 'TEST_PROJECT', 'TEST_CLIENT_ID', 'TEST_CLIENT_SECRET',
        'TEST_BUCKET', '/this/path.yaml')

  def test_init(self):
    """Test the initialization of the GoogleAPI class."""
    test_google_api = google_api.GoogleAPI(self.config, mock.Mock())
    self.assertEqual(self.config, test_google_api._config)
    self.assertEqual(
        'GoogleAPI for project: "TEST_PROJECT"', str(test_google_api))
    self.assertEqual(
        '<GoogleAPI.from_config(<ProjectConfig(TEST_KEY, TEST_PROJECT, '
        'TEST_CLIENT_ID, TEST_CLIENT_SECRET, TEST_BUCKET, /this/path.yaml)>)>',
        repr(test_google_api))

  @mock.patch.object(auth, 'CloudCredentials', autospec=True)
  def test_from_config(self, mock_creds):
    """Test the initialization of the GoogleAPI class from config."""
    del mock_creds  # Unused.
    google_api.GoogleAPI.SCOPES = ['VALID_SCOPE']
    google_api.GoogleAPI.SERVICE = 'VALID_SERVICE'
    google_api.GoogleAPI.VERSION = '1'
    test_google_api = google_api.GoogleAPI.from_config(self.config)
    self.assertEqual(self.config, test_google_api._config)

  @parameterized.named_parameters(
      {'testcase_name': 'NoSCOPES',
       'scopes': None, 'service': '', 'version': ''},
      {'testcase_name': 'NoSERVICE',
       'scopes': '', 'service': None, 'version': ''},
      {'testcase_name': 'NoVERSION',
       'scopes': '', 'service': '', 'version': None},
  )
  def test_from_config__attribute_error(self, scopes, service, version):
    """Test that initialization fails when class variables are not set."""
    google_api.GoogleAPI.SCOPES = scopes
    google_api.GoogleAPI.SERVICE = service
    google_api.GoogleAPI.VERSION = version
    with self.assertRaises(AttributeError):
      google_api.GoogleAPI.from_config(self.config)


if __name__ == '__main__':
  absltest.main()
