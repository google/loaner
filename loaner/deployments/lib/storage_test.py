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

"""Tests for deployments.lib.storage."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import mock

from google.cloud import exceptions
from google.cloud import storage as storage_client

from loaner.deployments.lib import auth
from loaner.deployments.lib import common
from loaner.deployments.lib import storage
from absl.testing import absltest

_FAKE_BUCKET_OBJECT = {
    'kind': 'storage#bucket',
    'id': 'TEST_BUCKET',
    'selfLink': 'http://url-to-the-bucket',
    'projectNumber': '1234567890',
    'name': 'TEST_BUCKET',
    'timeCreated': '2018-01-01T00:00:00.000Z',
    'updated': '2018-01-01T00:00:00.000Z',
    'metageneration': '1',
    'location': 'US',
    'storageClass': 'STANDARD',
    'etag': 'CAE=',
}


class CloudStorageAPITest(absltest.TestCase):

  def setUp(self):
    super(CloudStorageAPITest, self).setUp()
    self.config = common.ProjectConfig(
        'TEST_PROJECT', 'TEST_CLIENT_ID', 'TEST_CLIENT_SECRET', 'TEST_BUCKET')

  def test_create_storage_api(self):
    """Test the initialization of the Cloud Storage API helper class."""
    test_storage_api = storage.CloudStorageAPI(self.config, mock.Mock())
    self.assertEqual(self.config, test_storage_api._config)
    self.assertEqual(
        'CloudStorageAPI for project: TEST_PROJECT.', str(test_storage_api))

  @mock.patch.object(storage_client, 'Client', autospec=True)
  @mock.patch.object(auth, 'CloudCredentials', autospec=True)
  def test_create_storage_api_from_config(self, mock_creds, mock_client):
    """Test initialization using the classmethod from_config."""
    test_from_config = storage.CloudStorageAPI.from_config(self.config)
    self.assertEqual(self.config, test_from_config._config)
    self.assertEqual(
        'CloudStorageAPI for project: TEST_PROJECT.', str(test_from_config))
    self.assertTrue(mock_creds.called)
    self.assertTrue(mock_client.called)

  def test_cloud_storage_get_bucket(self):
    """Test the get_bucket API method for the Google Cloud Storage API."""
    mock_client = mock.Mock()
    mock_client.get_bucket.return_value = _FAKE_BUCKET_OBJECT

    test_cloud_storage_api = storage.CloudStorageAPI(self.config, mock_client)
    self.assertEqual(_FAKE_BUCKET_OBJECT, test_cloud_storage_api.get_bucket())
    mock_client.get_bucket.assert_called_once_with(self.config.bucket)

  def test_cloud_storage_get_bucket__custom_name(self):
    """Test the get_bucket API method for the Google Cloud Storage API."""
    mock_client = mock.Mock()
    mock_client.get_bucket.return_value = _FAKE_BUCKET_OBJECT

    test_cloud_storage_api = storage.CloudStorageAPI(self.config, mock_client)
    self.assertEqual(
        _FAKE_BUCKET_OBJECT,
        test_cloud_storage_api.get_bucket('BUCKET_NAME'),
    )
    mock_client.get_bucket.assert_called_once_with('BUCKET_NAME')

  def test_cloud_storage_get_bucket__not_found_error(self):
    """Test the get_bucket API method for an invalid project."""
    test_cloud_storage_api = storage.CloudStorageAPI(self.config, mock.Mock())
    test_cloud_storage_api._client.get_bucket.side_effect = exceptions.NotFound(
        'The bucket requested was not found.'
    )
    with self.assertRaises(storage.NotFoundError):
      test_cloud_storage_api.get_bucket()

  def test_cloud_storage_insert_bucket(self):
    """Test the insert_bucket method for the Cloud Storage API."""
    mock_client = mock.Mock()
    mock_client.create_bucket.return_value = _FAKE_BUCKET_OBJECT

    test_cloud_storage_api = storage.CloudStorageAPI(self.config, mock_client)
    self.assertEqual(
        _FAKE_BUCKET_OBJECT, test_cloud_storage_api.insert_bucket())
    mock_client.create_bucket.assert_called_once_with(self.config.bucket)

  def test_cloud_storage_insert_bucket__custom_name(self):
    """Test the insert_bucket method for the Cloud Storage API."""
    mock_client = mock.Mock()
    mock_client.create_bucket.return_value = _FAKE_BUCKET_OBJECT

    test_cloud_storage_api = storage.CloudStorageAPI(self.config, mock_client)
    self.assertEqual(
        _FAKE_BUCKET_OBJECT,
        test_cloud_storage_api.insert_bucket('BUCKET_NAME'),
    )
    mock_client.create_bucket.assert_called_once_with('BUCKET_NAME')

  def test_cloud_storage_api_insert_bucket__already_exists_error(self):
    """Test the Cloud Storage Bucket creation for an existing bucket."""
    test_cloud_storage_api = storage.CloudStorageAPI(self.config, mock.Mock())
    test_cloud_storage_api._client.create_bucket.side_effect = (
        exceptions.Conflict('This bucket already exists.'))
    with self.assertRaises(storage.AlreadyExistsError):
      test_cloud_storage_api.insert_bucket()


if __name__ == '__main__':
  absltest.main()
