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

"""Tests for backend.api.template_api."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from absl.testing import parameterized
import mock

from protorpc import message_types

import endpoints

from loaner.web_app.backend.api import root_api  # pylint: disable=unused-import
from loaner.web_app.backend.api import template_api
from loaner.web_app.backend.api.messages import template_messages
from loaner.web_app.backend.models import template_model  # pylint: disable=unused-import
from loaner.web_app.backend.testing import loanertest


class TemplateApiTest(parameterized.TestCase, loanertest.EndpointsTestCase):
  """Test for the Template API."""

  def setUp(self):
    super(TemplateApiTest, self).setUp()
    self.service = template_api.TemplateApi()
    self.login_admin_endpoints_user()
    self.template_1 = template_model.Template(
        id='this_template', body='template body 1', title='title')
    self.template_2 = template_model.Template(
        id='second_template', body='template body 2',
        title='title 2')
    self.template_1.put()
    self.template_2.put()
    self.template_list = template_model.Template.get_all()

  def tearDown(self):
    super(TemplateApiTest, self).tearDown()
    self.service = None

  def test_get_list_api(self):
    response = self.service.list(message_types.VoidMessage())
    self.assertEqual(
        self.template_list[0].body,
        response.templates[0].body)
    self.assertEqual(
        self.template_list[0].title,
        response.templates[0].title)
    self.assertEqual(
        self.template_list[1].body,
        response.templates[1].body)
    self.assertEqual(
        self.template_list[1].title,
        response.templates[1].title)

  def test_update_template_api(self):
    request = template_messages.UpdateTemplateRequest(name='second_template',
                                                      body='test update',
                                                      title='update title')
    with mock.patch.object(
        self.service, 'check_xsrf_token', autospec=True) as mock_xsrf_token:
      response = self.service.update(request)
      self.assertEqual(mock_xsrf_token.call_count, 1)
    self.assertIsInstance(response, message_types.VoidMessage)
    template = template_model.Template.get('second_template')
    self.assertEqual(
        template.body,
        'test update')
    self.assertEqual(
        template.title,
        'update title')

  def test_remove_template_api(self):
    request = template_messages.RemoveTemplateRequest(name='second_template')
    with mock.patch.object(
        self.service, 'check_xsrf_token', autospec=True) as mock_xsrf_token:
      response = self.service.remove(request)
      self.assertEqual(mock_xsrf_token.call_count, 1)
    self.assertIsInstance(response, message_types.VoidMessage)
    template = template_model.Template.get('second_template')
    self.assertIsNone(template)

  def test_create(self):
    request = template_messages.CreateTemplateRequest(
        template=template_messages.Template(
            name='test_create_template',
            body='test create body',
            title='test create title'))
    with mock.patch.object(
        self.service, 'check_xsrf_token', autospec=True) as mock_xsrf_token:
      response = self.service.create(request)
      self.assertEqual(mock_xsrf_token.call_count, 1)
      self.assertIsInstance(response, message_types.VoidMessage)

  def test_create_bad_request(self):
    """Test create raises BadRequestException with required fields missing."""
    request = template_messages.CreateTemplateRequest(
        template=template_messages.Template(
            name='',
            body='',
            title='test_title'))
    with self.assertRaises(endpoints.BadRequestException):
      self.service.create(request)

  def test_update_bad_request(self):
    """Tests update raises BadRequestException with required fields missing."""
    request = template_messages.UpdateTemplateRequest(
        name='this_template',
        body='',
        title='')
    with self.assertRaises(endpoints.BadRequestException):
      self.service.update(request)

  def test_create_duplicate_name(self):
    request = template_messages.CreateTemplateRequest(
        template=template_messages.Template(
            name='test_create_template',
            body='test create body',
            title='test create title'))
    with mock.patch.object(
        self.service, 'check_xsrf_token', autospec=True) as mock_xsrf_token:
      response = self.service.create(request)
      self.assertEqual(mock_xsrf_token.call_count, 1)
      self.assertIsInstance(response, message_types.VoidMessage)
    request = template_messages.CreateTemplateRequest(
        template=template_messages.Template(
            name='test_create_template',
            body='test second body',
            title='test second title'))
    with mock.patch.object(
        self.service, 'check_xsrf_token', autospec=True) as mock_xsrf_token:
      with self.assertRaises(endpoints.BadRequestException):
        response = self.service.create(request)

if __name__ == '__main__':
  loanertest.main()
