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

"""Tests for deployments.lib.datastore."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import mock

from google.cloud import datastore as datastore_client
from google.cloud.datastore import entity
from google.cloud.datastore import key

from loaner.deployments.lib import auth
from loaner.deployments.lib import common
from loaner.deployments.lib import datastore
from absl.testing import absltest


class DatastoreAPITest(absltest.TestCase):

  def setUp(self):
    super(DatastoreAPITest, self).setUp()
    self.config = common.ProjectConfig(
        'TEST_KEY', 'TEST_PROJECT', 'TEST_CLIENT_ID', 'TEST_CLIENT_SECRET',
        'TEST_BUCKET', '/test/path.yaml')

  def test_create_datastore_api(self):
    """Test the initialization of the Cloud Datastore API helper class."""
    test_datastore_api = datastore.DatastoreAPI(self.config, mock.Mock())
    self.assertEqual(self.config, test_datastore_api._config)
    self.assertEqual(
        'DatastoreAPI for project: TEST_PROJECT.', str(test_datastore_api))

  @mock.patch.object(datastore_client, 'Client', autospec=True)
  @mock.patch.object(auth, 'CloudCredentials', autospec=True)
  def test_create_datstore_api_from_config(self, mock_creds, mock_client):
    """Test initialization using the classmethod from_config."""
    test_from_config = datastore.DatastoreAPI.from_config(self.config)
    self.assertEqual(self.config, test_from_config._config)
    self.assertEqual(
        'DatastoreAPI for project: TEST_PROJECT.', str(test_from_config))
    self.assertTrue(mock_creds.called)
    self.assertTrue(mock_client.called)

  def test_datastore_api_get_version(self):
    """Test the get_version API method for the Datastore API."""
    test_response = entity.Entity(
        key=key.Key('Config', 'datastore_version', project='TEST_PROJECT'))
    test_response['integer_value'] = 1
    mock_client = mock.Mock()
    mock_client.get.return_value = test_response

    test_datastore_api = datastore.DatastoreAPI(self.config, mock_client)
    self.assertEqual(1, test_datastore_api.get_version())

  def test_datastore_api_get_version__not_found_error(self):
    """Test the get_version API method with an invalid response."""
    mock_client = mock.Mock()
    mock_client.get.return_value = {}

    test_datastore_api = datastore.DatastoreAPI(self.config, mock_client)
    with self.assertRaises(datastore.NotFoundError):
      test_datastore_api.get_version()


if __name__ == '__main__':
  absltest.main()
