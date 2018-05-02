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


class TemplateTest(loanertest.TestCase):
  """Tests for the TemplateLoader class and Template model."""

  def test_templates(self):
    template = template_model.Template.create(
        'loaner_due', title=TEST_TITLE, body=TEST_BODY)
    self.assertEqual(template.name, 'loaner_due')

    template_model.Template.create('reminder_base', body=TEST_BASE)
    template_loader = template_model.TemplateLoader()

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

if __name__ == '__main__':
  loanertest.main()
