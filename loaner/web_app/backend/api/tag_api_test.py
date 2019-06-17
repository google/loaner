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

    self.default_tag = tag_model.Tag.create(
        user_email=loanertest.USER_EMAIL, name='tag-visible-unprotected',
        hidden=False, protect=False, color='blue')
    self.default_tag_response = tag_messages.Tag(
        name=self.default_tag.name,
        hidden=self.default_tag.hidden,
        protect=self.default_tag.protect,
        color=self.default_tag.color,
        description=self.default_tag.description,
        urlsafe_key=self.default_tag.key.urlsafe())

    self.hidden_tag = tag_model.Tag.create(
        user_email=loanertest.USER_EMAIL, name='tag-hidden',
        hidden=True, protect=False, color='red', description='test-description')
    self.hidden_tag_response = tag_messages.Tag(
        name=self.hidden_tag.name,
        hidden=self.hidden_tag.hidden,
        protect=self.hidden_tag.protect,
        color=self.hidden_tag.color,
        description=self.hidden_tag.description,
        urlsafe_key=self.hidden_tag.key.urlsafe())

    self.protected_tag = tag_model.Tag.create(
        user_email=loanertest.USER_EMAIL, name='tag-protected',
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
        name='restricted_location', hidden=False, protect=False, color='red',
        description='leadership circle'))
    with mock.patch.object(
        self.service, 'check_xsrf_token', autospec=True) as mock_xsrf_token:
      response = self.service.create(request)
      self.assertEqual(mock_xsrf_token.call_count, 1)
      self.assertIsInstance(response, message_types.VoidMessage)

  def test_create_defaults(self):
    request = tag_messages.CreateTagRequest(tag=tag_messages.Tag(
        name='restricted_location', color='blue', protect=False))
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

  def test_list_tags_include_hidden(self):
    with mock.patch.object(
        self.service, 'check_xsrf_token', autospec=True) as mock_xsrf_token:
      response = self.service.list(tag_messages.ListTagRequest(
          page_size=tag_model.Tag.query().count(), include_hidden_tags=True))
      self.assertEqual(mock_xsrf_token.call_count, 1)
      self.assertListEqual(response.tags, [
          self.test_tag_response, self.default_tag_response,
          self.hidden_tag_response, self.protected_tag_response
      ])
      self.assertIsNotNone(response.cursor)
      self.assertFalse(response.has_additional_results)
      self.assertEqual(response.total_pages, 1)

  def test_list_tags_exclude_hidden(self):
    with mock.patch.object(
        self.service, 'check_xsrf_token', autospec=True) as mock_xsrf_token:
      response = self.service.list(tag_messages.ListTagRequest(
          page_size=tag_model.Tag.query().count(), include_hidden_tags=False))
      self.assertEqual(mock_xsrf_token.call_count, 1)
      self.assertNotIn(self.hidden_tag_response, response.tags)
      self.assertIsNotNone(response.cursor)
      self.assertEqual(response.total_pages, 1)

  def test_list_tags_additional_results(self):
    first_response = self.service.list(tag_messages.ListTagRequest(page_size=1))
    self.assertListEqual(first_response.tags, [self.test_tag_response])
    self.assertTrue(first_response.has_additional_results)
    self.assertIsNotNone(first_response.cursor)
    self.assertEqual(first_response.total_pages, 3)

    second_response = self.service.list(tag_messages.ListTagRequest(
        page_size=1, cursor=first_response.cursor))
    self.assertListEqual(second_response.tags, [
        self.default_tag_response])
    self.assertTrue(second_response.has_additional_results)
    self.assertIsNotNone(second_response.cursor)
    self.assertEqual(second_response.total_pages, 3)

    third_response = self.service.list(tag_messages.ListTagRequest(
        page_size=1, cursor=second_response.cursor))
    self.assertListEqual(third_response.tags, [self.protected_tag_response])
    self.assertFalse(third_response.has_additional_results)
    self.assertIsNotNone(third_response.cursor)
    self.assertEqual(third_response.total_pages, 3)

  def test_list_tags_first_page_index(self):
    response = self.service.list(tag_messages.ListTagRequest(
        page_size=1, page_index=1))
    self.assertListEqual(response.tags, [self.test_tag_response])
    self.assertTrue(response.has_additional_results)
    self.assertIsNotNone(response.cursor)
    self.assertEqual(response.total_pages, 3)

  def test_list_tags_last_page_index(self):
    response = self.service.list(tag_messages.ListTagRequest(
        page_size=1, page_index=3))
    self.assertListEqual(response.tags, [self.protected_tag_response])
    self.assertFalse(response.has_additional_results)
    self.assertIsNotNone(response.cursor)
    self.assertEqual(response.total_pages, 3)

  def test_list_tags_page_size_bad_request(self):
    with self.assertRaises(endpoints.BadRequestException):
      self.service.list(tag_messages.ListTagRequest(page_size=0))

  def test_list_tags_none(self):
    self.test_tag.key.delete()
    self.default_tag.key.delete()
    self.hidden_tag.key.delete()
    self.protected_tag.key.delete()

    response = self.service.list(tag_messages.ListTagRequest())
    self.assertEmpty(response.tags)
    self.assertFalse(response.has_additional_results)
    self.assertIsNone(response.cursor)
    self.assertEqual(response.total_pages, 0)

  def test_list_tags_no_cursor(self):
    with mock.patch.object(
        api_utils, 'get_datastore_cursor',
        autospec=True) as mock_get_datastore_cursor:
      self.service.list(tag_messages.ListTagRequest())
      self.assertFalse(mock_get_datastore_cursor.called)

  def test_list_tags_cursor_bad_request(self):
    with self.assertRaises(datastore_errors.BadValueError):
      self.service.list(tag_messages.ListTagRequest(cursor='bad_cursor_value'))

  def test_update(self):
    new_color = 'blue'
    new_description = 'An updated description.'
    request = tag_messages.UpdateTagRequest(
        tag=tag_messages.Tag(
            urlsafe_key=self.test_tag.key.urlsafe(),
            name=self.test_tag.name,
            hidden=self.test_tag.hidden,
            protect=self.test_tag.protect,
            color=new_color,
            description=new_description))
    with mock.patch.object(
        self.service, 'check_xsrf_token', autospec=True) as mock_xsrf_token:
      response = self.service.update(request)
      self.assertEqual(mock_xsrf_token.call_count, 1)
    self.assertIsInstance(response, message_types.VoidMessage)
    # Ensure that the new tag was updated.
    tag = tag_model.Tag.get(self.test_tag.name)
    self.assertEqual(tag.name, self.test_tag.name)
    self.assertEqual(tag.hidden, self.test_tag.hidden)
    self.assertEqual(tag.protect, self.test_tag.protect)
    self.assertEqual(tag.color, new_color)
    self.assertEqual(tag.description, new_description)

  def test_update_rename(self):
    """Tests updating a tag with a rename."""
    new_name = 'A new tag name.'
    request = tag_messages.UpdateTagRequest(
        tag=tag_messages.Tag(
            urlsafe_key=self.test_tag.key.urlsafe(),
            name=new_name,
            hidden=self.test_tag.hidden,
            protect=self.test_tag.protect,
            color=self.test_tag.color,
            description=self.test_tag.description))
    response = self.service.update(request)
    self.assertIsInstance(response, message_types.VoidMessage)
    tag = tag_model.Tag.get(self.test_tag.name)
    self.assertEqual(tag.name, new_name)
    self.assertEqual(tag.hidden, self.test_tag.hidden)
    self.assertEqual(tag.protect, self.test_tag.protect)
    self.assertEqual(tag.color, self.test_tag.color)
    self.assertEqual(tag.description, self.test_tag.description)

  def test_update_nonexistent(self):
    """Tests updating a nonexistent tag."""
    request = tag_messages.UpdateTagRequest(
        tag=tag_messages.Tag(
            urlsafe_key='nonexistent_urlsafe_key',
            name='nonexistent tag',
            hidden=False,
            protect=False,
            color='blue',
            description=None))
    with mock.patch.object(
        self.service, 'check_xsrf_token', autospec=True):
      with self.assertRaises(tag_api.endpoints.BadRequestException):
        self.service.update(request)

  def test_update_protected(self):
    """Tests updating a nonexistent tag."""
    request = tag_messages.UpdateTagRequest(
        tag=tag_messages.Tag(
            urlsafe_key=self.protected_tag.key.urlsafe(),
            name=self.protected_tag.name,
            hidden=self.protected_tag.hidden,
            protect=self.protected_tag.protect,
            color=self.protected_tag.color,
            description='A new description for a protected tag.'))
    with self.assertRaises(tag_api.endpoints.BadRequestException):
      self.service.update(request)

  def test_update_bad_request(self):
    """Tests update raises BadRequestException with required fields missing."""
    request = tag_messages.UpdateTagRequest(
        tag=tag_messages.Tag(
            urlsafe_key=self.test_tag.key.urlsafe(),
            name='tag name'))
    with self.assertRaises(endpoints.BadRequestException):
      self.service.update(request)


if __name__ == '__main__':
  loanertest.main()
