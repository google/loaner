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
from absl.testing import parameterized
import mock

from google.appengine.ext import deferred

from loaner.web_app.backend.handlers.task import stream_to_bigquery
from loaner.web_app.backend.testing import handlertest


class StreamToBigQueryHandlerTest(
    handlertest.HandlerTestCase, parameterized.TestCase):

  @parameterized.named_parameters(
      ('threshold_reached', True, 1),
      ('threshold_not_reached', False, 0))
  @mock.patch.object(deferred, 'defer', autospec=True)
  @mock.patch.object(stream_to_bigquery.bigquery_row_model, 'BigQueryRow')
  def test_post(
      self, threshold_return, stream_call_count, mock_row_model, mock_defer):
    payload_dict = {'test': 'test'}
    payload = pickle.dumps(payload_dict)
    mock_row_model.threshold_reached.return_value = threshold_return
    response = self.testapp.post(r'/_ah/queue/stream-bq', payload)

    self.assertEqual(response.status_int, 200)
    mock_row_model.add.assert_called_once_with(**payload_dict)
    self.assertEqual(mock_defer.call_count, stream_call_count)

if __name__ == '__main__':
  handlertest.main()
