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
from six.moves import input
from six.moves import range

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
    wrapper = textwrap.TextWrapper(
        break_on_hyphens=False,
        break_long_words=False,
        width=_wrap_width())
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


def write_break():
  """Writes a line break followed by a line of '-' and two more line breaks."""
  write('')
  write(''.join(['-' for _ in range(0, _wrap_width(), 1)]))
  write('')


def prompt(message, user_prompt=None, default=None, parser=None):
  """Prompts the user for input.

  Args:
    message: str, the info message to display before prompting for user input.
    user_prompt: str, the prompt to display before input.
    default: str, the default value if no other input is provided.
    parser: Callable, an object to validate and parse the provided input.
        A parser must meet the following requirements:
          1) The object must have a parse() method that accepts a single string
             as input and returns the parsed output.
          2) Any error that occurs during parse() should raise a ValueError to
             indicate bad user input with a helpful error message.
        A working example can be found below as the 'YesNoParser'.

  Returns:
    The user provided input (optionally parsed).

  Raises:
    NameError: when the developer provided parser object does not provide the
        public `parse` method.
  """
  if user_prompt is None:
    user_prompt = '>>>> '

  if default is not None:
    message = '{}\nDefault: {}'.format(message, default)

  while True:
    write(message)
    user_input = input(user_prompt)
    if not user_input and default is not None:
      user_input = default
    if parser is None:
      break
    parse_method = getattr(parser, 'parse', None)
    if parse_method is None or not hasattr(parse_method, '__call__'):
      raise NameError(
          "the object provided as a parser {!r} must have 'parse' as a public "
          'method'.format(parser))
    try:
      user_input = parser.parse(user_input)
    except ValueError as err:
      write("Invalid Response: '{}'\nError: {}\nPlease try again.\n".format(
          user_input, err))
    else:
      break
  return user_input


class YesNoParser(object):
  """A Yes/No parser object."""

  def __init__(self, need_full=False):
    self._need_full = need_full
    self._valid_yes = ('yes',) if need_full else ('y', 'yes')
    self._valid_no = ('no',) if need_full else ('n', 'no')

  def __repr__(self):
    return '<{0}({1})>'.format(self.__class__.__name__, self._need_full)

  def parse(self, arg):
    """Parses and validates the provided argument.

    Args:
      arg: str, the string to be parsed and validated.

    Returns:
      A boolean for whether or not the provided input is valid.

    Raises:
      ValueError: when the provided argument is invalid.
    """
    clean_arg = arg.strip().lower()
    if clean_arg in self._valid_yes:
      return True
    if clean_arg in self._valid_no:
      return False
    raise ValueError("the value {!r} is not a 'yes' or 'no'".format(arg))


class StringParser(object):
  """A string parser object."""

  def __init__(self, allow_empty_string=False):
    self._allow_empty_string = allow_empty_string

  def parse(self, arg):
    """Parses and validates the provided argument.

    Args:
      arg: str, the string to be parsed and validated.

    Returns:
      The parsed string.

    Raises:
      ValueError: when the provided argument is invalid.
    """
    clean_arg = arg.strip()
    if self._allow_empty_string or clean_arg:
      return clean_arg
    raise ValueError('the value {!r} is not a valid string'.format(arg))


def prompt_yes_no(message, need_full=False, **kwargs):
  """Prompt the user for a 'yes' or 'no' as a boolean.

  Args:
    message: str, the info message to display before prompting for user input.
    need_full: bool, whether or not the full word ('yes' or 'no') is required.
    **kwargs: keyword arguments to be passed to prompt.

  Returns:
    True if the user responded with 'yes' and False if 'no'.
  """
  return prompt(message, parser=YesNoParser(need_full=need_full), **kwargs)


def prompt_string(message, allow_empty_string=False, **kwargs):
  """Prompt the user for a string.

  Args:
    message: str, the info message to display before prompting for user input.
    allow_empty_string: bool, whether or not the response is allowed to be an
        empty string.
    **kwargs: keyword arguments to be passed to prompt.

  Returns:
    A user provided string.
  """
  return prompt(message, parser=StringParser(allow_empty_string, **kwargs))


def prompt_int(message, minimum=None, maximum=None, **kwargs):
  """Prompt the user for an integer.

  Args:
    message: str, the info message to display before prompting for user input.
    minimum: int, the minimum accepted value.
    maximum: int, the maximum accepted value.
    **kwargs: keyword arguments to be passed to prompt.

  Returns:
    A user provided int.
  """
  parser = flags.IntegerParser(lower_bound=minimum, upper_bound=maximum)
  return prompt(message, parser=parser, **kwargs)


def prompt_csv(message, **kwargs):
  """Prompt the user for a comma separated list of values.

  Args:
    message: str, the info message to display before prompting for user input.
    **kwargs: keyword arguments to be passed to prompt.

  Returns:
    A user provided list of values.
  """
  return prompt(message, parser=flags.ListParser(), **kwargs)


def prompt_enum(message, accepted_values=None, case_sensitive=True, **kwargs):
  """Prompt the user for a value within an Enum.

  Args:
    message: str, the info message to display before prompting for user input.
    accepted_values: List[Any], a list of accepted values.
    case_sensitive: bool, whether or not validation should require the response
        to be the same case.
    **kwargs: keyword arguments to be passed to prompt.

  Returns:
    A user provided value from within the Enum.
  """
  message += '\nAvailable options are: {}'.format(', '.join(accepted_values))
  parser = flags.EnumParser(
      enum_values=accepted_values, case_sensitive=case_sensitive)
  return prompt(message, parser=parser, **kwargs)
