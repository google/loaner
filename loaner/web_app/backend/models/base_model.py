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
from google.appengine.runtime import apiproxy_errors

from loaner.web_app.backend.lib import utils

_PUT_DOC_ERR_MSG = 'Error putting a document (%s) into the index (%s).'
_REMOVE_DOC_ERR_MSG = 'Error removing document with id: %s'
_CREATE_DOC_ERR_MSG = 'Unable to create document for %s.'


class Error(Exception):
  """Base class for exceptions."""


class DocumentCreationError(Error):
  """Raised when search document creation of a model fails."""


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

  @classmethod
  def index_entities_for_search(cls):
    """Indexes all entities of a model for search."""
    page_size = search.MAXIMUM_DOCUMENTS_PER_PUT_REQUEST
    entities, next_cursor, additional_results = (
        cls.query().fetch_page(page_size=page_size, start_cursor=None))
    while True:
      search_documents = []
      for entity in entities:
        try:
          search_documents.append(entity.to_document())
        except DocumentCreationError:
          logging.error(_CREATE_DOC_ERR_MSG, entity.key)
      cls.add_docs_to_index(search_documents)
      if additional_results:
        entities, next_cursor, additional_results = (
            cls.query().fetch_page(
                page_size=page_size, start_cursor=next_cursor))
      else:
        break

  @classmethod
  def get_index(cls):
    """Returns the search Index for a given model."""
    return search.Index(name=cls._INDEX_NAME)

  @classmethod
  def add_docs_to_index(cls, documents):
    """Adds a list of documents to a particular index.

    Args:
      documents: a list of search.Documents to add to the class' index.
    """
    index = cls.get_index()
    for doc in documents:
      try:
        index.put(doc)
      except search.PutError as err:
        result = err.results[0]
        if result.code == search.OperationResult.TRANSIENT_ERROR:
          index.put(doc)
      except (search.Error, apiproxy_errors.OverQuotaError):
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

  @classmethod
  def _to_search_fields(cls, key, value):
    """Converts an ndb.Property into a search document field.

    Args:
      key: str, the name of the field.
      value: ndb.Property, the value to convert.

    Returns:
      A list of search fields created from the specified property. Repeated
          properties will create one field per item.
    """
    if value is None:
      return []

    if isinstance(value, list):
      search_fields = []
      for val in value:
        search_fields.extend(cls._to_search_fields(key, val))
      return search_fields

    if isinstance(value, ndb.Key):
      return [search.AtomField(name=key, value=value.urlsafe())]

    if isinstance(value, (datetime.datetime, datetime.date)):
      return [search.DateField(name=key, value=value)]

    if isinstance(value, bool):
      return [search.AtomField(name=key, value=str(value))]

    if isinstance(value, int) and not isinstance(value, bool):
      return [search.NumberField(name=key, value=value)]

    if isinstance(value, ndb.GeoPt):
      return [search.GeoField(
          name=key, value=search.GeoPoint(value.lat, value.lon))]

    return [search.TextField(name=key, value=unicode(value))]

  def _get_document_fields(self):
    """Enumerates search document fields from entity properties.

    Returns:
      A list of document fields.
    """
    document_fields = []
    for property_name in self._properties:  # pylint: disable=protected-access
      value = getattr(self, property_name)
      document_fields.extend(self._to_search_fields(property_name, value))
    return document_fields

  def to_document(self):
    """Creates a search.Document representation of a model.

    Returns:
      search.Document of the current model to be indexed with a valid doc_id. A
          doc_id will be autogenerated when inserted into the Index if one is
          not provided.

    Raises:
      DocumentCreationError: when unable to create a document for the
          model.
    """
    try:
      return search.Document(
          doc_id=str(self.key.urlsafe()),
          fields=self._get_document_fields())

    except (TypeError, ValueError) as e:
      raise DocumentCreationError(e)


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
