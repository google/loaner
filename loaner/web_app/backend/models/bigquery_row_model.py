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

"""A model representing a BigQuery row."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import collections
import datetime
import logging

from google.appengine.ext import ndb

from loaner.web_app import constants
from loaner.web_app.backend.clients import bigquery
from loaner.web_app.backend.models import base_model


class BigQueryRow(base_model.BaseModel):
  """Datastore model representing a single row in BigQuery.

  Attributes:
    ndb_key: ndb.key, The key of the ndb entity being streamed to BigQuery.
    model_type: str, the model type being streamed to BigQuery.
    timestamp: datetime, the timestamp of when the action occurred.
    actor: str, the acting user of the action.
    method: str, method name performing the action.
    summary: str, Human-readable summary of what is occurring.
    entity: json, a flattened representation of the entity.
    streamed: bool, indicates if the data was streamed successfully.
  """
  ndb_key = ndb.KeyProperty(required=True)
  model_type = ndb.StringProperty(required=True)
  timestamp = ndb.DateTimeProperty(required=True)
  actor = ndb.StringProperty(required=True)
  method = ndb.StringProperty(required=True)
  summary = ndb.StringProperty(required=True)
  entity = ndb.JsonProperty(required=True)
  streamed = ndb.BooleanProperty(default=False)

  @classmethod
  def add(cls, model_instance, timestamp, actor, method, summary):
    """Adds a row to the queue to be submitted to BigQuery.

    Args:
      model_instance: ndb model, the instance of the affected model.
      timestamp: datetime, a timestamp of when the change occurred.
      actor: str, user performing the action.
      method: str, the method name performing the action.
      summary: str, human-readable summary of what is occurring.

    Returns:
      The created row entity.
    """
    row = cls(
        ndb_key=model_instance.key,
        model_type=type(model_instance).__name__,
        timestamp=timestamp,
        actor=actor,
        method=method,
        summary=summary,
        entity=model_instance.to_json_dict())
    row.put()
    return row

  @classmethod
  def _fetch_unstreamed_rows(cls):
    """Retrieves all rows that have not been streamed."""
    return cls.query(cls.streamed == False).fetch(  # pylint: disable=g-explicit-bool-comparison,singleton-comparison
        limit=constants.BIGQUERY_ROW_MAX_BATCH_SIZE)

  @classmethod
  def _get_last_unstreamed_row(cls):
    """Retrieves the last row that was not streamed."""
    return cls.query(cls.streamed == False).order(  # pylint: disable=g-explicit-bool-comparison,singleton-comparison
        cls.streamed, cls.timestamp).get()

  @classmethod
  def _time_threshold_reached(cls):
    """Checks if the time threshold for a BigQuery stream was met."""
    threshold = datetime.datetime.utcnow() - datetime.timedelta(
        minutes=constants.BIGQUERY_ROW_TIME_THRESHOLD)
    return cls._get_last_unstreamed_row().timestamp <= threshold

  @classmethod
  def _row_threshold_reached(cls):
    """Checks if the unstreamed row threshold for a BigQuery stream was met."""
    return (cls.query(cls.streamed == False).count(  # pylint: disable=g-explicit-bool-comparison,singleton-comparison
        limit=constants.BIGQUERY_ROW_MAX_BATCH_SIZE) >=
            constants.BIGQUERY_ROW_SIZE_THRESHOLD)

  @classmethod
  def threshold_reached(cls):
    """Determines whether or not entities should be streamed to BigQuery."""
    return cls._time_threshold_reached() or cls._row_threshold_reached()

  @classmethod
  def stream_rows(cls):
    """Streams all unstreamed rows if a threshold has been reached."""
    logging.info('Streaming rows to BigQuery.')
    if not cls.threshold_reached():
      logging.info('Not streaming rows, thresholds not met.')
      return
    bq_client = bigquery.BigQueryClient()
    rows = cls._fetch_unstreamed_rows()
    tables = _format_for_bq(rows)
    try:
      for table_name in tables:
        bq_client.stream_table(table_name, tables[table_name])
    except bigquery.InsertError:
      logging.error('Unable to stream rows.')
      return
    _set_streamed(rows)


def _set_streamed(rows):
  """Sets the rows as streamed to BigQuery."""
  for row in rows:
    row.streamed = True
  ndb.put_multi(rows)


def _format_for_bq(rows):
  """Formats BigQueryRow entities and metadata for the BigQuery API.

  Args:
    rows: List[BigQueryRow], a list of rows to format for the BigQuery API.

  Returns:
    A Dictionary keyed by model type with rows for a given table.
  """
  tables = collections.defaultdict(list)
  for row in rows:
    entity_dict = row.to_json_dict()
    tables[row.model_type].append(
        (entity_dict['ndb_key'], entity_dict['timestamp'],
         entity_dict['actor'], entity_dict['method'], entity_dict['summary'],
         entity_dict['entity']))
  return tables
