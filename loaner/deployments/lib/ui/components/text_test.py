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

"""Tests for deployments.lib.ui.components.text."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from absl.testing import absltest
from loaner.deployments.lib.ui.components import text


class TextTest(absltest.TestCase):

  def test_code(self):
    self.assertEqual(('code', 'content'), text.code('content'))

  def test_emphasis(self):
    self.assertEqual(('emphasis', 'content'), text.emphasis('content'))

  def test_highlight(self):
    self.assertEqual(('highlight', 'content'), text.highlight('content'))

  def test_title(self):
    self.assertEqual(('title', 'content'), text.title('content'))

  def test_block(self):
    expected = (
        'Title standard text CODE', [('title', 5), ('text', 15), ('code', 4)])
    block = text.Block(
        text.title('Title'), ' standard text ', text.code('CODE'))
    self.assertEqual(expected, block.get_text())

  def test_block_colors(self):
    block = text.Block()
    expected = ['text', 'code', 'emphasis', 'highlight', 'title']
    self.assertCountEqual(expected, block.colors.keys())

  def test_block_set(self):
    expected = (
        'Title standard text emphasis',
        [('title', 5), ('text', 15), ('emphasis', 8)])
    block = text.Block('Default text')
    block.set(
        text.title('Title'), ' standard text ', text.emphasis('emphasis'))
    self.assertEqual(expected, block.get_text())


if __name__ == '__main__':
  absltest.main()
