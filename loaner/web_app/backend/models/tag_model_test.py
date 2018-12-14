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

"""Tests for backend.models.tag_model."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from absl.testing import parameterized

import mock

from google.appengine.api import datastore_errors
from google.appengine.ext import deferred
from google.appengine.ext import ndb

from loaner.web_app.backend.models import base_model
from loaner.web_app.backend.models import tag_model
from loaner.web_app.backend.testing import loanertest


class _ModelWithTags(base_model.BaseModel):
  """Datastore model representing a model with a tags property."""
  tags = ndb.StructuredProperty(tag_model.TagData, repeated=True)


class TagModelTest(loanertest.TestCase, parameterized.TestCase):
  """Tests for the Tag class."""

  def setUp(self):
    super(TagModelTest, self).setUp()

    tag_model._MODELS_WITH_TAGS = (_ModelWithTags,)

    self.tag1 = tag_model.Tag(
        name='TestTag1', hidden=False, protect=True,
        color='blue', description='Description 1.')
    self.tag2 = tag_model.Tag(
        name='TestTag2', hidden=False, protect=False,
        color='red', description='Description 2.')
    self.tag1.put()
    self.tag2.put()

    self.tag1_data = tag_model.TagData(
        tag_key=self.tag1.key, more_info='tag1_data info.')
    self.tag2_data = tag_model.TagData(
        tag_key=self.tag2.key, more_info='tag2_data info.')

    self.entity1 = _ModelWithTags(
        tags=[self.tag1_data, self.tag2_data]).put().get()
    self.entity2 = _ModelWithTags(
        tags=[self.tag1_data, self.tag2_data]).put().get()
    self.entity3 = _ModelWithTags(
        tags=[self.tag1_data, self.tag2_data]).put().get()

  @mock.patch.object(base_model.BaseModel, 'stream_to_bq', autospec=True)
  def test_create(self, mock_stream_to_bq):
    """Test the creation of a Tag."""
    tag_entity = tag_model.Tag.create(
        user_email=loanertest.USER_EMAIL,
        name='TestTag4',
        hidden=False,
        protect=False,
        color='red',
        description='Description 4.')
    self.assertEqual(
        tag_entity, tag_model.Tag.get(
            urlsafe_key=tag_entity.key.urlsafe()))
    self.assertEqual(mock_stream_to_bq.call_count, 1)

  def test_create_existing(self):
    """Test the creation of an existing Tag."""
    with self.assertRaises(datastore_errors.BadValueError):
      tag_model.Tag.create(
          user_email=loanertest.USER_EMAIL,
          name='TestTag1',
          hidden=False,
          protect=False,
          color='red',
          description='A description.')

  def test_update(self):
    """Test updating a Tag."""
    self.tag2.update(
        user_email=loanertest.USER_EMAIL,
        hidden=False,
        protect=False,
        color='blue',
        description='A new description.',
        name='TestTag2')
    self.assertFalse(self.tag2.hidden)
    self.assertFalse(self.tag2.protect)
    self.assertEqual(self.tag2.color, 'blue')
    self.assertEqual(self.tag2.description, 'A new description.')
    self.assertEqual(self.tag2.name, 'TestTag2')

  def test_update_new_name(self):
    """Test the renaming of a Tag."""
    self.tag1.update(
        user_email=loanertest.USER_EMAIL,
        hidden=True,
        protect=True,
        color='blue',
        description='Description 1.',
        name='TestTag1 Renamed')
    self.assertIn(
        tag_model.TagData(
            tag_key=self.tag1.key, more_info=self.tag1_data.more_info),
        self.entity1.tags)
    self.assertEqual(self.tag1.name, 'TestTag1 Renamed')

  def test_update_new_name_fail(self):
    """Test renaming a Tag to a name that already exists."""
    with self.assertRaises(datastore_errors.BadValueError):
      self.tag2.update(
          user_email=loanertest.USER_EMAIL,
          hidden=False,
          protect=False,
          color='red',
          description='A new description.',
          name='TestTag1')

  @parameterized.parameters(
      ('TestTag1', 'tag1_data info.'),
      ('TestTag2', 'tag2_data info.'),
  )
  @mock.patch.object(ndb, 'put_multi', autospec=True)
  def test_destroy(self, tag, tag_info, mock_put_multi):
    """Test destroying an existing Tag using deferred tasks."""
    tag_key = tag_model.Tag.query(tag_model.Tag.name == tag).get().key
    tag_key.delete()

    tasks = self.taskqueue_stub.get_filtered_tasks()
    deferred.run(tasks[0].payload)

    tag_data = tag_model.TagData(tag_key=tag_key, more_info=tag_info)
    self.assertIsNone(tag_key.get())
    self.assertNotIn(tag_data, self.entity1.tags)
    self.assertNotIn(tag_data, self.entity2.tags)
    self.assertNotIn(tag_data, self.entity3.tags)
    mock_put_multi.assert_called_once_with(
        [self.entity1, self.entity2, self.entity3])

  def test_delete_tags(self):
    """Test destroying a Tag in small batches to test multiple defer calls."""
    tag_model._delete_tags(
        _ModelWithTags, key=self.tag1.key, batch_size=2)
    tasks = self.taskqueue_stub.get_filtered_tasks()
    deferred.run(tasks[0].payload)
    deferred.run(tasks[0].payload)
    self.assertNotIn(self.tag1_data, self.entity1.tags)
    self.assertNotIn(self.tag1_data, self.entity2.tags)
    self.assertNotIn(self.tag1_data, self.entity3.tags)

if __name__ == '__main__':
  loanertest.main()
