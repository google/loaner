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

import platform
import re
import sys
import textwrap

from absl import flags
from six.moves import input
from six.moves import range

# A Google Cloud Project ID must be between 6 and 30 characters, it cannot end
# with a hyphen, it must begin with a letter, and must be all lower case
# letters, numbers, and hyphens.
_PROJECT_ID_REGEX = r'^[a-z][a-z0-9-]{4,28}[a-z0-9]$'
_PROJECT_REQUIREMENTS = (
    'the length must be between 6 and 30 lowercase letters, numbers, and '
    'hyphens. The first character must be a letter. More information can be '
    'found in the resource reference here: https://cloud.google.com'
    '/resource-manager/reference/rest/v1/projects#Project'
)
# An email address must include an `@` and a `.`.
_EMAIL_REGEX = r'[^@]+@[^@]+\.[^@]+'
_EMAIL_REQUIREMENTS = 'an email address must include a `@` and `.`'
# A Google OAuth2 Client ID must be lower case letters, numbers, and hypens
# followed by '.apps.googleusercontent.com'.
_CLIENT_ID_REGEX = r'^[a-z0-9-]+\.apps\.googleusercontent\.com$'
_CLIENT_ID_REQUIREMENTS = (
    'the OAuth2 Client ID must be lowercase letters, numbers, and hypens '
    'followed by `.apps.googleusercontent.com`'
)
# Version specifics can be found here:
# https://cloud.google.com/appengine/docs/standard/python/config/appref
# Characters allowed in the version string.
# Lowercase letters, numbers, and hyphens.
_VERSION_CHARS = frozenset((
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o',
    'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '1', '2', '3', '4',
    '5', '6', '7', '8', '9', '0', '-',
))
# Version strings that are reserved or otherwise not allowed.
_VERSION_BLACKLIST = frozenset(('default', 'latest'))
# Version cannot start with ah-
_VERSION_CANNOT_START_WITH = 'ah-'
# Version requirements string.
_VERSION_REQUIREMENTS = (
    'the version string provided: {!r} does not meet the requirements.\n'
    'The version string can only be composed of lower case letters, numbers, '
    "and hyphens. The strings 'default' and 'latest' are reserved and therefore"
    " not allowed. Finally, the version string may not begin with 'ah-'."
)


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
        width=flags.get_help_width())
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
  write(''.join(['-' for _ in range(0, flags.get_help_width(), 1)]))
  write('')


def clear_screen():
  """Clears the screen of the running system."""
  system = platform.system().strip().lower()
  if system == 'linux':
    write('\033[H\033[J')


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
  write_break()
  return user_input


class Parser(object):
  """A base parser object."""

  def __eq__(self, other):
    return self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not self.__eq__(other)


class YesNoParser(Parser):
  """A Yes/No parser object."""

  def __init__(self, need_full=False):
    self._need_full = need_full
    self._valid_yes = ('yes',) if need_full else ('y', 'yes')
    self._valid_no = ('no',) if need_full else ('n', 'no')

  def __repr__(self):
    return '<{0}({1!r})>'.format(self.__class__.__name__, self._need_full)

  def parse(self, arg):
    """Parses and validates the provided argument.

    Args:
      arg: str, the string to be parsed and validated.

    Returns:
      A boolean for whether or not the provided input is valid.

    Raises:
      ValueError: when the provided argument is invalid.
    """
    if isinstance(arg, bool):
      return arg
    clean_arg = arg.strip().lower()
    if clean_arg in self._valid_yes:
      return True
    if clean_arg in self._valid_no:
      return False
    raise ValueError("the value {!r} is not a 'yes' or 'no'".format(arg))


class StringParser(Parser):
  """A string parser object."""

  def __init__(self, allow_empty_string=False):
    self._allow_empty_string = allow_empty_string

  def __str__(self):
    return self.__class__.__name__

  def __repr__(self):
    return '<{0}(allow_empty_string={1!r})>'.format(
        self.__class__.__name__, self._allow_empty_string)

  def parse(self, arg):
    """Parses and validates the provided argument.

    When overriding this public method in subclasses call self._parse() to
    utilize the string parser.

    Args:
      arg: str, the string to be parsed and validated.

    Returns:
      The parsed string.
    """
    return self._parse(arg)

  def _parse(self, arg):
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


class RegExParser(StringParser):
  """A regular expression parser object."""

  def __init__(self, regex, requirements):
    """Initializes a regular expression parser.

    Args:
      regex: str, the regular expression to use when parsing values.
      requirements: str, the string used to describe the requirements of the
          regular expression in human terms.
    """
    super(RegExParser, self).__init__(False)
    self._regex = regex
    self._requirements = requirements

  def __repr__(self):
    return '<RegExParser({0!r}, {1!r})>'.format(self._regex, self._requirements)

  def parse(self, arg):
    """Parses and validates the provided argument.

    Args:
      arg: str, the string to be parsed and validated.

    Returns:
      The parsed string.

    Raises:
      ValueError: when the provided argument is invalid.
    """
    clean_arg = self._parse(arg)
    matched_arg = re.match(self._regex, clean_arg)
    if matched_arg:
      return matched_arg.string
    raise ValueError(
        'the value provided ({!r}) does not match the requirements: {}'.format(
            arg, self._requirements))


