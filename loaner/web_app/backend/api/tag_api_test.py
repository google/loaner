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
import endpoints

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

    self.test_tag = tag_model.Tag.create(
        user_email=loanertest.USER_EMAIL, name='tag-one',
        hidden=False, protect=False, color='amber')

  def tearDown(self):
    super(TagApiTest, self).tearDown()
    self.service = None

  def test_create(self):
    request = tag_messages.CreateTagRequest(tag=tag_messages.Tag(
        name='restricted_location', hidden=False, color='red',
        description='leadership circle'))
    with mock.patch.object(
        self.service, 'check_xsrf_token', autospec=True) as mock_xsrf_token:
      response = self.service.create(request)
      self.assertEqual(mock_xsrf_token.call_count, 1)
      self.assertIsInstance(response, message_types.VoidMessage)

  def test_create_defaults(self):
    request = tag_messages.CreateTagRequest(tag=tag_messages.Tag(
        name='restricted_location', color='blue'))
    with mock.patch.object(
        self.service, 'check_xsrf_token', autospec=True) as mock_xsrf_token:
      response = self.service.create(request)
      self.assertEqual(mock_xsrf_token.call_count, 1)
      self.assertIsInstance(response, message_types.VoidMessage)

  def test_create_bad_request(self):
    """Test create raises BadRequestException with required fields missing."""
    request = tag_messages.CreateTagRequest(
        tag=tag_messages.Tag(name='no_color_tag'))
    with self.assertRaises(endpoints.BadRequestException):
      self.service.create(request)

  def test_create_prexisting_tag(self):
    request = tag_messages.CreateTagRequest(tag=tag_messages.Tag(
        name=self.test_tag.name, hidden=False, color='blue'))
    with self.assertRaises(endpoints.BadRequestException):
      self.service.create(request)

  def test_destroy_tag(self):
    request = tag_messages.TagRequest(
        urlsafe_key=self.test_tag.key.urlsafe())
    with mock.patch.object(
        self.service, 'check_xsrf_token', autospec=True) as mock_xsrf_token:
      response = self.service.destroy(request)
      self.assertEqual(mock_xsrf_token.call_count, 1)
      self.assertIsNone(
          tag_model.Tag.get(self.test_tag.key.urlsafe()))
      self.assertIsInstance(response, message_types.VoidMessage)

  def test_destroy_not_existing(self):
    request = tag_messages.TagRequest(urlsafe_key='nonexistent_tag')
    with self.assertRaises(endpoints.BadRequestException):
      self.service.destroy(request)

  def test_get_tag(self):
    request = tag_messages.TagRequest(urlsafe_key=self.test_tag.key.urlsafe())
    expected_response = tag_messages.Tag(
        name=self.test_tag.name,
        hidden=self.test_tag.hidden,
        color=self.test_tag.color,
        protect=self.test_tag.protect,
        description=self.test_tag.description)
    with mock.patch.object(
        self.service, 'check_xsrf_token', autospec=True) as mock_xsrf_token:
      response = self.service.get(request)
      self.assertEqual(mock_xsrf_token.call_count, 1)
      self.assertEqual(response, expected_response)

  def test_get_tag_bad_request(self):
    request = tag_messages.TagRequest(urlsafe_key='fake_urlsafe_key')
    with self.assertRaises(endpoints.BadRequestException):
      self.service.get(request)


if __name__ == '__main__':
  loanertest.main()
