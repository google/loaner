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

from absl.testing import parameterized
import mock

from google.appengine.api import search
from google.appengine.ext import ndb

from loaner.web_app.backend.models import base_model
from loaner.web_app.backend.models import shelf_model
from loaner.web_app.backend.testing import loanertest


class BaseModelTest(loanertest.TestCase, parameterized.TestCase):
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

  def test_maintain_search_index_failure(self):
    with self.assertRaises(NotImplementedError):
      test_model = base_model.BaseModel()
      test_model.maintain_search_index()

  @parameterized.parameters(
      ('thisIsAValidDocId',),
      ('1234AlsoValid',),
      ('Also_Valid_a123',))
  def test_is_valid_doc_id(self, doc_id):
    test_model = base_model.BaseModel()
    self.assertTrue(test_model.is_valid_doc_id(doc_id))

  @parameterized.parameters(
      ('!InvalidDocId',),
      ('__InvalidDocId',),
      ('invalid-doc id',))
  def test_invalid_doc_ids(self, doc_id):
    test_model = base_model.BaseModel()
    self.assertFalse(test_model.is_valid_doc_id(doc_id))

  def test_get_index(self):
    base_model.BaseModel._INDEX_NAME = None
    with self.assertRaises(ValueError):
      base_model.BaseModel.get_index()

  def test_add_doc_to_index(self):
    base_model.BaseModel._INDEX_NAME = 'test'
    test_index = base_model.BaseModel.get_index()
    base_model.BaseModel.add_doc_to_index(search.Document(
        doc_id='test_id', fields=[
            search.TextField(name='field_one', value='value_one')]))
    self.assertIsInstance(
        test_index.get_range(
            start_id='test_id', limit=1, include_start_object=True)[0],
        search.Document)

  @mock.patch.object(search.Index, 'put', auto_spec=True)
  def test_add_doc_to_index_put_error(self, mock_put):
    mock_put.side_effect = [
        search.PutError(message='Fail!', results=[
            search.PutResult(code=search.OperationResult.TRANSIENT_ERROR)]),
        None]
    base_model.BaseModel.add_doc_to_index(search.Document(
        doc_id='test_id', fields=[
            search.TextField(name='field_one', value='value_one')]))
    assert mock_put.call_count == 2

  @mock.patch.object(base_model, 'logging', auto_spec=True)
  @mock.patch.object(search.Index, 'put', auto_spec=True)
  def test_add_doc_to_index_error(self, mock_put, mock_logging):
    mock_put.side_effect = search.Error()
    base_model.BaseModel.add_doc_to_index(search.Document(
        doc_id='test_id', fields=[
            search.TextField(name='field_one', value='value_one')]))
    assert mock_put.call_count == 1
    assert mock_logging.error.call_count == 1

  def test_get_doc_by_id(self):
    base_model.BaseModel._INDEX_NAME = 'test'
    test_index = base_model.BaseModel.get_index()
    test_index.put([search.Document(
        doc_id='test_id', fields=[
            search.TextField(name='field_one', value='value_one')])])
    self.assertIsInstance(
        base_model.BaseModel.get_doc_by_id(doc_id='test_id'), search.Document)

  def test_remove_doc_by_id(self):
    base_model.BaseModel._INDEX_NAME = 'test'
    test_index = base_model.BaseModel.get_index()
    test_index.put([search.Document(
        doc_id='test_id', fields=[
            search.TextField(name='field_one', value='value_one')])])
    base_model.BaseModel.remove_doc_by_id('test_id')
    test_response = test_index.get_range(
        start_id='test_id', limit=1, include_start_object=True)
    self.assertIsInstance(test_response, search.GetResponse)
    self.assertEqual(test_response.results, [])

  @mock.patch.object(base_model, 'logging', auto_spec=True)
  @mock.patch.object(search.Index, 'delete', auto_spec=True)
  def test_remove_doc_by_id_delete_error(self, mock_delete, mock_logging):
    mock_delete.side_effect = search.DeleteError(
        message='Delete Fail!', results=[])
    base_model.BaseModel.remove_doc_by_id('test_id')
    mock_logging.error.assert_called_once_with(
        base_model._REMOVE_DOC_ERR_MSG, 'test_id')


if __name__ == '__main__':
  loanertest.main()
