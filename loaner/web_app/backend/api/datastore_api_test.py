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

"""Tests for backend.api.datastore_api."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import mock

import endpoints

from loaner.web_app.backend.api import datastore_api
from loaner.web_app.backend.api.messages import datastore_messages
from loaner.web_app.backend.models import user_model
from loaner.web_app.backend.testing import loanertest


class DatastoreEndpointsTest(loanertest.EndpointsTestCase):
  """Test the Datastore Endpoints API."""

  def setUp(self):
    super(DatastoreEndpointsTest, self).setUp()
    self.service = datastore_api.DatastoreApi()

  def tearDown(self):
    super(DatastoreEndpointsTest, self).tearDown()
    self.service = None

  @mock.patch('__main__.datastore_api.datastore_yaml.import_yaml')
  @mock.patch('__main__.datastore_api.root_api.Service.check_xsrf_token')
  def test_import(self, mock_xsrf_token, mock_importyaml):
    self.login_admin_endpoints_user()
    request = datastore_messages.ImportYamlRequest(yaml='fake_yaml')

    self.service.datastore_import(request)
    self.assertEqual(mock_xsrf_token.call_count, 1)
    mock_importyaml.assert_called_once_with('fake_yaml', wipe=False)
    user_model.User.get_user(loanertest.USER_EMAIL).key.delete()

  @mock.patch('__main__.datastore_api.datastore_yaml.import_yaml')
  @mock.patch('__main__.datastore_api.root_api.Service.check_xsrf_token')
  def test_import_not_admin(self, mock_xsrf_token, mock_importyaml):
    self.login_endpoints_user()
    request = datastore_messages.ImportYamlRequest(yaml='fake_yaml')

    self.assertRaises(
        endpoints.ForbiddenException, self.service.datastore_import, request)
    self.assertFalse(mock_xsrf_token.called)


if __name__ == '__main__':
  loanertest.main()
