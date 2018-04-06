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

"""Base model class for the loaner project."""

import datetime
import inspect
import logging
import pickle
import string

from protorpc import messages

from google.appengine.api import search
from google.appengine.api import taskqueue
from google.appengine.ext import ndb

from loaner.web_app.backend.lib import utils

_PUT_DOC_ERR_MSG = 'Error putting a document (%s) into the index (%s).'
_REMOVE_DOC_ERR_MSG = 'Error removing document with id: %s'


class BaseModel(ndb.Model):  # pylint: disable=too-few-public-methods
  """Base model class for the loaner project."""

  _INDEX_NAME = None
  _SEARCH_ASCII = frozenset(set(string.printable) - set(string.whitespace))

  def stream_to_bq(self, user, summary, timestamp=None):
    """Creates a task to stream an update to BigQuery.

    Args:
      user: string user email of the acting user.
      summary: string summary of the action being performed.
      timestamp: datetime, if not provided current time will be used.
    """
    if not timestamp:
      timestamp = datetime.datetime.utcnow()
    calling_function = inspect.stack()[1][3]
    task_params = {
        'model_instance': self,
        'timestamp': timestamp,
        'actor': user,
        'method': calling_function,
        'summary': summary,
    }
    taskqueue.add(
        queue_name='stream-bq',
        payload=pickle.dumps(task_params),
        target='default')

  def to_json_dict(self):
    """Converts entity to a JSON-friendly dict.

    Returns:
      The entity as a dictionary with only JSON-friendly values.
    """
    return _sanitize_dict(self.to_dict())

  def maintain_search_index(self):
    """Maintains the status of an entity in the search index."""
    raise NotImplementedError

  def is_valid_doc_id(self, doc_id):
    """Validates the doc id.

    Args:
      doc_id: str, the document id to validate.

    Returns:
      True if the id is valid, False if it is not.
    """
    for char in doc_id:
      if char not in self._SEARCH_ASCII:
        return False
    return not doc_id.startswith('!') and not doc_id.startswith('__')

  @classmethod
  def get_index(cls):
    """Returns the search Index for a given model."""
    return search.Index(name=cls._INDEX_NAME)

  @classmethod
  def add_doc_to_index(cls, doc):
    """Adds a doc to a particular index.

    Args:
      doc: search.Document, the document to add to the class' index.
    """
    index = cls.get_index()
    try:
      index.put(doc)
    except search.PutError as err:
      result = err.results[0]
      if result.code == search.OperationResult.TRANSIENT_ERROR:
        index.put(doc)
    except search.Error as err:
      logging.error(_PUT_DOC_ERR_MSG, doc, index)

  @classmethod
  def get_doc_by_id(cls, doc_id):
    """Retrieves a document within an index by id.

    Args:
      doc_id: str, the document id to retrieve.

    Returns:
      The document associated with the provided id.
    """
    return cls.get_index().get(doc_id=doc_id)

  @classmethod
  def remove_doc_by_id(cls, doc_id):
    """Removes a particular doc from the relevant index given it's id.

    Args:
      doc_id: str, the document id to be removed.
    """
    try:
      cls.get_index().delete(doc_id)
    except search.DeleteError:
      logging.error(_REMOVE_DOC_ERR_MSG, doc_id)


def _sanitize_dict(entity_dict):
  """Sanitize select values of an entity-derived dictionary."""
  for key, value in entity_dict.iteritems():
    if isinstance(value, dict):
      entity_dict[key] = _sanitize_dict(value)
    elif isinstance(value, list):
      entity_dict[key] = [_serialize(s_value) for s_value in value]
    else:
      entity_dict[key] = _serialize(value)

  return entity_dict


def _serialize(value):
  """Serializes a complex ndb type.

  Args:
    value: A ndb type to be serialized.

  Returns:
    Value serialized to simple data type such as integer or string.
  """
  if isinstance(value, datetime.datetime):
    return utils.datetime_to_unix(value)
  elif isinstance(value, (ndb.Key, ndb.GeoPt, messages.Enum)):
    return str(value)
  else:
    return value
