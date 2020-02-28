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

# Lint as: python3
"""Tests for web_app.backend.api.messages.template_messages."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from loaner.web_app.backend.api.messages import template_messages
from absl.testing import absltest


class TemplateMessagesPy23MigrationTest(absltest.TestCase):

  def testTemplateTypeTitle(self):
    title_tmpl_type = template_messages.TemplateType(1)
    self.assertEqual(title_tmpl_type.name, 'TITLE')

  def testTemplateTypeBody(self):
    body_tmpl_type = template_messages.TemplateType(2)
    self.assertEqual(body_tmpl_type.name, 'BODY')

  def testTemplate(self):
    template = template_messages.Template(
        name='TMPL-NAME',
        body='TMPL-BODY-CONTENT',
        title='TMPL-TITLE')

    self.assertEqual(template.name, 'TMPL-NAME')
    self.assertEqual(template.body, 'TMPL-BODY-CONTENT')
    self.assertEqual(template.title, 'TMPL-TITLE')

  def testListTemplatesResponse(self):
    tmpls = [
        template_messages.Template(name='TMPL-NAME-1'),
        template_messages.Template(name='TMPL-NAME-2')
    ]
    list_tmpl_resp = template_messages.ListTemplatesResponse(templates=tmpls)

    self.assertListEqual(list_tmpl_resp.templates, tmpls)

  def testUpdateTemplate(self):
    update_tmpl = template_messages.UpdateTemplate(
        name='TMPL-NAME',
        body='TMPL-BODY-CONTENTS',
        title='TMPL-TITLE')

    self.assertEqual(update_tmpl.name, 'TMPL-NAME')
    self.assertEqual(update_tmpl.body, 'TMPL-BODY-CONTENTS')
    self.assertEqual(update_tmpl.title, 'TMPL-TITLE')

  def testUpdateTemplateRequest(self):
    update_tmpl_req = template_messages.UpdateTemplateRequest(
        name='TMPL-NAME',
        body='TMPL-BODY-CONTENTS',
        title='TMPL-TITLE')

    self.assertEqual(update_tmpl_req.name, 'TMPL-NAME')
    self.assertEqual(update_tmpl_req.body, 'TMPL-BODY-CONTENTS')
    self.assertEqual(update_tmpl_req.title, 'TMPL-TITLE')

  def testRemoveTemplateRequest(self):
    remove_tmpl_req = template_messages.RemoveTemplateRequest(name='TMPL-NAME')
    self.assertEqual(remove_tmpl_req.name, 'TMPL-NAME')

  def testCreateTemplateRequest(self):
    tmpl = template_messages.Template(name='TMPL-NAME')
    create_tmpl_req = template_messages.CreateTemplateRequest(template=tmpl)
    self.assertEqual(create_tmpl_req.template, tmpl)


if __name__ == '__main__':
  absltest.main()
