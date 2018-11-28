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

"""Loaner Search utilities."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import logging
import math

from protorpc import messages

from google.appengine.api import search

from loaner.web_app.backend.api.messages import shared_messages
from loaner.web_app.backend.models import device_model


_CORRUPT_KEY_MSG = 'The key provided for submission was not found.'


def to_query(entity, model_class):
  """Builds a valid query of properties of an NDB model.

  Args:
    entity: An instance of an NDB Model or a ProtoRPC message.
    model_class: NDB model to use for iterating its properties.

  Returns:
    A valid formatted query.
  """
  query = None
  for key in model_class._properties:  # pylint: disable=protected-access
    value = getattr(entity, key, None)
    if value is not None and value != []:  # pylint: disable=g-explicit-bool-comparison
      format_query = ':'.join((key, str(value)))
      try:
        query = ' '.join((query, format_query))
      except TypeError:
        query = format_query
  return query


def document_to_message(document, message):
  """Builds a search document into an ProtoRPC message.

  Args:
    document: search.ScoredDocument, A document from a search result.
    message: messages.Message, a ProtoRPC.messages message to build.

  Returns:
    A constructed ProtoRPC message.
  """
  for field in document.fields:
    if field.name == 'assignment_date':
      setattr(
          message, 'max_extend_date',
          device_model.calculate_return_dates(field.value).max)
    try:
      setattr(message, field.name, field.value)
    except messages.ValidationError:
      if field.value == 'True':
        setattr(message, field.name, True)
      elif field.value == 'False':
        setattr(message, field.name, False)
      elif isinstance(field.value, float):
        setattr(message, field.name, int(field.value))
    except AttributeError:
      if field.name == 'lat_long':
        setattr(message, 'latitude', field.value.latitude)
        setattr(message, 'longitude', field.value.longitude)
      else:
        logging.error('Unable to map %s to any attribute.', field.name)

  return message


def calculate_page_offset(page_size, page_number):
  """Calculates the page offset for a given page size and number.

  Args:
    page_size: int, the size of the amount of items for a page.
    page_number: int, the page number to calculate an offset for.

  Returns:
    The calculated integer value for the offset.
  """
  return (page_number - 1) * page_size


def calculate_total_pages(page_size, total_results):
  """Calculates the number of pages for a given page size and number of results.

  Args:
    page_size: int, the size of the amount of items for a page.
    total_results: int, the number of results.

  Returns:
    The calculated integer value of the total number of pages.
  """
  total_pages = total_results/page_size
  return int(math.ceil(total_pages))


def set_search_query_options(request):
  """Sets the search query options based on a ProtoRPC request message.

  Args:
    request: messages.Message, The message that contains the values of the
        query options.

  Returns:
    A tuple containing the values of query options if they exist in the
        message.
  """
  try:
    query = request.query_string
  except AttributeError:
    query = None

  expressions = []
  sort_options = None
  try:
    for message_expression in request.expressions:
      direction = search.SortExpression.DESCENDING
      if (message_expression.direction ==
          shared_messages.SortDirection.ASCENDING):
        direction = search.SortExpression.ASCENDING
      expressions.append(
          search.SortExpression(
              expression=message_expression.expression, direction=direction))
    if expressions:
      sort_options = search.SortOptions(expressions=expressions)
  except AttributeError:
    # We do not want to so anything if the message does not have expressions
    # since sort_options is already set to None above.
    pass

  try:
    returned_fields = request.returned_fields
  except AttributeError:
    returned_fields = None

  return query, sort_options, returned_fields
