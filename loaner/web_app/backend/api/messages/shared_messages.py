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

"""Shared messages for all APIs."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from protorpc import messages


class SortDirection(messages.Enum):
  """SortDirection ProtoRPC message.

  Attributes:
    ASCENDING: enum, The direction for sorting results in ascending order.
    DESCENDING: enum, The direction for sorting results in descending order.
  """
  ASCENDING = 0
  DESCENDING = 1


class SearchExpression(messages.Message):
  """SearchExpression ProtoRPC message.

  Attributes:
    expression: str, An expression to be evaluated when sorting results for each
        matching document such as a search document filed name.
    direction: SortDirection, The direction to sort the search results, either
        ASCENDING or DESCENDING.
  """
  expression = messages.StringField(1, required=True)
  direction = messages.EnumField(SortDirection, 2)


class SearchRequest(messages.Message):
  """SearchRequest ProtoRPC message.

  Attributes:
    query_string: str, A query string to conduct a search on an index.
    expressions: List[SearchExpression], A list representing a multi-dimensional
        sort of Documents.
    returned_fileds: List[str], A list of basestring as facet name to return
        specific facet with the result.
  """
  query_string = messages.StringField(1)
  expressions = messages.MessageField(SearchExpression, 2, repeated=True)
  returned_fields = messages.StringField(3, repeated=True)
