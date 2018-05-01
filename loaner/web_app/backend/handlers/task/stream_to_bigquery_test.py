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

"""Tests for backend.handlers.task.stream_to_bigquery."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import pickle

import mock

from loaner.web_app.backend.handlers.task import stream_to_bigquery  # pylint: disable=unused-import
from loaner.web_app.backend.testing import handlertest


class StreamToBigQueryHandlerTest(handlertest.HandlerTestCase):

  @mock.patch('__main__.stream_to_bigquery.bigquery_row_model.BigQueryRow')
  def test_post(self, mock_row_model):
    payload_dict = {'test': 'test'}
    payload = pickle.dumps(payload_dict)

    response = self.testapp.post(r'/_ah/queue/stream-bq', payload)

    self.assertEqual(response.status_int, 200)
    mock_row_model.add.assert_called_once_with(**payload_dict)


if __name__ == '__main__':
  handlertest.main()
