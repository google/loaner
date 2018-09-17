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

"""Utility functions for Grab n Go management."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys
import textwrap

from absl import flags

FLAGS = flags.FLAGS

flags.DEFINE_integer('wrap_width', 79, 'The maximum width of wrapped lines')


def _wrap_width():
  """The maximum width of wrapped lines."""
  return FLAGS.wrap_width if FLAGS.is_parsed() else FLAGS['wrap_width'].default


def _wrap_lines(lines, wrapper=None):
  """Wraps a multiline string.

  Args:
    lines: str, a multiline string to wrap.
    wrapper: textwrap.TextWrapper, the wrapper to use for wrapping and
        formatting.

  Returns:
    The formatted string.
  """
  if wrapper is None:
    wrapper = textwrap.TextWrapper(break_long_words=False, width=_wrap_width())
  result = '\n'.join([wrapper.fill(line) for line in lines.splitlines()])
  if lines.endswith('\n'):
    result += '\n'
  return result


def write(message):
  """Writes a message to stdout.

  Args:
    message: str, the message to write to stdout.
  """
  sys.stdout.write(_wrap_lines(message) + '\n')
  sys.stdout.flush()
