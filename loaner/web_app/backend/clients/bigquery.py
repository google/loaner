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

"""Client for interacting with the BigQuery API."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import logging

from loaner.web_app.backend.common import google_cloud_lib_fixer  # pylint: disable=unused-import
# pylint: disable=g-bad-import-order,g-import-not-at-top

from google import cloud
from google.cloud import bigquery

from loaner.web_app import constants
from loaner.web_app.backend.models import device_model
from loaner.web_app.backend.models import shelf_model
from loaner.web_app.backend.models import survey_models

NDB_TO_BIGQUERY_TYPE = {
    'StringProperty': 'STRING',
    'IntegerProperty': 'INTEGER',
    'FloatProperty': 'FLOAT',
    'BooleanProperty': 'BOOLEAN',
    'DateTimeProperty': 'TIMESTAMP',
    'KeyProperty': 'STRING',
    'GeoPtProperty': 'STRING',
}


class Error(Exception):
  """Base error class for this module."""


class GetTableError(Error):
  """Raised when the client fails to retrieve a table."""


class SchemaError(Error):
  """Raised when there is an error generating the schema."""


class SchemaFieldModeError(Error):
  """Raised when there is a mode mismatch between two SchemaField objects."""


class SchemaFieldTypeError(Error):
  """Raised when there is a type mismatch between two SchemaField objects."""


class InsertError(Error):
  """Raised when there's a problem inserting data into BigQuery."""


class BigQueryClient(object):
  """Client that handles BigQuery interactions."""

  def __init__(self):
    if constants.ON_LOCAL:
      return
    self._client = bigquery.Client()
    self._dataset = self._client.dataset(constants.BIGQUERY_DATASET_NAME)

  def initialize_tables(self):
    """Performs first-time setup by creating dataset/tables."""
    if constants.ON_LOCAL:
      logging.debug('On local, not connecting to BQ.')
      return

    logging.info('Beginning BigQuery initialization.')
    try:
      self._dataset.create()
    except cloud.exceptions.Conflict:
      logging.warning(
          'Dataset %s already exists, not creating.', self._dataset.name)
    else:
      logging.info('Dataset %s successfully created.', self._dataset.name)

    self._create_table(constants.BIGQUERY_DEVICE_TABLE, device_model.Device())
    self._create_table(constants.BIGQUERY_SHELF_TABLE, shelf_model.Shelf())
    self._create_table(
        constants.BIGQUERY_SURVEY_TABLE, survey_models.Question())

    logging.info('BigQuery successfully initialized.')

  def _create_table(self, table_name, entity_instance):
    """Creates a BigQuery Table or attempts to update an existing schema.

    Args:
      table_name: str, name of the table to be created or updated.
      entity_instance: an ndb.Model entity instance to base the schema on.
    """
    table = self._dataset.table(table_name)
    entity_schema = _generate_entity_schema(entity_instance)
    table_schema = _generate_schema(entity_schema)
    table.schema = table_schema
    try:
      table.create()
    except cloud.exceptions.Conflict:
      logging.info(
          'Table %s already exists, attempting to update it.', table_name)
      table.reload()
      merged_schema = _merge_schemas(table.schema, table_schema)
      table.patch(schema=merged_schema)
      logging.info('Table %s updated.', table_name)
    else:
      logging.info('Table %s created.', table_name)

  def stream_table(self, table_name, table):
    """Inserts table rows into BigQuery.

      For each row in a given table, we include a row_id, which is derived
      using the BigQueryRow Model metadata, to supply the BigQuery API with an
      'InsertID' to help ensure consistency.

      https://cloud.google.com/bigquery/streaming-data-into-bigquery#dataconsistency

    Args:
      table_name: str, table name to stream to.
      table: List[tuple], rows for the insert request to the BigQuery API.

    Raises:
      GetTableError: if an invalid table is passed in or the table is not
          initialized.
      InsertError: if the insert fails for any reason.
    """
    if constants.ON_LOCAL:
      logging.debug('On local, not connecting to BQ.')
      return

    bq_table = self._dataset.table(table_name)

    if not bq_table.exists():
      raise GetTableError(
          'Table {} does not exist or is not initialized'.format(table))
    bq_table.reload()
    # A row_id is comprised of each row's ndb key, timestamp, actor, and method.
    row_ids = [str(row[:5]) for row in table]
    errors = bq_table.insert_data(table, row_ids=row_ids)
    if errors:
      logging.error('BigQuery insert generated errors.')
      logging.error(errors)
      raise InsertError('BigQuery insert generated errors {}.'.format(errors))


