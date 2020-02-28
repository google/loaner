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

# Lint as: python3
"""Tests for web_app.backend.api.messages.shared_messages."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from loaner.web_app.backend.api.messages import shared_messages
from absl.testing import absltest


class SharedMessagesPy23MigrationTest(absltest.TestCase):

  def testSortDirectionAscending(self):
    sort_direction_asc = shared_messages.SortDirection(0)
    self.assertEqual(sort_direction_asc.name, 'ASCENDING')

  def testSortDirectionDescending(self):
    sort_direction_desc = shared_messages.SortDirection(1)
    self.assertEqual(sort_direction_desc.name, 'DESCENDING')

  def testSearchExpression(self):
    search_exp = shared_messages.SearchExpression(
        expression='FAKE-EXPRESSION',
        direction=shared_messages.SortDirection(0))
    self.assertEqual(search_exp.expression, 'FAKE-EXPRESSION')
    self.assertEqual(search_exp.direction.name, 'ASCENDING')

  def testSearchRequest(self):
    search_exp = shared_messages.SearchExpression(
        expression='FAKE-EXPRESSION',
        direction=shared_messages.SortDirection(0))

    search_request = shared_messages.SearchRequest(
        query_string='FAKE-QUERY-STRING',
        expressions=[search_exp],
        returned_fields=['FAKE-RETURN'])

    self.assertEqual(search_request.query_string, 'FAKE-QUERY-STRING')
    self.assertListEqual(search_request.returned_fields, ['FAKE-RETURN'])
    self.assertEqual(
        search_request.expressions[0].expression, 'FAKE-EXPRESSION')
    self.assertEqual(
        search_request.expressions[0].direction.name, 'ASCENDING')


if __name__ == '__main__':
  absltest.main()
