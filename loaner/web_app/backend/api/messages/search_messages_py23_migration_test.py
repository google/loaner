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
"""Tests for web_app.backend.api.messages.search_messages."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from loaner.web_app.backend.api.messages import search_messages
from absl.testing import absltest


class SearchMessagesPy23MigrationTest(absltest.TestCase):

  def testSearchIndexEnumDevice(self):
    search_index_enum = search_messages.SearchIndexEnum(0)
    self.assertEqual(search_index_enum.name, 'DEVICE')

  def testSearchIndexEnumShelf(self):
    search_index_enum = search_messages.SearchIndexEnum(1)
    self.assertEqual(search_index_enum.name, 'SHELF')

  def testSearchMessage(self):
    search_messages_output = search_messages.SearchMessage()
    self.assertTrue(hasattr(search_messages_output, 'model'))


if __name__ == '__main__':
  absltest.main()
