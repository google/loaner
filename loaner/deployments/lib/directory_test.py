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

"""Tests for deployments.lib.directory."""

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

from absl.testing import parameterized

from googleapiclient import errors

import httplib2
import mock

from loaner.deployments.lib import common
from loaner.deployments.lib import directory
from absl.testing import absltest

_FAKE_ROLE_OBJECT = {
    'kind': 'admin#directory#role',
    'etag': 'E_TAG',
    'roleId': 'ROLE_ID',
    'roleName': 'ROLE_NAME',
    'rolePrivileges': [{
        'privilegeName': 'PRIVILEGE_NAME_0', 'serviceId': 'SERVICE_ID_0',
    }],
}

_FAKE_USER_OBJECT = {
    'kind': 'admin#directory#user',
    'id': 'unique_id',
    'etag': 'E_TAG',
    'primaryEmail': 'grab-n-go-role@example.com',
    'name': {
        'givenName': 'Grab n Go',
        'familyName': 'Role Account',
    },
    'isAdmin': False,
    'isDelegatedAdmin': False,
    'creationTime': '2018-01-01T00:00:00.000Z',
    'changePasswordAtNextLogin': False,
    'customerId': 'my_customer',
    'orgUnitPath': '/',
    'isMailboxSetup': False,
}


class DirectoryAPITest(parameterized.TestCase, absltest.TestCase):

  def setUp(self):
    super(DirectoryAPITest, self).setUp()
    self.config = common.ProjectConfig(
        'TEST_KEY', 'TEST_PROJECT', 'TEST_CLIENT_ID', 'TEST_CLIENT_SECRET',
        'TEST_BUCKET', '/test/path.yaml')

  def test_directory_api_insert_role(self):
    """Test the insert_role API method for the Google Admin Directory API."""
    mock_client = mock.Mock()
    mock_insert = mock_client.roles.return_value.insert
    mock_insert.return_value.execute.return_value = _FAKE_ROLE_OBJECT

    test_directory_api = directory.DirectoryAPI(self.config, mock_client)
    self.assertEqual(_FAKE_ROLE_OBJECT, test_directory_api.insert_role())

  @parameterized.parameters(
      (http_status.CONFLICT, directory.AlreadyExistsError),
      (http_status.INTERNAL_SERVER_ERROR, directory.AlreadyExistsError),
      (http_status.FORBIDDEN, directory.ForbiddenError),
      (http_status.NOT_FOUND, directory.InsertionError),
  )
  def test_directory_api_insert_role__errors(
      self, error_code, expected_error):
    """Test the insert_role API method for the Google Admin Directory API."""
    test_directory_api = directory.DirectoryAPI(self.config, mock.Mock())
    test_directory_api._client.roles.side_effect = errors.HttpError(
        httplib2.Response({
            'reason': 'NOT USED', 'status': error_code}),
        'NOT USED.'.encode(encoding='UTF-8'))
    with self.assertRaises(expected_error):
      test_directory_api.insert_role()

  def test_directory_api_insert_user(self):
    """Test the insert_user API method for the Google Admin Directory API."""
    mock_client = mock.Mock()
    mock_insert = mock_client.users.return_value.insert
    mock_insert.return_value.execute.return_value = _FAKE_USER_OBJECT

    test_directory_api = directory.DirectoryAPI(self.config, mock_client)
    self.assertEqual(
        _FAKE_USER_OBJECT, test_directory_api.insert_user('UNUSED_PASSWORD'))

  @parameterized.parameters(
      (http_status.CONFLICT, directory.AlreadyExistsError),
      (http_status.INTERNAL_SERVER_ERROR, directory.AlreadyExistsError),
      (http_status.FORBIDDEN, directory.ForbiddenError),
      (http_status.NOT_FOUND, directory.InsertionError),
  )
  def test_directory_api_insert_user__errors(
      self, error_code, expected_error):
    """Test the insert_user API method for the Google Admin Directory API."""
    test_directory_api = directory.DirectoryAPI(self.config, mock.Mock())
    test_directory_api._client.users.side_effect = errors.HttpError(
        httplib2.Response({
            'reason': 'NOT USED', 'status': error_code}),
        'NOT USED.'.encode(encoding='UTF-8'))
    with self.assertRaises(expected_error):
      test_directory_api.insert_user('UNUSED_PASSWORD')


if __name__ == '__main__':
  absltest.main()
