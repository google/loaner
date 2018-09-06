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

"""Tests for backend.api.tag_api."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import mock

from protorpc import message_types

from loaner.web_app.backend.api import root_api
from loaner.web_app.backend.api import tag_api
from loaner.web_app.backend.api.messages import tag_messages
from loaner.web_app.backend.models import tag_model
from loaner.web_app.backend.testing import loanertest


class TagApiTest(loanertest.EndpointsTestCase):
  """Tests for the Tag API."""

  def setUp(self):
    super(TagApiTest, self).setUp()
    self.service = tag_api.TagApi()
    self.login_admin_endpoints_user()

  def tearDown(self):
    super(TagApiTest, self).tearDown()
    self.service = None

  @mock.patch.object(root_api.Service, 'check_xsrf_token', autospec=True)
  def test_create(self, mock_xsrf_token):
    request = tag_messages.CreateTagRequest(tag=tag_messages.Tag(
        name='restricted_location', visible=True, color='red',
        description='leadership circle'))
    response = self.service.create(request)
    self.assertEqual(mock_xsrf_token.call_count, 1)
    self.assertIsInstance(response, message_types.VoidMessage)

  @mock.patch.object(root_api.Service, 'check_xsrf_token', autospec=True)
  def test_create_defaults(self, mock_xsrf_token):
    request = tag_messages.CreateTagRequest(tag=tag_messages.Tag(
        name='restricted_location', color='blue'))
    response = self.service.create(request)
    self.assertEqual(mock_xsrf_token.call_count, 1)
    self.assertIsInstance(response, message_types.VoidMessage)

  def test_create_bad_request(self):
    request = tag_messages.CreateTagRequest(
        tag=tag_messages.Tag(name='no_color_tag'))
    with self.assertRaises(tag_api.endpoints.BadRequestException):
      self.service.create(request)

  def test_create_prexisting_tag(self):
    tag_model.Tag.create(
        user_email=loanertest.USER_EMAIL, name='needs_cleaning', visible=True,
        protect=False, color='green')
    request = tag_messages.CreateTagRequest(tag=tag_messages.Tag(
        name='needs_cleaning', visible=True, color='blue'))
    with self.assertRaises(tag_api.endpoints.BadRequestException):
      self.service.create(request)


if __name__ == '__main__':
  loanertest.main()
