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

"""Tests for backend.models.template_model."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import datetime

from absl.testing import parameterized
from google.appengine.api import datastore_errors
from google.appengine.api import memcache
from loaner.web_app.backend.models import template_model
from loaner.web_app.backend.testing import loanertest

TEST_BASE = '<html><body>{% block body %}{% endblock %}</body></html>'
TEST_TITLE = 'Your loaner is due on {{day_of_week}}'
TEST_BODY = (
    '{% extends "reminder_base" %}'
    '{% block body %}'
    'Hello, {{user_email}}. Your loaner with serial number {{serial}} is due '
    'on {{date}}. Return it by then if you ever want to see your pet turtle, '
    '{{turtle_name}}, again.'
    '{% endblock %}')


def _create_template_parameters():
  """Creates a template list of parameters for parameterized test cases.

  Yields:
    A list containing values for template parameters
  """
  template_name_value = 'this_template'
  body_value = 'body update test'
  title_value = 'title update test'

  template_parameters = [template_name_value, title_value, body_value]
  yield [template_parameters]


class TemplateTest(parameterized.TestCase, loanertest.TestCase):
  """Tests for the TemplateLoader class and Template model."""

  def setUp(self):
    super(TemplateTest, self).setUp()
    self.template_model_1 = template_model.Template(
        id='this_template', body='template body 1', title='title').put().get()
    self.template_model_2 = template_model.Template(
        id='second_template', body='template body 2',
        title='title 2').put().get()

  def test_get(self):
    self.assertEqual(
        template_model.Template.get('this_template'),
        self.template_model_1)

  def test_create_template_name_with_empty_string(self):
    """Test the creation of a Template with an empty string."""
    with self.assertRaises(datastore_errors.BadValueError):
      template_model.Template.create(
          name='',
          title='test',
          body='test')

  def test_create_existing(self):
    """Test the creation of an existing template."""
    with self.assertRaises(datastore_errors.BadValueError):
      template_model.Template.create(
          name='this_template',
          title='test')

  def test_get_all_from_datastore(self):
    templates = template_model.Template.get_all()
    self.assertLen(templates, 2)

  def test_get_all_from_memcache(self):
    template_list = ['template1', 'template2', 'template3']
    mem_name = 'template_list'
    memcache.set(mem_name, template_list)
    template_list_memcache = template_model.Template.get_all()
    self.assertLen(template_list_memcache, 2)
    memcache.flush_all()
    reference_datastore_template_list = template_model.Template.get_all()
    self.assertLen(reference_datastore_template_list, 2)

  @parameterized.parameters(_create_template_parameters())
  def test_remove(self, test_template):
    self.template_model_2.remove()
    entity_keys = template_model.Template.query().fetch()
    entity_deleted = template_model.Template.get_by_id('second_template')
    self.assertLen(entity_keys, 1)
    self.assertEqual(entity_deleted, None)

  @parameterized.parameters(_create_template_parameters())
  def test_update(self, test_template):
    self.template_model_1.update(
        name=test_template[0], title=test_template[1], body=test_template[2])
    updated_template = template_model.Template.get_by_id('this_template')
    self.assertEqual(updated_template.name, test_template[0])
    self.assertEqual(updated_template.title, test_template[1])
    self.assertEqual(updated_template.body, test_template[2])

  @parameterized.parameters(_create_template_parameters())
  def test_update_one_field_empty(self, test_template):
    self.template_model_1.update(
        name=test_template[0], body=test_template[2])
    updated_template = template_model.Template.get_by_id('this_template')
    self.assertEqual(updated_template.name, test_template[0])
    self.assertEqual(updated_template.body, test_template[2])

  @parameterized.parameters(_create_template_parameters())
  def test_update_failure(self, test_template):
    with self.assertRaises(datastore_errors.BadValueError):
      self.template_model_1.update(name=test_template[0])

  @parameterized.parameters(_create_template_parameters())
  def test_update_get_all(self, test_template):
    update_template = template_model.Template(
        id='this_template', body='body update test', title='title update test')
    self.template_model_1.update(
        name=update_template.name,
        title=update_template.title,
        body=update_template.body)
    templates = template_model.Template.get_all()
    index = templates.index(update_template)
    self.assertEqual(templates[index].title, test_template[1])
    self.assertEqual(templates[index].body, test_template[2])

  def test_templates(self):
    template = template_model.Template.create(
        'loaner_due', title=TEST_TITLE, body=TEST_BODY)
    self.assertEqual(template.name, 'loaner_due')

    template_model.Template.create('reminder_base', body=TEST_BASE)
    template_loader = template_model.Template()

    due_date = datetime.datetime(2017, 10, 13, 9, 31, 0, 0)
    config_dict = {
        'user_email': loanertest.USER_EMAIL,
        'serial': '12345ABC',
        'day_of_week': due_date.strftime('%A'),
        'date': due_date.strftime('%A, %B %d'),
        'turtle_name': 'Grumpy'
    }
    rendered_title, rendered_body = template_loader.render(
        'loaner_due', config_dict)
    self.assertEqual(rendered_title, 'Your loaner is due on Friday')
    self.assertEqual(rendered_body, (
        '<html><body>'  # Includes the reminder_base template.
        'Hello, {}. Your loaner with serial number '
        '12345ABC is due on Friday, October 13. Return it by then if you ever '
        'want to see your pet turtle, Grumpy, again.'
        '</body></html>'.format(loanertest.USER_EMAIL)))

    # Without memcache
    memcache.flush_all()
    rendered_title, rendered_body = template_loader.render(
        'loaner_due', config_dict)
    self.assertEqual(rendered_title, 'Your loaner is due on Friday')
    self.assertEqual(rendered_body, (
        '<html><body>'
        'Hello, {}. Your loaner with serial number '
        '12345ABC is due on Friday, October 13. Return it by then if you ever '
        'want to see your pet turtle, Grumpy, again.'
        '</body></html>'.format(loanertest.USER_EMAIL)))

  @parameterized.parameters(_create_template_parameters())
  def test_create(self, test_template):
    created_template = template_model.Template.create(
        name='new_created_one', title=test_template[1], body=test_template[2])
    templates = template_model.Template.get_all()
    index = templates.index(created_template)
    self.assertEqual(templates[index].title, test_template[1])
    self.assertEqual(templates[index].body, test_template[2])
    self.assertLen(templates, 3)
    created_template.remove()

if __name__ == '__main__':
  loanertest.main()
