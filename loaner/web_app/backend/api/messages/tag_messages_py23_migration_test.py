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
"""Tests for web_app.backend.api.messages.tag_messages."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from loaner.web_app.backend.api.messages import tag_messages
from absl.testing import absltest


class TagMessagesPy23MigrationTest(absltest.TestCase):

  def setUp(self):
    super(TagMessagesPy23MigrationTest, self).setUp()

    self.tag = tag_messages.Tag(
        name='FAKE-NAME',
        hidden=False,
        color='FAKE-COLOR',
        protect=True,
        description='FAKE-DESCRIPTION',
        urlsafe_key='FAKE-URL-KEY')

  def assert_tag(self, item):
    self.assertFalse(item.hidden)
    self.assertTrue(item.protect)
    self.assertEqual(item.name, 'FAKE-NAME')
    self.assertEqual(item.color, 'FAKE-COLOR')
    self.assertEqual(item.urlsafe_key, 'FAKE-URL-KEY')
    self.assertEqual(item.description, 'FAKE-DESCRIPTION')

  def testTag(self):
    self.assert_tag(self.tag)

  def testCreateTagRequest(self):
    create_tag_req = tag_messages.CreateTagRequest(tag=self.tag)
    self.assert_tag(create_tag_req.tag)

  def testUpdateTagRequest(self):
    update_tag_req = tag_messages.UpdateTagRequest(tag=self.tag)
    self.assert_tag(update_tag_req.tag)

  def testTagRequest(self):
    tag_req = tag_messages.TagRequest(urlsafe_key='FAKE-URL-KEY')
    self.assertEqual(tag_req.urlsafe_key, 'FAKE-URL-KEY')

  def testListTagRequest(self):
    list_tag_req = tag_messages.ListTagRequest(
        page_size=50,
        cursor='FAKE-CURSOR',
        page_index=2,
        include_hidden_tags=True)

    self.assertEqual(list_tag_req.page_index, 2)
    self.assertEqual(list_tag_req.page_size, 50)
    self.assertTrue(list_tag_req.include_hidden_tags)
    self.assertEqual(list_tag_req.cursor, 'FAKE-CURSOR')

  def testListTagResponse(self):
    list_tag_resp = tag_messages.ListTagResponse(
        tags=[],
        cursor='FAKE-CURSOR',
        has_additional_results=True,
        total_pages=20)

    self.assertListEqual(list_tag_resp.tags, [])
    self.assertEqual(list_tag_resp.total_pages, 20)
    self.assertEqual(list_tag_resp.cursor, 'FAKE-CURSOR')
    self.assertTrue(list_tag_resp.has_additional_results)

  def testTagData(self):
    tag_data = tag_messages.TagData(tag=None, more_info='FAKE-MORE-INFO')

    self.assertIsNone(tag_data.tag)
    self.assertEqual(tag_data.more_info, 'FAKE-MORE-INFO')


if __name__ == '__main__':
  absltest.main()
