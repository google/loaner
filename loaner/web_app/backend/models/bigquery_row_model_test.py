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

import mock

from loaner.web_app.backend.models import bigquery_row_model
from loaner.web_app.backend.models import shelf_model
from loaner.web_app.backend.testing import loanertest


class BigQueryRowModelTest(loanertest.TestCase):
  """Tests for BigQueryModel class."""

  def setUp(self):
    super(BigQueryRowModelTest, self).setUp()
    test_shelf = shelf_model.Shelf(
        friendly_name='Test', location='Here', capacity=16)
    test_shelf.put()
    self.test_shelf = test_shelf
    mock_bigquery = mock.patch.object(
        bigquery_row_model, 'bigquery_client', autospec=True)
    self.addCleanup(mock_bigquery.stop)
    self.mock_bigquery = mock_bigquery.start()
    self.mock_bigquery_client = mock.Mock()
    self.mock_bigquery.BigQueryClient.return_value = self.mock_bigquery_client

  def test_add(self):
    test_row = bigquery_row_model.BigQueryRow.add(
        self.test_shelf, datetime.datetime.utcnow(),
        'test@{}'.format(loanertest.USER_DOMAIN),
        'test', 'This is a test')

    retrieved_row = test_row.key.get()
    self.assertEqual(retrieved_row.ndb_key, self.test_shelf.key)

  def test_fetch_unstreamed_rows(self):
    test_row = bigquery_row_model.BigQueryRow.add(
        self.test_shelf, datetime.datetime.utcnow(),
        'test@{}'.format(loanertest.USER_DOMAIN),
        'test', 'This is a test')

    self.assertEqual(
        len(bigquery_row_model.BigQueryRow.fetch_unstreamed_rows()), 1)

    test_row.streamed = True
    test_row.put()

    self.assertEqual(
        len(bigquery_row_model.BigQueryRow.fetch_unstreamed_rows()), 0)

  def test_stream(self):
    test_row = bigquery_row_model.BigQueryRow.add(
        self.test_shelf, datetime.datetime.utcnow(),
        'test@{}'.format(loanertest.USER_DOMAIN),
        'test', 'This is a test')
    test_row_dict = test_row.to_json_dict()
    expected_bq_row = (
        test_row_dict['ndb_key'], test_row_dict['timestamp'],
        'test@{}'.format(loanertest.USER_DOMAIN), 'test', 'This is a test',
        test_row_dict['entity'])

    test_row.stream()

    self.mock_bigquery_client.stream_row.assert_called_once_with(
        'Shelf', expected_bq_row)
    self.assertTrue(test_row.streamed)


if __name__ == '__main__':
  loanertest.main()
