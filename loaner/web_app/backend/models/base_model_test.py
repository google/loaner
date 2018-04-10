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

import datetime

from absl.testing import parameterized
import mock

from google.appengine.api import search
from google.appengine.ext import ndb

from loaner.web_app.backend.models import base_model
from loaner.web_app.backend.models import shelf_model
from loaner.web_app.backend.testing import loanertest


class Test(base_model.BaseModel):
  """A test class used for this testing module."""
  text_field = ndb.StringProperty()


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

  def test_to_seach_fields(self):
    # Test list field generation.
    search_fields = base_model.BaseModel._to_search_fields(
        'list_field', ['item_1', 'item_2'])
    expected_fields = [
        search.TextField(name='list_field', value='item_1'),
        search.TextField(name='list_field', value='item_2')]
    self.assertEqual(expected_fields, search_fields)

    # Test ndb.Key field generation.
    test_key = ndb.Key('Test', 1)
    search_field = base_model.BaseModel._to_search_fields(
        'key_field', test_key)
    expected_field = [search.AtomField(
        name='key_field', value=test_key.urlsafe())]
    self.assertEqual(expected_field, search_field)

    # Test datetime field generation.
    search_field = base_model.BaseModel._to_search_fields(
        'datetime_field', datetime.datetime(year=2017, month=1, day=5))
    expected_field = [search.DateField(
        name='datetime_field',
        value=datetime.datetime(year=2017, month=1, day=5))]
    self.assertEqual(expected_field, search_field)

    # Test boolean field generation.
    search_field = base_model.BaseModel._to_search_fields('bool_field', True)
    expected_field = [search.AtomField(
        name='bool_field', value='True')]
    self.assertEqual(expected_field, search_field)

    # Test geopt field generation.
    search_field = base_model.BaseModel._to_search_fields(
        'geopt_field', ndb.GeoPt('52.37, 4.88'))
    expected_field = [search.GeoField(
        name='geopt_field', value=search.GeoPoint(52.37, 4.88))]
    self.assertEqual(expected_field, search_field)

  @mock.patch.object(
      base_model.BaseModel, '_to_search_fields', auto_spec=True)
  def test_get_document_fields(self, mock_to_search_fields):
    test_model = Test(text_field='item_1')
    expected_result = [search.TextField(name='text_field', value='item_1')]
    mock_to_search_fields.side_effect = [expected_result]
    document_fields = test_model._get_document_fields()
    self.assertCountEqual(expected_result, document_fields)

  @mock.patch.object(
      base_model.BaseModel, '_get_document_fields', auto_spec=True)
  @mock.patch.object(
      base_model.BaseModel, 'is_valid_doc_id', return_value=True,
      auto_spec=True)
  def test_to_document(self, mock_is_valid_doc_id, mock_get_document_fields):
    test_model = Test(id='fake')
    fields = [search.AtomField(name='text_field', value='12345ABC')]
    mock_get_document_fields.return_value = fields
    test_document = search.Document(doc_id=test_model.key.id(), fields=fields)
    result = test_model.to_document()
    self.assertEqual(result, test_document)

  @mock.patch.object(
      base_model.BaseModel, 'is_valid_doc_id', return_value=False,
      auto_spec=True)
  def test_to_document_doc_id_none(self, mock_is_valid_doc_id):
    test_model = Test(id='fake')
    result = test_model.to_document()
    self.assertIsNone(result.doc_id)

  @mock.patch.object(
      base_model.BaseModel, '_get_document_fields', return_value=False,
      auto_spec=True)
  def test_to_document_error(self, mock_get_document_fields):
    test_model = Test(id='fake')
    with self.assertRaises(base_model.DocumentCreationError):
      test_model.to_document()


if __name__ == '__main__':
  loanertest.main()
