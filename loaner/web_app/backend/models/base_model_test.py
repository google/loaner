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

"""Tests for backend.models.base_model."""

import mock

from google.appengine.ext import ndb

from loaner.web_app.backend.models import base_model
from loaner.web_app.backend.models import shelf_model
from loaner.web_app.backend.testing import loanertest


class BaseModelTest(loanertest.TestCase):
  """Tests for BaseModel class."""

  @mock.patch.object(base_model, 'taskqueue')
  def test_stream_to_bq(self, mock_taskqueue):
    test_shelf = shelf_model.Shelf(location='Here', capacity=16)
    test_shelf.put()

    test_shelf.stream_to_bq(
        'test@{}'.format(loanertest.USER_DOMAIN), 'Test stream')

    assert mock_taskqueue.add.called

  def test_to_json_dict(self):
    class TestSubEntity(base_model.BaseModel):
      test_substring = ndb.StringProperty()
      test_subdatetime = ndb.DateTimeProperty(auto_now_add=True)

    class TestEntity(base_model.BaseModel):
      test_string = ndb.StringProperty()
      test_datetime = ndb.DateTimeProperty(auto_now_add=True)
      test_keyproperty = ndb.KeyProperty()
      test_geopt = ndb.GeoPtProperty()
      test_structuredprop = ndb.StructuredProperty(TestSubEntity)
      test_repeatedprop = ndb.StringProperty(repeated=True)

    entity = TestEntity(test_string='Hello', test_geopt=ndb.GeoPt(50, 100))
    entity.test_structuredprop = TestSubEntity(test_substring='foo')
    entity.put()
    entity.test_keyproperty = entity.key
    entity.put()

    entity_dict = entity.to_json_dict()

    self.assertIsInstance(entity_dict.get('test_datetime'), int)
    self.assertIsInstance(
        entity_dict['test_structuredprop']['test_subdatetime'], int)
    self.assertIsInstance(entity_dict['test_repeatedprop'], list)


if __name__ == '__main__':
  loanertest.main()
