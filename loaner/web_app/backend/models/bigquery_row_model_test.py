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

"""Tests for backend.models.bigquery_row_model."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import datetime

from absl.testing import parameterized
import freezegun
import mock

from google.appengine.ext import ndb

from loaner.web_app import constants
from loaner.web_app.backend.clients import bigquery
from loaner.web_app.backend.models import bigquery_row_model
from loaner.web_app.backend.models import device_model
from loaner.web_app.backend.models import shelf_model
from loaner.web_app.backend.testing import loanertest


class BigQueryRowModelTest(loanertest.TestCase, parameterized.TestCase):
  """Tests for BigQueryModel class."""

  def setUp(self):
    super(BigQueryRowModelTest, self).setUp()

    self.test_shelf = shelf_model.Shelf(
        friendly_name='Test', location='Here', capacity=16)
    self.test_shelf.put()

    self.test_device = device_model.Device(
        serial_number='VOID', enrolled=False,
        device_model='HP Chromebook 13 G1', current_ou='/',
        shelf=self.test_shelf.key, chrome_device_id='unique_id_8',
        damaged=False)
    self.test_device.put()

    self.test_row_1 = bigquery_row_model.BigQueryRow.add(
        self.test_shelf, datetime.datetime.utcnow(),
        'test@{}'.format(loanertest.USER_DOMAIN),
        'test', 'This is a test')

    self.test_row_2 = bigquery_row_model.BigQueryRow.add(
        self.test_device, datetime.datetime.utcnow(),
        'test@{}'.format(loanertest.USER_DOMAIN),
        'test', 'This is a test')

    mock_bigquery = mock.patch.object(
        bigquery_row_model, 'bigquery', autospec=True)
    self.addCleanup(mock_bigquery.stop)
    self.mock_bigquery = mock_bigquery.start()
    self.mock_bigquery_client = mock.Mock()
    self.mock_bigquery.BigQueryClient.return_value = self.mock_bigquery_client

  def test_add(self):
    retrieved_row = self.test_row_1.key.get()
    self.assertEqual(retrieved_row.ndb_key, self.test_shelf.key)

  def test_fetch_unstreamed_rows(self):
    self.assertLen(bigquery_row_model.BigQueryRow._fetch_unstreamed_rows(), 2)
    self.test_row_1.streamed = True
    self.test_row_1.put()
    self.assertLen(bigquery_row_model.BigQueryRow._fetch_unstreamed_rows(), 1)

  @freezegun.freeze_time('1956-01-31')
  def test_time_threshold_reached(self):
    threshold = datetime.datetime.utcnow() - datetime.timedelta(
        minutes=constants.BIGQUERY_ROW_TIME_THRESHOLD)
    self.test_row_1.timestamp = threshold
    self.test_row_1.streamed = False
    self.test_row_1.put()
    self.assertTrue(bigquery_row_model.BigQueryRow._time_threshold_reached())

  @freezegun.freeze_time('1956-01-31')
  def test_time_threshold_reached_fail(self):
    threshold = datetime.datetime.utcnow() - datetime.timedelta(
        minutes=constants.BIGQUERY_ROW_TIME_THRESHOLD - 1)
    self.test_row_1.timestamp = threshold
    self.test_row_1.streamed = False
    self.test_row_1.put()
    self.assertFalse(bigquery_row_model.BigQueryRow._time_threshold_reached())

  def test_row_threshold_reached(self):
    for insert in range(constants.BIGQUERY_ROW_SIZE_THRESHOLD):
      row = bigquery_row_model.BigQueryRow.add(
          self.test_shelf, datetime.datetime.utcnow(),
          'test@{}'.format(loanertest.USER_DOMAIN),
          'test', 'This is a test ' + str(insert))
      row.streamed = False
      row.put()
    self.assertTrue(bigquery_row_model.BigQueryRow._row_threshold_reached())

  def test_row_threshold_reached_fail(self):
    self.test_row_1.streamed = False
    self.test_row_1.put()
    self.assertFalse(bigquery_row_model.BigQueryRow._row_threshold_reached())

  @parameterized.named_parameters(
      ('time', '_time_threshold_reached'),
      ('rows', '_row_threshold_reached'))
  @mock.patch.object(ndb, 'put_multi', autospec=True)
  def test_stream_rows(self, threshold_function, mock_put_multi):
    test_row_dict_1 = self.test_row_1.to_json_dict()
    test_row_dict_2 = self.test_row_2.to_json_dict()
    test_row_1 = (test_row_dict_1['ndb_key'], test_row_dict_1['timestamp'],
                  test_row_dict_1['actor'], test_row_dict_1['method'],
                  test_row_dict_1['summary'], test_row_dict_1['entity'])
    test_row_2 = (test_row_dict_2['ndb_key'], test_row_dict_2['timestamp'],
                  test_row_dict_2['actor'], test_row_dict_2['method'],
                  test_row_dict_2['summary'], test_row_dict_2['entity'])
    expected_tables = {
        self.test_row_1.model_type: [test_row_1],
        self.test_row_2.model_type: [test_row_2]
    }

    with mock.patch.object(
        bigquery_row_model.BigQueryRow,
        threshold_function, return_value=True):
      bigquery_row_model.BigQueryRow.stream_rows()

    self.mock_bigquery_client.stream_table.assert_any_call(
        self.test_row_1.model_type, expected_tables[self.test_row_1.model_type])
    self.mock_bigquery_client.stream_table.assert_any_call(
        self.test_row_2.model_type, expected_tables[self.test_row_2.model_type])
    self.assertEqual(self.mock_bigquery_client.stream_table.call_count, 2)
    self.assertTrue(self.test_row_1.streamed)
    self.assertTrue(self.test_row_2.streamed)
    self.assertEqual(mock_put_multi.call_count, 1)

  def test_stream_rows_insert_error(self):
    self.mock_bigquery_client.stream_table.side_effect = bigquery.InsertError
    with mock.patch.object(
        bigquery_row_model.BigQueryRow,
        'threshold_reached', return_value=True):
      with self.assertRaises(bigquery.InsertError):
        bigquery_row_model.BigQueryRow.stream_rows()

if __name__ == '__main__':
  loanertest.main()
