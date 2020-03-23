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
"""Tests for web_app.backend.models.tag_model_py23_migration."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import mock
from loaner.web_app.backend.models import tag_model
from absl.testing import absltest


class TagModelPy23MigrationTest(absltest.TestCase):

  def setUp(self):
    super(TagModelPy23MigrationTest, self).setUp()
    self.tag = tag_model.Tag(
        name='TestTag1',
        hidden=False,
        protect=True,
        color='blue',
        description='Description 1.')

  @mock.patch.object(tag_model.ndb.Model, 'put')
  @mock.patch.object(tag_model.base_model.BaseModel, 'stream_to_bq')
  def testCreate(self, stream_to_bq_mock, model_put_mock):
    user_email = 'test@google.com'
    name = 'name'
    hidden = False
    protect = True
    color = 'grey'
    tag = tag_model.Tag.create(
        user_email, name, hidden, protect, color, description=None)
    stream_to_bq_mock.assert_called_once_with(
        'test@google.com', "Created a new tag with name 'name'.")
    model_put_mock.assert_called_once_with()
    self.assertEqual('grey', tag.color)
    self.assertEqual(False, tag.hidden)
    self.assertEqual(True, tag.protect)

  @mock.patch.object(tag_model.ndb.Model, 'put')
  @mock.patch.object(tag_model.base_model.BaseModel, 'stream_to_bq')
  @mock.patch.object(tag_model.Tag, 'key')
  def testUpdate(self, key_mock, stream_to_bq_mock, model_put_mock):
    self.tag.update(
        user_email='test@google.com',
        hidden=False,
        protect=False,
        color='blue',
        description='A new description.',
        name='TestTag2')
    stream_to_bq_mock.assert_called_once_with(
        'test@google.com', "Updated a tag with name 'TestTag2'.")
    model_put_mock.assert_called_once_with()
    key_mock.urlsafe.assert_called_once_with()

  @mock.patch.object(tag_model.Tag, 'query')
  def testPrePutHook(self, query_mock):
    self.tag = tag_model.Tag(
        name='TestTag3',
        hidden=False,
        protect=False,
        color='red',
        description='Description 2.')
    query_mock.return_value.get.return_value = False
    self.tag.name = 'test123'
    self.tag._pre_put_hook()
    query_mock.return_value.get.assert_called_once_with(keys_only=True)

  @mock.patch.object(tag_model.ndb, 'Key')
  @mock.patch.object(tag_model.logging, 'info')
  def testPreDeleteHook(self, info_mock, key_mock):
    self.tag = tag_model.Tag(
        name='TestTag3',
        hidden=False,
        protect=False,
        color='red',
        description='Description 2.')
    key_mock.urlsafe.return_value = 'test'
    key_mock.get.return_value.name = 'test_name'
    self.tag._pre_delete_hook(key_mock)
    info_mock.assert_called_once_with(
        'Destroying the tag with urlsafe key %r and name %r.', 'test',
        'test_name')
    key_mock.urlsafe.assert_called_once_with()

  @mock.patch.object(tag_model.Tag, 'query')
  def testList(self, query_mock):
    query_mock.return_value.fetch_page.return_value = 1
    tag_model.Tag.list(page_size=1, include_hidden_tags=True)
    query_mock.return_value.fetch_page.assert_called_once_with(
        offset=0, page_size=1, start_cursor=None)

  @mock.patch.object(tag_model.logging, 'info')
  @mock.patch.object(tag_model.deferred, 'defer')
  @mock.patch.object(tag_model.ndb, 'put_multi')
  def testDeleteTags(self, mock_ndb, mock_defer, mock_info):
    tag_mock = mock.Mock()
    tag_mock.key.urlsafe.return_value = 'http://test.com'
    model_tag_mock = mock.Mock(tags='test')
    entity_mock = mock.Mock()
    entity_mock.tags = [model_tag_mock]
    model_mock = mock.Mock()
    model_mock.query.return_value.fetch_page.return_value = ([entity_mock],
                                                             'test', True)
    tag_model._delete_tags(model_mock, tag=tag_mock, batch_size=2)
    mock_defer.assert_called_once_with(
        tag_model._delete_tags,
        model_mock,
        tag_mock,
        batch_size=2,
        cursor='test',
        num_updated=1)
    model_mock.query.return_value.fetch_page.assert_called_once_with(
        2, start_cursor=None)
    mock_ndb.assert_called_once_with([entity_mock])
    mock_info.assert_called_once_with(
        'Destroyed %d occurrence(s) of the tag with URL safe key %r', 1,
        'http://test.com')


class TestTagData(absltest.TestCase):

  def testTagDate(self):

    tag_model_object = tag_model.Tag(
        name='TestTag1', hidden=False, protect=True,
        color='blue', description='Description 1.')

    tag = tag_model.TagData(tag=tag_model_object, more_info='test_data')
    self.assertEqual('test_data', tag.more_info)
    self.assertEqual(tag_model_object, tag.tag)


if __name__ == '__main__':
  absltest.main()
