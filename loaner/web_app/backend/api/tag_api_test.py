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
from google.appengine.api import datastore_errors

import endpoints

from loaner.web_app.backend.api import tag_api
from loaner.web_app.backend.api.messages import tag_messages
from loaner.web_app.backend.lib import api_utils
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
    self.test_tag_response = tag_messages.Tag(
        name=self.test_tag.name,
        hidden=self.test_tag.hidden,
        protect=self.test_tag.protect,
        color=self.test_tag.color,
        description=self.test_tag.description,
        urlsafe_key=self.test_tag.key.urlsafe())

    self.hidden_tag = tag_model.Tag.create(
        user_email=loanertest.USER_EMAIL, name='tag-two',
        hidden=True, protect=False, color='red', description='test-description')
    self.hidden_tag_response = tag_messages.Tag(
        name=self.hidden_tag.name,
        hidden=self.hidden_tag.hidden,
        protect=self.hidden_tag.protect,
        color=self.hidden_tag.color,
        description=self.hidden_tag.description,
        urlsafe_key=self.hidden_tag.key.urlsafe())

    self.protected_tag = tag_model.Tag.create(
        user_email=loanertest.USER_EMAIL, name='tag-three',
        hidden=False, protect=True, color='amber')
    self.protected_tag_response = tag_messages.Tag(
        name=self.protected_tag.name,
        hidden=self.protected_tag.hidden,
        protect=self.protected_tag.protect,
        color=self.protected_tag.color,
        description=self.protected_tag.description,
        urlsafe_key=self.protected_tag.key.urlsafe())

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
        urlsafe_key=self.hidden_tag.key.urlsafe())
    with mock.patch.object(
        self.service, 'check_xsrf_token', autospec=True) as mock_xsrf_token:
      response = self.service.destroy(request)
      self.assertEqual(mock_xsrf_token.call_count, 1)
      self.assertIsNone(
          tag_model.Tag.get(self.hidden_tag.key.urlsafe()))
      self.assertIsInstance(response, message_types.VoidMessage)

  def test_destroy_not_existing(self):
    with self.assertRaises(endpoints.BadRequestException):
      self.service.destroy(
          tag_messages.TagRequest(urlsafe_key='nonexistent_tag'))

  def test_destroy_protected(self):
    with self.assertRaises(endpoints.BadRequestException):
      self.service.destroy(
          tag_messages.TagRequest(
              urlsafe_key=self.protected_tag.key.urlsafe()))

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

  def test_list_tags(self):
    with mock.patch.object(
        self.service, 'check_xsrf_token', autospec=True) as mock_xsrf_token:
      response = self.service.list(tag_messages.ListTagRequest(page_size=10000))
      self.assertEqual(mock_xsrf_token.call_count, 1)
      self.assertListEqual(
          response.tags,
          [self.test_tag_response,
           self.hidden_tag_response,
           self.protected_tag_response])

  def test_list_tags_additional_results(self):
    first_response = self.service.list(tag_messages.ListTagRequest(page_size=1))
    self.assertListEqual(first_response.tags, [self.test_tag_response])
    self.assertTrue(first_response.has_additional_results)

    second_response = self.service.list(tag_messages.ListTagRequest(
        page_size=1, cursor=first_response.cursor))
    self.assertEqual(second_response.tags, [self.hidden_tag_response])
    self.assertTrue(second_response.has_additional_results)

    third_response = self.service.list(tag_messages.ListTagRequest(
        page_size=10000, cursor=second_response.cursor))
    self.assertEqual(third_response.tags, [self.protected_tag_response])
    self.assertFalse(third_response.has_additional_results)

    self.assertIsNotNone(second_response.cursor)

  def test_list_tags_none(self):
    self.test_tag.key.delete()
    self.hidden_tag.key.delete()
    self.protected_tag.key.delete()

    response = self.service.list(tag_messages.ListTagRequest())
    self.assertEmpty(response.tags)
    self.assertFalse(response.has_additional_results)
    self.assertIsNone(response.cursor)

  def test_list_tags_no_cursor(self):
    with mock.patch.object(
        api_utils, 'get_datastore_cursor',
        autospec=True) as mock_get_datastore_cursor:
      self.service.list(tag_messages.ListTagRequest())
      self.assertFalse(mock_get_datastore_cursor.called)

  def test_list_tags_bad_request(self):
    with self.assertRaises(datastore_errors.BadValueError):
      self.service.list(tag_messages.ListTagRequest(cursor='bad_cursor_value'))


if __name__ == '__main__':
  loanertest.main()
