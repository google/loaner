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

"""Streams any unstreamed BigQuery Datastore rows to BigQuery."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import logging
import pickle
import webapp2

from google.appengine.ext import deferred

from loaner.web_app.backend.models import bigquery_row_model


class StreamToBigQueryHandler(webapp2.RequestHandler):
  """Handler to add a row and stream to BigQuery if a threshold is reached."""

  def post(self):
    """Adds a BigQuery row to Datastore and streams it using a deferred task.

    Raises:
      deferred.PermanentTaskFailure: if we encounter any exception to avoid
        adding duplicate rows during task retries.
    """
    payload = pickle.loads(self.request.body)
    bigquery_row_model.BigQueryRow.add(**payload)
    try:
      if bigquery_row_model.BigQueryRow.threshold_reached():
        deferred.defer(bigquery_row_model.BigQueryRow.stream_rows)
      else:
        logging.info('Not streaming rows, thresholds not met.')
    except Exception as e:  # pylint: disable=broad-except
      raise deferred.PermanentTaskFailure(
          'Exception caught for BigQuery streaming: %s.' % e)
