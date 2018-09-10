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

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

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
  _INDEX_NAME = 'TestIndex'

  @property
  def identifier(self):
    return 'name'


class TestSubEntity(base_model.BaseModel):
  """A test class used for TestEntity structured property."""
  test_substring = ndb.StringProperty()
  test_subdatetime = ndb.DateTimeProperty(auto_now_add=True)


class TestEntity(base_model.BaseModel):
  """A test class used to create test entities of all ndb properties."""
  test_string = ndb.StringProperty()
  test_datetime = ndb.DateTimeProperty(auto_now_add=True)
  test_keyproperty = ndb.KeyProperty()
  test_geopt = ndb.GeoPtProperty()
  test_structuredprop = ndb.StructuredProperty(TestSubEntity)
  test_repeatedprop = ndb.StringProperty(repeated=True)
  test_bool = ndb.BooleanProperty()


class BaseModelTest(loanertest.TestCase, parameterized.TestCase):
  """Tests for BaseModel class."""

  @mock.patch.object(base_model, 'taskqueue')
  def test_stream_to_bq(self, mock_taskqueue):
    test_shelf = shelf_model.Shelf(location='Here', capacity=16)
    test_shelf.put()

    test_shelf.stream_to_bq(
        'test@{}'.format(loanertest.USER_DOMAIN), 'Test stream')

    self.assertTrue(mock_taskqueue.add.called)

  def test_to_json_dict(self):
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

  @mock.patch.object(Test, 'to_document')
  def test_index_entities_for_search(self, mock_to_document):
    base_model.search.MAXIMUM_DOCUMENTS_PER_PUT_REQUEST = 1
    test_entity_1_key = Test(text_field='item_1').put()
    test_entity_2_key = Test(text_field='item_2').put()
    documents = [
        search.Document(
            doc_id=test_entity_1_key.urlsafe(),
            fields=[search.TextField(name='text_field', value='item_1')]),
        search.Document(
            doc_id=test_entity_2_key.urlsafe(),
            fields=[search.TextField(name='text_field', value='item_2')]),]
    mock_to_document.side_effect = documents
    Test.index_entities_for_search()
    self.assertEqual(mock_to_document.call_count, 2)

  @mock.patch.object(base_model, 'logging', autospec=True)
  @mock.patch.object(base_model.BaseModel, 'to_document', autospec=True)
  def test_index_entities_for_search_error(
      self, mock_to_document, mock_logging):
    entity = Test(text_field='item_1').put()
    mock_to_document.side_effect = base_model.DocumentCreationError
    Test.index_entities_for_search()
    mock_logging.error.assert_called_once_with(
        base_model._CREATE_DOC_ERR_MSG, entity)

  def test_get_index(self):
    base_model.BaseModel._INDEX_NAME = None
    with self.assertRaises(ValueError):
      base_model.BaseModel.get_index()

  def test_add_docs_to_index(self):
    base_model.BaseModel._INDEX_NAME = 'test'
    test_index = base_model.BaseModel.get_index()
    base_model.BaseModel.add_docs_to_index([search.Document(
        doc_id='test_id', fields=[
            search.TextField(name='field_one', value='value_one')])])
    self.assertIsInstance(
        test_index.get_range(
            start_id='test_id', limit=1, include_start_object=True)[0],
        search.Document)

  @mock.patch.object(search.Index, 'put')
  def test_add_docs_to_index_put_error(self, mock_put):
    mock_put.side_effect = [
        search.PutError(message='Fail!', results=[
            search.PutResult(code=search.OperationResult.TRANSIENT_ERROR)]),
        None]
    base_model.BaseModel.add_docs_to_index([search.Document(
        doc_id='test_id', fields=[
            search.TextField(name='field_one', value='value_one')])])
    self.assertEqual(mock_put.call_count, 2)

  @parameterized.parameters(
      (search.Error(),),
      (base_model.apiproxy_errors.OverQuotaError,))
  @mock.patch.object(base_model, 'logging', autospec=True)
  @mock.patch.object(search.Index, 'put')
  def test_add_docs_to_index_error(self, mock_error, mock_put, mock_logging):
    mock_put.side_effect = mock_error
    base_model.BaseModel.add_docs_to_index([search.Document(
        doc_id='test_id', fields=[
            search.TextField(name='field_one', value='value_one')])])
    self.assertEqual(mock_put.call_count, 1)
    self.assertEqual(mock_logging.error.call_count, 1)

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

  @mock.patch.object(base_model, 'logging', autospec=True)
  @mock.patch.object(search.Index, 'delete', autospec=True)
  def test_remove_doc_by_id_delete_error(self, mock_delete, mock_logging):
    mock_delete.side_effect = search.DeleteError(
        message='Delete Fail!', results=[])
    base_model.BaseModel.remove_doc_by_id('test_id')
    mock_logging.error.assert_called_once_with(
        base_model._REMOVE_DOC_ERR_MSG, 'test_id')

  def test_clear_index(self):
    test_index = Test.get_index()
    test_index.put([
        search.Document(
            doc_id='test_id_one', fields=[
                search.TextField(name='field_one', value='value_one')]),
        search.Document(
            doc_id='test_id_two', fields=[
                search.AtomField(name='field_two', value='value_two')]),
        search.Document(
            doc_id='test_id_three', fields=[
                search.NumberField(name='field_three', value=3)])])
    # Ensure both docs were added to the index.
    self.assertLen(test_index.get_range(ids_only=True), 3)
    Test.clear_index()
    # Ensure the index was cleared.
    self.assertFalse(test_index.get_range(ids_only=True))

  @mock.patch.object(base_model, 'logging', autospec=True)
  @mock.patch.object(search.Index, 'delete', autospec=True)
  @mock.patch.object(search.Index, 'get_range', autospec=True)
  def test_clear_index_delete_error(
      self, mock_range, mock_delete, mock_logging):
    mock_range.return_value = [search.ScoredDocument(doc_id='unused_doc_id')]
    mock_delete.side_effect = search.DeleteError(
        message='Delete Fail!', results=[])
    base_model.BaseModel.clear_index()
    self.assertEqual(mock_logging.exception.call_count, 1)

  def test_to_seach_fields(self):
    # Test list field generation.
    entity = TestEntity(test_repeatedprop=['item_1', 'item_2'])
    search_fields = entity._to_search_fields(
        'test_repeatedprop', ['item_1', 'item_2'])
    expected_fields = [
        search.TextField(name='test_repeatedprop', value='item_1'),
        search.AtomField(name='test_repeatedprop', value='item_1'),
        search.TextField(name='test_repeatedprop', value='item_2'),
        search.AtomField(name='test_repeatedprop', value='item_2')]
    self.assertEqual(expected_fields, search_fields)

    # Test ndb.Key field generation.
    test_key = ndb.Key('Test', 1)
    entity = TestEntity(test_keyproperty=test_key)
    search_field = entity._to_search_fields('test_keyproperty', test_key)
    expected_field = [search.AtomField(
        name='test_keyproperty', value=test_key.urlsafe())]
    self.assertEqual(expected_field, search_field)

    # Test datetime field generation.
    date = datetime.datetime(year=2017, month=1, day=5)
    entity = TestEntity(test_datetime=date)
    search_field = entity._to_search_fields('test_datetime', date)
    expected_field = [search.DateField(name='test_datetime', value=date)]
    self.assertEqual(expected_field, search_field)

    # Test boolean field generation.
    entity = TestEntity(test_bool=True)
    search_field = entity._to_search_fields('test_bool', True)
    expected_field = [search.AtomField(name='test_bool', value='True')]
    self.assertEqual(expected_field, search_field)

    # Test geopt field generation.
    geopt = ndb.GeoPt('52.37, 4.88')
    entity = TestEntity(test_geopt=geopt)
    search_field = entity._to_search_fields('test_geopt', geopt)
    expected_field = [search.GeoField(
        name='test_geopt', value=search.GeoPoint(52.37, 4.88))]
    self.assertEqual(expected_field, search_field)

  @mock.patch.object(base_model.BaseModel, '_to_search_fields')
  def test_get_document_fields(self, mock_to_search_fields):
    test_model = Test(text_field='item_1')
    text_field1 = search.TextField(name='text_field', value='item_1')
    test_field2 = search.TextField(name='identifier', value='name')
    expected_result = [text_field1, test_field2]
    mock_to_search_fields.side_effect = [[text_field1], [test_field2]]
    document_fields = test_model._get_document_fields()
    self.assertCountEqual(expected_result, document_fields)
    self.assertEqual(mock_to_search_fields.call_count, 2)

  @mock.patch.object(base_model.BaseModel, '_to_search_fields')
  def test_get_document_fields_no_identifier(self, mock_to_search_fields):
    test_model = TestSubEntity(test_substring='item_1')
    text_field1 = search.TextField(name='test_substring', value='item_1')
    test_field2 = search.TextField(name='test_subdatetime', value='name')
    expected_result = [text_field1, test_field2]
    mock_to_search_fields.side_effect = [[text_field1], [test_field2]]
    document_fields = test_model._get_document_fields()
    self.assertCountEqual(expected_result, document_fields)
    self.assertEqual(mock_to_search_fields.call_count, 2)

  @mock.patch.object(
      base_model.BaseModel, '_get_document_fields', autospec=True)
  def test_to_document(self, mock_get_document_fields):
    test_model = Test(id='fake')
    fields = [search.AtomField(name='text_field', value='12345ABC')]
    mock_get_document_fields.return_value = fields
    test_document = search.Document(
        doc_id=test_model.key.urlsafe(), fields=fields)
    result = test_model.to_document()
    self.assertEqual(result, test_document)

  @mock.patch.object(
      base_model.BaseModel, '_get_document_fields', return_value=False,
      autospec=True)
  def test_to_document_error(self, mock_get_document_fields):
    test_model = Test(id='fake')
    with self.assertRaises(base_model.DocumentCreationError):
      test_model.to_document()

  def test_search(self):
    index = Test.get_index()
    test_doc = search.Document(
        doc_id='test_doc_id_1',
        fields=[search.TextField(name='text_field', value='item 1')])
    not_used_doc = search.Document(
        doc_id='test_doc_id_2',
        fields=[search.TextField(name='text_field', value='item 2')])
    not_used_doc2 = search.Document(
        doc_id='test_doc_id_3',
        fields=[search.TextField(name='text_field', value='notused')])
    index.put(test_doc)
    index.put(not_used_doc)
    index.put(not_used_doc2)
    actual_search_result = Test.search(query_string='item', query_limit=1)
    self.assertEqual(actual_search_result.number_found, 2)
    self.assertLen(actual_search_result.results, 1)

    no_search_results = Test.search(query_string='does_not_exist')
    self.assertEqual(no_search_results.number_found, 0)

  @mock.patch.object(search, 'Query', autospec=True)
  def test_search_query_error(self, mock_query):
    mock_query.side_effect = search.QueryError
    search_result = Test.search(query_string='item1')
    self.assertIsInstance(search_result, search.SearchResults)

  @parameterized.parameters(
      ('a:123456', 'asset_tag:123456',),
      ('at:123456', 'asset_tag:123456',),
      ('s:123456ABC', 'serial_number:123456ABC',),
      ('sn:123456ABC', 'serial_number:123456ABC',),
      ('u:user', 'assigned_user:user',),
      ('au:user', 'assigned_user:user',),
      ('j:not_in_params', 'j:not_in_params',),  # Not within the search params.
      ('123456', '123456',),  # Query string does not need formatting.
      (None, ''))  # None should return an empty string.
  def test_format_query(self, test_query_string, expected_query_string):
    Test._SEARCH_PARAMETERS = {
        'a': 'asset_tag', 'at': 'asset_tag', 's': 'serial_number',
        'sn': 'serial_number', 'u': 'assigned_user', 'au': 'assigned_user'}

    formatted_query_string = Test.format_query(test_query_string)
    self.assertEqual(expected_query_string, formatted_query_string)


if __name__ == '__main__':
  loanertest.main()
