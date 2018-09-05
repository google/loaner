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

"""Text block widget and helper methods."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import urwid


def code(text):
  """Returns a text fragment (tuple) that will be displayed as code."""
  return ('code', text)


def emphasis(text):
  """Returns a text fragment (tuple) that will be emphasized when displayed."""
  return ('emphasis', text)


def highlight(text):
  """Returns a text fragment (tuple) that will be highlighted to stand out."""
  return ('highlight', text)


def title(text):
  """Returns a text fragment (tuple) that will be used as a title or heading."""
  return ('title', text)


class Block(urwid.Text):
  """A block of text with line wrapping to fill available space.

    |This is what a block of text would look  |
    |like when being rendered in urwid. Lines |
    |are automatically wrapped.               |

  Text fragments support the display attributes found here:
  http://urwid.org/manual/displayattributes.html

  Helper methods are provided above to create common text fragments. e.g.
    new_content = text.Block('Text to display ',
        text.emphasis('emphasized'), ' and ', text.highlight('highlighted'),
        '.')
  """

  def __init__(self, *args):
    """Initializes a new block of text.

    Args:
      *args: text fragments to display within this block.
    """
    super(Block, self).__init__(('text', list(args) or ''))

  @property
  def colors(self):
    return {
        'text': ('black', 'light gray', None, None, None),
        'code': ('dark gray', 'light gray', None, None, None),
        'emphasis': ('black', 'light gray', None, None, None),
        'highlight': ('light gray', 'dark blue', None, None, None),
        'title': ('light blue,bold', 'light gray', None, None, None),
    }

  def set(self, *args):
    """Sets the block's text to the given list of fragments."""
    self.set_text(('text', list(args) or ''))
