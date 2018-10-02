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

from absl.testing import parameterized

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


class CloudStorageAPITest(parameterized.TestCase, absltest.TestCase):

  def setUp(self):
    super(CloudStorageAPITest, self).setUp()
    self.config = common.ProjectConfig(
        'TEST_KEY', 'TEST_PROJECT', 'TEST_CLIENT_ID', 'TEST_CLIENT_SECRET',
        'TEST_BUCKET', '/test/path.yaml')

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

  @parameterized.named_parameters(
      ('Default Bucket', None, 'TEST_BUCKET'),
      ('Custom Bucket', 'OTHER_BUCKET', 'OTHER_BUCKET'),
  )
  def test_cloud_storage_get_bucket(self, test_bucket, expected_bucket):
    """Test the get_bucket API method for the Google Cloud Storage API."""
    mock_client = mock.Mock()
    mock_client.get_bucket.return_value = _FAKE_BUCKET_OBJECT

    test_cloud_storage_api = storage.CloudStorageAPI(self.config, mock_client)
    self.assertEqual(
        _FAKE_BUCKET_OBJECT, test_cloud_storage_api.get_bucket(test_bucket))
    mock_client.get_bucket.assert_called_once_with(expected_bucket)

  def test_cloud_storage_get_bucket__not_found_error(self):
    """Test the get_bucket API method for an invalid project."""
    test_cloud_storage_api = storage.CloudStorageAPI(self.config, mock.Mock())
    test_cloud_storage_api._client.get_bucket.side_effect = exceptions.NotFound(
        'The bucket requested was not found.'
    )
    with self.assertRaises(storage.NotFoundError):
      test_cloud_storage_api.get_bucket()

  @parameterized.named_parameters(
      ('Default Bucket', None, 'TEST_BUCKET'),
      ('Custom Bucket', 'OTHER_BUCKET', 'OTHER_BUCKET'),
  )
  def test_cloud_storage_insert_bucket(self, test_bucket, expected_bucket):
    """Test the insert_bucket method for the Cloud Storage API."""
    mock_client = mock.Mock()
    mock_client.create_bucket.return_value = _FAKE_BUCKET_OBJECT

    test_cloud_storage_api = storage.CloudStorageAPI(self.config, mock_client)
    self.assertEqual(
        _FAKE_BUCKET_OBJECT, test_cloud_storage_api.insert_bucket(test_bucket))
    mock_client.create_bucket.assert_called_once_with(expected_bucket)

  def test_cloud_storage_api_insert_bucket__already_exists_error(self):
    """Test the Cloud Storage Bucket creation for an existing bucket."""
    test_cloud_storage_api = storage.CloudStorageAPI(self.config, mock.Mock())
    test_cloud_storage_api._client.create_bucket.side_effect = (
        exceptions.Conflict('This bucket already exists.'))
    with self.assertRaises(storage.AlreadyExistsError):
      test_cloud_storage_api.insert_bucket()

  @parameterized.parameters(
      (None, 'TEST_BUCKET'), ('OTHER_BUCKET', 'OTHER_BUCKET'))
  @mock.patch.object(storage_client, 'Blob', autospec=True)
  def test_cloud_storage_insert_blob(
      self, test_bucket, expected_bucket, mock_blob_class):
    """Test the creation of a Blob on Google Cloud Storage."""
    mock_blob = mock_blob_class.return_value
    mock_client = mock.Mock()
    test_cloud_storage_api = storage.CloudStorageAPI(self.config, mock_client)

    with mock.patch.object(
        test_cloud_storage_api, 'get_bucket',
        return_value=_FAKE_BUCKET_OBJECT) as mock_get_bucket:

      test_cloud_storage_api.insert_blob(
          'TEST_PATH', {'key': 'value'}, test_bucket)

      mock_get_bucket.assert_called_once_with(expected_bucket)
      mock_blob.upload_from_string.assert_called_once_with(
          data='{"key": "value"}',
          content_type='application/json',
          client=mock_client,
      )

  @parameterized.named_parameters(
      ('Default Bucket', None, 'TEST_BUCKET'),
      ('Custom Bucket', 'OTHER_BUCKET', 'OTHER_BUCKET'),
  )
  def test_cloud_storage_get_blob(self, test_bucket, expected_bucket):
    """Test the retrieval of a Blob from Google Cloud Storage."""
    with mock.patch.object(
        storage_client, 'Blob', autospec=True) as mock_blob_class:
      mock_blob = mock_blob_class.return_value
      mock_blob.download_as_string.return_value = '{"key": "value"}'

      mock_client = mock.Mock()
      mock_bucket = mock_client.get_bucket.return_value
      mock_bucket.get_blob.return_value = mock_blob

      test_cloud_storage_api = storage.CloudStorageAPI(self.config, mock_client)

      self.assertEqual(
          {'key': 'value'},
          test_cloud_storage_api.get_blob('TEST_BLOB', test_bucket))

      mock_client.get_bucket.assert_called_once_with(expected_bucket)
      mock_bucket.get_blob.assert_called_once_with('TEST_BLOB', mock_client)
      mock_blob.download_as_string.assert_called_once_with(mock_client)

  @parameterized.parameters(AttributeError('FAIL'), exceptions.NotFound('FAIL'))
  @mock.patch.object(storage_client, 'Blob', autospec=True)
  def test_cloud_storage_get_blob__not_found_error(
      self, test_error, mock_blob_class):
    """Test the retrieval of a Blob that cannot be found."""
    mock_blob = mock_blob_class.return_value
    mock_blob.download_as_string.side_effect = test_error

    mock_client = mock.Mock()
    mock_client.get_bucket.return_value.get_blob.return_value = mock_blob

    test_cloud_storage_api = storage.CloudStorageAPI(self.config, mock_client)

    with self.assertRaises(storage.NotFoundError):
      test_cloud_storage_api.get_blob('TEST_BLOB')


if __name__ == '__main__':
  absltest.main()