def _generate_entity_schema(entity):
  """Converts an ndb.Model to a BigQuery schema.

  Args:
    entity: ndb.Model, an instance of an ndb.Model.

  Returns:
    A list of bigquery.SchemaField objects.

  Raises:
    SchemaError: if property can not be retrieved from entity.
  """
  schema = []
  for property_name in entity.to_dict().iterkeys():
    ndb_property = entity._properties.get(property_name, None)  # pylint: disable=protected-access
    if not ndb_property:
      raise SchemaError(
          'Unable to retrieve property {name} from entity.'.format(
              name=property_name))

    ndb_type = type(ndb_property).__name__
    field_type = 'REPEATED' if ndb_property._repeated else 'NULLABLE'  # pylint: disable=protected-access
    if ndb_type == 'StructuredProperty':
      nested_entity = getattr(entity, property_name)
      if not nested_entity:
        # Uninstantiated structured properties must be instantiated to be added
        # to the schema.
        try:
          nested_entity = ndb_property._modelclass()  # pylint: disable=protected-access
        except TypeError:
          logging.warning(
              'Could not create instance of %s, skipping.', property_name)
          continue
        generated_schema = _generate_entity_schema(nested_entity)
        schema.append(bigquery.SchemaField(
            property_name, 'RECORD', field_type, fields=generated_schema))
    else:
      bigquery_type = NDB_TO_BIGQUERY_TYPE.get(ndb_type)
      if not bigquery_type:
        logging.warning(
            'Unable to convert %s property to BigQuery type; using string '
            'instead.', property_name)
        schema.append(bigquery.SchemaField(property_name, 'STRING', field_type))
      else:
        schema.append(
            bigquery.SchemaField(property_name, bigquery_type, field_type))

  return schema


def _generate_schema(entity_fields=None):
  """Generates a BigQuery schema.

  Args:
    entity_fields: list of bigquery.SchemaField objects, the fields to include
    in the entity record.

  Returns:
    A list of bigquery.SchemaField objects.
  """
  schema = [
      bigquery.SchemaField(
          'ndb_key', 'STRING', 'REQUIRED',
          description='ndb key of the entity.'),
      bigquery.SchemaField('timestamp', 'TIMESTAMP', 'REQUIRED'),
      bigquery.SchemaField(
          'actor',
          'STRING',
          'REQUIRED',
          description='User performing the action.'),
      bigquery.SchemaField(
          'method',
          'STRING',
          'REQUIRED',
          description='Method performing the action.'),
      bigquery.SchemaField(
          'summary',
          'STRING',
          'REQUIRED',
          description='User generated summary.')
  ]
  if entity_fields:
    schema.append(
        bigquery.SchemaField(
            'entity',
            'RECORD',
            'NULLABLE',
            description='Current attributes of the entity.',
            fields=entity_fields))
  return schema


def _merge_schemas(current_fields, new_fields):
  """Merges two potentially nested bigquery.SchemaField object lists.

  Merges two lists of SchemaField objects, while preserving the nested structure
  and the unique SchemaField objects from both in the resultant schema, as long
  as the mode and field type of each field are consistent during the merge. i.e.
  BigQuery COLUMN deletions or mode, type, and name changes are disallowed.
  https://cloud.google.com/bigquery/docs/manually-changing-schemas

  Args:
    current_fields: Iterable[bigquery.SchemaField], current fields to merge to.
    new_fields: Iterable[bigquery.SchemaField], new fields to merge from.

  Returns:
    List[bigquery.SchemaField], the merged schemas.

  Raises:
    SchemaFieldModeError: if two fields with the same name do not match in mode.
    SchemaFieldTypeError: if two fields with the same name do not match in type.
  """
  if not isinstance(current_fields, list):
    current_fields = list(current_fields)

  current_fields_dict = {field.name: field for field in current_fields}

  for new_field in new_fields:
    current_field = current_fields_dict.get(new_field.name)
    if current_field is None:
      current_fields.append(new_field)

    elif new_field.mode != current_field.mode:
      raise SchemaFieldModeError(
          ('New SchemaField {name!r} with mode {new_mode!r} does not match'
           'current SchemaField with mode {current_mode!r}').format(
               name=new_field.name,
               current_mode=current_field.mode,
               new_mode=new_field.mode))

    elif new_field.field_type != current_field.field_type:
      raise SchemaFieldTypeError(
          ('New SchemaField {name!r} with type {new_type!r} does not match'
           'current SchemaField with type {current_type!r}').format(
               name=new_field.name,
               current_type=current_field.field_type,
               new_type=new_field.field_type))

    elif current_field.fields:
      merged_fields = _merge_schemas(current_field.fields, new_field.fields)
      current_fields.remove(current_field)
      current_fields.append(bigquery.SchemaField(
          current_field.name,
          'RECORD',
          current_field.mode,
          fields=merged_fields))

  return current_fields
