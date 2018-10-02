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

"""Tests for deployments.lib.app_engine."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

# Prefer Python 3 and fall back on Python 2.
# pylint:disable=g-statement-before-imports,g-import-not-at-top
try:
  from http import HTTPStatus as http_status
except ImportError:
  import httplib as http_status
# pylint:enable=g-statement-before-imports,g-import-not-at-top

from googleapiclient import errors

import httplib2
import mock

from absl.testing import absltest
from loaner.deployments.lib import app_engine
from loaner.deployments.lib import common


_FAKE_APPLICATION_OBJECT = {
    'id': 'PROJECT_ID',
    'locationId': 'us-east1',
    'authDomain': 'example.com',
    'codeBucket': 'staging.PROJECT_ID.appspot.com',
    'servingStatus': 'SERVING',
    'defaultHostname': 'PROJECT_ID.appspot.com',
    'defaultBucket': 'PROJECT_ID.appspot.com',
    'gcrDomain': 'us.gcr.io',
}


class AppEngineTest(absltest.TestCase):

  def setUp(self):
    super(AppEngineTest, self).setUp()
    self.config = common.ProjectConfig(
        'TEST_KEY', 'TEST_PROJECT', 'TEST_CLIENT_ID', 'TEST_CLIENT_SECRET',
        'TEST_BUCKET', '/test/path.yaml')

  def test_admin_api_create(self):
    """Test the create API method for the App Engine Admin API."""
    mock_client = mock.Mock()
    mock_create = mock_client.apps.return_value.create
    mock_create.return_value.execute.return_value = _FAKE_APPLICATION_OBJECT

    test_app_engine_admin_api = app_engine.AdminAPI(self.config, mock_client)
    self.assertEqual(
        _FAKE_APPLICATION_OBJECT, test_app_engine_admin_api.create('us-east1'))

  def test_admin_api_create__not_found_error(self):
    """Test the App Engine project creation for an invalid location."""
    test_app_engine_admin_api = app_engine.AdminAPI(self.config, mock.Mock())
    with self.assertRaises(app_engine.NotFoundError):
      test_app_engine_admin_api.create('INVALID_LOCATION')

  def test_admin_api_create__creation_error(self):
    """Test the App Engine project creation for an invalid project."""
    test_app_engine_admin_api = app_engine.AdminAPI(self.config, mock.Mock())
    test_app_engine_admin_api._client.apps.side_effect = errors.HttpError(
        httplib2.Response({
            'reason': 'Not found.', 'status': http_status.NOT_FOUND}),
        'Project not found.'.encode(encoding='UTF-8'))
    with self.assertRaises(app_engine.CreationError):
      test_app_engine_admin_api.create('us-east1')

  def test_admin_api_get(self):
    """Test the get API method for the App Engine Admin API."""
    mock_client = mock.Mock()
    mock_get = mock_client.apps.return_value.get
    mock_get.return_value.execute.return_value = _FAKE_APPLICATION_OBJECT

    test_app_engine_admin_api = app_engine.AdminAPI(self.config, mock_client)
    self.assertEqual(_FAKE_APPLICATION_OBJECT, test_app_engine_admin_api.get())

  def test_admin_api_get__not_found_error(self):
    """Test the get API method for an invalid project."""
    test_app_engine_admin_api = app_engine.AdminAPI(self.config, mock.Mock())
    test_app_engine_admin_api._client.apps.side_effect = errors.HttpError(
        httplib2.Response({
            'reason': 'Not found.', 'status': http_status.NOT_FOUND}),
        'App not found.'.encode(encoding='UTF-8'))
    with self.assertRaises(app_engine.NotFoundError):
      test_app_engine_admin_api.get()


if __name__ == '__main__':
  absltest.main()
