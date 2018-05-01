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

"""Tests for backend.clients.bigquery_client."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import datetime

import mock

# pylint: disable=g-bad-import-order
from loaner.web_app.backend.common import google_cloud_lib_fixer  # pylint: disable=unused-import
from google import cloud
from google.cloud import bigquery

from google.appengine.ext import ndb
# pylint: enable=g-bad-import-order

from loaner.web_app import constants
from loaner.web_app.backend.clients import bigquery_client
from loaner.web_app.backend.models import bigquery_row_model
from loaner.web_app.backend.models import device_model
from loaner.web_app.backend.testing import loanertest


class BigQueryClientTest(loanertest.TestCase):
  """Tests for BigQueryClient."""

  def setUp(self):
    super(BigQueryClientTest, self).setUp()
    bq_patcher = mock.patch.object(bigquery, 'Client', autospec=True)
    self.addCleanup(bq_patcher.stop)
    self.bq_mock = bq_patcher.start()
    self.dataset = mock.Mock()
    self.table = mock.Mock()
    self.table.schema = []
    self.table.exists.return_value = True
    self.table.insert_data.return_value = None
    self.dataset.table.return_value = self.table
    self.client = bigquery_client.BigQueryClient()
    self.client._dataset = self.dataset

  @mock.patch.object(bigquery_client, 'bigquery')
  @mock.patch.object(
      bigquery_client, '_generate_schema', return_value=mock.Mock())
  def test_initialize_tables(self, mock_schema, _):
    mock_client = bigquery_client.BigQueryClient()
    mock_client._dataset = mock.Mock()

    mock_client.initialize_tables()

    mock_schema.assert_called()
    mock_client._dataset.create.assert_called()
    mock_client._dataset.table.called_with(constants.BIGQUERY_DEVICE_TABLE)
    mock_client._dataset.table.called_with(constants.BIGQUERY_SHELF_TABLE)

  @mock.patch.object(bigquery_client, 'bigquery')
  @mock.patch.object(
      bigquery_client, '_generate_schema', return_value=mock.Mock())
  def test_initialize_tables__dataset_exists(self, mock_schema, unused):
    del unused
    mock_client = bigquery_client.BigQueryClient()
    mock_client._dataset = mock.Mock()
    mock_client._dataset.create.side_effect = cloud.exceptions.Conflict(
        'Already Exists: Dataset Loaner')

    mock_client.initialize_tables()

    mock_schema.assert_called()
    mock_client._dataset.create.assert_called()

  def test_stream_row(self):
    now = datetime.datetime.utcnow()
    test_device = device_model.Device(
        serial_number='abc123', chrome_device_id='123123')
    test_device.put()
    row = bigquery_row_model.BigQueryRow.add(
        test_device, now, loanertest.USER_EMAIL, 'Enroll', 'This is a test')

    self.client.stream_row('Test table', row._to_bq_format())

    self.table.insert_data.called_once()

  def test_stream_row_no_table(self):
    self.table.exists.return_value = False

    self.assertRaises(
        bigquery_client.GetTableError, self.client.stream_row, 'test', None)

  def test_stream_row_bq_errors(self):
    self.table.insert_data.return_value = 'Oh no it exploded'
    now = datetime.datetime.utcnow()
    test_device = device_model.Device(
        serial_number='abc123', chrome_device_id='123123')
    test_device.put()
    row = bigquery_row_model.BigQueryRow.add(
        test_device, now, loanertest.USER_EMAIL, 'Enroll', 'This is a test')

    self.assertRaises(
        bigquery_client.InsertError, self.client.stream_row, 'test',
        row._to_bq_format())

  def test_generate_schema_no_entity(self):
    generated_schema = bigquery_client._generate_schema()

    self.assertEqual(len(generated_schema), 5)
    self.assertIsInstance(generated_schema[0], bigquery.SchemaField)

  def test_generate_schema_entity(self):
    entity_fields = [bigquery.SchemaField('test', 'STRING', 'REQUIRED')]

    generated_schema = bigquery_client._generate_schema(entity_fields)
    self.assertEqual(len(generated_schema), 6)
    self.assertEqual(generated_schema[5].fields[0].name, 'test')

  def test_generate_entity_schema(self):

    class NestedTestModel(ndb.Model):
      nested_string_attribute = ndb.StringProperty()

    class TestModel(ndb.Model):
      string_attribute = ndb.StringProperty()
      integer_attribute = ndb.IntegerProperty()
      boolean_attribute = ndb.BooleanProperty()
      nested_attribute = ndb.StructuredProperty(NestedTestModel)

    nested_schema = [
        bigquery.SchemaField('nested_string_attribute', 'STRING', 'NULLABLE')]
    expected_schema = [
        bigquery.SchemaField('string_attribute', 'STRING', 'NULLABLE'),
        bigquery.SchemaField('integer_attribute', 'INTEGER', 'NULLABLE'),
        bigquery.SchemaField('boolean_attribute', 'BOOLEAN', 'NULLABLE'),
        bigquery.SchemaField(
            'nested_attribute', 'RECORD', 'NULLABLE', fields=nested_schema)
    ]

    schema = bigquery_client._generate_entity_schema(TestModel())

    expected_schema_names = _populate_schema_names(expected_schema)
    schema_names = _populate_schema_names(schema)
    self.assertItemsEqual(expected_schema_names, schema_names)


def _populate_schema_names(schema):
  """Creates a list with the names that are inside of the schema.

  Args:
    schema:

  Returns:
    A list containing the names of the schema.
  """
  names = []
  for name in schema:
    names.append(name.name)
  return names


if __name__ == '__main__':
  loanertest.main()
