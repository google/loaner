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

from absl import logging

from google.appengine.ext import ndb

from loaner.web_app.backend.clients import bigquery_client
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
  def fetch_unstreamed_rows(cls):
    """Retrieves all rows that have not been streamed."""
    return cls.query(cls.streamed == False).fetch()  # pylint: disable=g-explicit-bool-comparison,singleton-comparison

  def stream(self):
    """Streams the row to BigQuery."""
    logging.info('Streaming row to table %s', self.model_type)
    bq_client = bigquery_client.BigQueryClient()
    try:
      bq_client.stream_row(self.model_type, self._to_bq_format())
    except bigquery_client.InsertError:
      logging.error('Unable to stream row, see logs.')
      return
    else:
      self._set_streamed()

  def _to_bq_format(self):
    """Converts row model to formatted tuple.

    Returns:
      Tuple of row data.
    """
    entity_dict = self.to_json_dict()
    return (
        entity_dict['ndb_key'], entity_dict['timestamp'],
        entity_dict['actor'], entity_dict['method'], entity_dict['summary'],
        entity_dict['entity'])

  def _set_streamed(self):
    """Sets the row as streamed to BigQuery."""
    self.streamed = True
    self.put()