class ProjectIDParser(RegExParser):
  """A Google Cloud Project ID Parser to enforce Google's requirements."""

  def __init__(self):
    super(ProjectIDParser, self).__init__(
        _PROJECT_ID_REGEX, _PROJECT_REQUIREMENTS)


class EmailParser(RegExParser):
  """An email parser object."""

  def __init__(self):
    super(EmailParser, self).__init__(_EMAIL_REGEX, _EMAIL_REQUIREMENTS)


class ClientIDParser(RegExParser):
  """A Google OAuth2 Client ID parser object."""

  def __init__(self):
    super(ClientIDParser, self).__init__(
        _CLIENT_ID_REGEX, _CLIENT_ID_REQUIREMENTS)


class VersionParser(Parser):
  """A parser for the Google App Engine Version string."""

  def parse(self, arg):
    """Parses and validates the provided argument.

    Args:
      arg: str, the version string to parse.

    Returns:
      The valid version string.

    Raises:
      ValueError: if the version string provided does not meet the requirements.
    """
    clean_arg = arg.strip().lower()
    if clean_arg and set(clean_arg).issubset(_VERSION_CHARS):
      if clean_arg not in _VERSION_BLACKLIST:
        if not clean_arg.startswith(_VERSION_CANNOT_START_WITH):
          return clean_arg
    raise ValueError(_VERSION_REQUIREMENTS.format(arg))


class ListParser(flags.ListParser):
  """A list parser object."""

  def __init__(self, allow_empty_list=False):
    super(ListParser, self).__init__()
    self._allow_empty_list = allow_empty_list

  def __str__(self):
    return self.__class__.__name__

  def __repr__(self):
    return '<{0}(allow_empty_list={1!r})>'.format(
        self.__class__.__name__, self._allow_empty_list)

  def __eq__(self, other):
    return self.allow_empty_list == other.allow_empty_list

  def __ne__(self, other):
    return not self.__eq__(other)

  @property
  def allow_empty_list(self):
    return self._allow_empty_list

  def parse(self, arg):
    """Parses and validates the provided argument.

    Args:
      arg: str, the string of comma separated values to be parsed and validated.

    Returns:
      The parsed list.

    Raises:
      ValueError: when the provided argument is invalid.
    """
    if not self._allow_empty_list and not arg:
      raise ValueError('an empty list is not allowed')
    return super(ListParser, self).parse(arg)


def prompt_yes_no(message, need_full=False, **kwargs):
  """Prompts the user for a 'yes' or 'no' as a boolean.

  Args:
    message: str, the info message to display before prompting for user input.
    need_full: bool, whether or not the full word ('yes' or 'no') is required.
    **kwargs: keyword arguments to be passed to prompt.

  Returns:
    True if the user responded with 'yes' and False if 'no'.
  """
  return prompt(message, parser=YesNoParser(need_full=need_full), **kwargs)


def prompt_string(message, allow_empty_string=False, **kwargs):
  """Prompts the user for a string.

  Args:
    message: str, the info message to display before prompting for user input.
    allow_empty_string: bool, whether or not the response is allowed to be an
        empty string.
    **kwargs: keyword arguments to be passed to prompt.

  Returns:
    A user provided string.
  """
  return prompt(message, parser=StringParser(allow_empty_string), **kwargs)


def prompt_project_id(message, **kwargs):
  """Prompts the user for a Google Cloud Project ID.

  Args:
    message: str, the info message to display before prompting for user input.
    **kwargs: keyword arguments to be passed to prompt.

  Returns:
    A user provided Google Cloud Project ID as a string.
  """
  return prompt(message, parser=ProjectIDParser(), **kwargs)


def prompt_int(message, minimum=None, maximum=None, **kwargs):
  """Prompts the user for an integer.

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


def prompt_csv(message, allow_empty_list=False, **kwargs):
  """Prompts the user for a comma separated list of values.

  Args:
    message: str, the info message to display before prompting for user input.
    allow_empty_list: bool, whether or not an empty list is considered a valid
        value.
    **kwargs: keyword arguments to be passed to prompt.

  Returns:
    A user provided list of values.
  """
  return prompt(message, parser=ListParser(allow_empty_list), **kwargs)


def prompt_enum(message, accepted_values=None, case_sensitive=True, **kwargs):
  """Prompts the user for a value within an Enum.

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
