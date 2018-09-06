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

import mock

from google.appengine.ext import ndb

from loaner.web_app.backend.models import device_model
from loaner.web_app.backend.models import shelf_model
from loaner.web_app.backend.models import tag_model
from loaner.web_app.backend.testing import loanertest


class TagModelTest(loanertest.TestCase):
  """Tests for the Tag class."""

  def setUp(self):
    super(TagModelTest, self).setUp()

    tag1_key = tag_model.Tag(
        name='TestTag1', visible=True, protect=True,
        color='blue', description='Description 1.').put()
    tag2_key = tag_model.Tag(
        name='TestTag2', visible=True, protect=False,
        color='red', description='Description 2.').put()

    self.tag1_data = device_model.TagData(
        tag_key=tag1_key, more_info='tag1_data info.')
    self.tag2_data = device_model.TagData(
        tag_key=tag2_key, more_info='tag2_data info.')

    shelf = shelf_model.Shelf(
        location='MTV', capacity=10, friendly_name='MTV office').put()
    self.device1 = device_model.Device(
        serial_number='12321', enrolled=True,
        device_model='HP Chromebook 13 G1', current_ou='/',
        shelf=shelf, chrome_device_id='unique_id_1',
        damaged=False, tags=[self.tag1_data, self.tag2_data]).put().get()
    self.device2 = device_model.Device(
        serial_number='67890', enrolled=True,
        device_model='Google Pixelbook', current_ou='/',
        shelf=shelf, chrome_device_id='unique_id_2',
        damaged=False, tags=[self.tag1_data, self.tag2_data]).put().get()
    self.device3 = device_model.Device(
        serial_number='Void', enrolled=False,
        device_model='HP Chromebook 13 G1', current_ou='/',
        shelf=shelf, chrome_device_id='unique_id_8',
        damaged=False, tags=[self.tag1_data, self.tag2_data]).put().get()

  def test_create(self):
    """Test the creation of a Tag."""
    self.assertEqual(
        tag_model.Tag.create(
            user_email=loanertest.USER_EMAIL,
            name='TestTag3', visible=True,
            protect=False, color='red',
            description='Description 3.'),
        tag_model.Tag.get('TestTag3'))

  def test_create_existing(self):
    """Test the creation of an existing Tag."""
    with self.assertRaises(tag_model.CreateTagError):
      tag_model.Tag.create(
          user_email=loanertest.USER_EMAIL,
          name='TestTag1', visible=True,
          protect=False, color='red',
          description='A description.')

  def test_update(self):
    """Test updating a Tag."""
    self.assertEqual(
        tag_model.Tag.update(
            user_email=loanertest.USER_EMAIL,
            name='TestTag2', visible=True,
            protect=False, color='red',
            description='A new description.'),
        tag_model.Tag.get('TestTag2'))

  def test_update_new_name(self):
    """Test the renaming of a Tag."""
    new_tag_name = tag_model.Tag.update(
        user_email=loanertest.USER_EMAIL,
        name='TestTag1', visible=True,
        protect=True, color='blue',
        description='Description 1.',
        new_name='TestTag1 Renamed')
    self.assertIn(
        device_model.TagData(
            tag_key=new_tag_name.key, more_info=self.tag1_data.more_info),
        self.device1.tags)
    self.assertIsNone(tag_model.Tag.get('TestTag1'))

  def test_update_non_existent(self):
    """Test updating a non-existent Tag."""
    with self.assertRaises(tag_model.UpdateTagError):
      tag_model.Tag.update(
          user_email=loanertest.USER_EMAIL,
          name='A tag that does not exist.', visible=True,
          protect=False, color='red',
          description='A description')

  def test_destroy_non_existent(self):
    """Test destroying a non-existent Tag."""
    with self.assertRaises(tag_model.DestroyTagError):
      tag_model.Tag.destroy(name='A tag that does not exist.')

  @mock.patch.object(ndb, 'put_multi', autospec=True)
  def test_destroy(self, mock_put_multi):
    """Test destroying a Tag."""
    tag_model.Tag.destroy('TestTag1')
    self.assertIsNone(tag_model.Tag.get('TestTag1'))
    self.assertNotIn(self.tag1_data, self.device1.tags)
    self.assertNotIn(self.tag1_data, self.device2.tags)
    self.assertNotIn(self.tag1_data, self.device3.tags)
    mock_put_multi.assert_called_once_with(
        [self.device1, self.device2, self.device3])

if __name__ == '__main__':
  loanertest.main()
