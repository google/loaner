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

"""Tests for deployments.lib.util."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import platform
import sys

from absl import flags
from absl.testing import parameterized

import mock

from pyfakefs import mox3_stubout
from six.moves import StringIO

from absl.testing import absltest
from loaner.deployments.lib import utils


class InvalidParser(object):
  """This represents an invalid parser object that has parse as an attribute."""

  def __init__(self):
    self.parse = 'NOT CALLABLE'


class UtilTest(parameterized.TestCase, absltest.TestCase):

  def setUp(self):
    super(UtilTest, self).setUp()
    self.stdout = StringIO()
    self.stubs = mox3_stubout.StubOutForTesting()
    self.stubs.SmartSet(sys, 'stdout', self.stdout)

  def tearDown(self):
    super(UtilTest, self).tearDown()
    self.stubs.UnsetAll()

  @parameterized.parameters(
      (1, 'one', 'one\n'),
      (2, 'two breaks', 'two\nbreaks\n'),
      (3, 'three line breaks', 'three\nline\nbreaks\n'),
      (4, 'four line breaks\n', 'four\nline\nbreaks\n\n'),
      (5, 'in text requires five breaks', 'in\ntext\nrequires\nfive\nbreaks\n'),
      (1, 'this-is-a-long-line-with-hypens-to-ensure-the-wrapper-does-not-break'
       '-lines-with-hypens', 'this-is-a-long-line-with-hypens-to-ensure-the-'
       'wrapper-does-not-break-lines-with-hypens\n'),
  )
  def test_write(self, wrap, text, expected_output):
    with mock.patch.object(flags, 'get_help_width', return_value=wrap):
      utils.write(text)
      self.assertEqual(sys.stdout.getvalue(), expected_output)

  def test_write_break(self):
    with mock.patch.object(utils, 'write') as mock_write:
      utils.write_break()
      self.assertEqual(3, mock_write.call_count)

  @parameterized.parameters('Linux', 'LINUX', ' lInuX  ')
  def test_clear_screen(self, test_system):
    with mock.patch.object(platform, 'system', return_value=test_system):
      with mock.patch.object(utils, 'write') as mock_write:
        utils.clear_screen()
        mock_write.assert_called_once_with('\033[H\033[J')

  @parameterized.named_parameters(
      ('Default args', 'MESSAGE', None, None, None, 'INPUT',
       'MESSAGE', '>>>> ', 'INPUT'),
      ('With a default response', 'MESSAGE', '> ', 'INPUT', None, '',
       'MESSAGE\nDefault: INPUT', '> ', 'INPUT'),
      ('With a parser', 'MESSAGE', '$> ', None, utils.YesNoParser(), 'y',
       'MESSAGE', '$> ', True),
  )
  def test_prompt(
      self, message, prompt, default, parser, user_input,
      expected_message, expected_prompt, expected_output):
    with mock.patch.object(
        utils, 'input', return_value=user_input) as mock_input:
      with mock.patch.object(utils, 'write') as mock_write:
        actual_output = utils.prompt(message, prompt, default, parser)
        mock_write.assert_any_call(expected_message)
        self.assertEqual(mock_write.call_count, 4)
      mock_input.assert_called_once_with(expected_prompt)
    self.assertEqual(actual_output, expected_output)

  @parameterized.named_parameters(
      ('No parse attribute', {}),
      ('Invalid parse attribute', InvalidParser()),
  )
  def test_prompt__invalid_parser(self, parser):
    with mock.patch.object(utils, 'input'):
      with self.assertRaises(NameError):
        utils.prompt('', None, None, parser)

  def test_prompt__invalid_input(self):
    with mock.patch.object(
        utils, 'input', side_effect=['INPUT', 'n']) as mock_input:
      with mock.patch.object(utils, 'write') as mock_write:
        self.assertFalse(utils.prompt('MSG', None, None, utils.YesNoParser()))
        mock_write.assert_any_call(
            "Invalid Response: 'INPUT'\nError: the value 'INPUT' is not a "
            "'yes' or 'no'\nPlease try again.\n")
        self.assertEqual(mock_input.call_count, 2)

  @parameterized.named_parameters(
      ('Short, lower, True', False, 'y', True),
      ('Short, upper, True', False, 'Y', True),
      ('Long, lower, True', True, 'yes', True),
      ('Long, upper, True', True, 'YES', True),
      ('Short, lower, False', False, 'n', False),
      ('Short, upper, False', False, 'N', False),
      ('Long, lower, False', True, 'no', False),
      ('Long, upper, False', True, 'NO', False),
      ('Bool, False', False, False, False),
      ('Bool, True', False, True, True),
  )
  def test_yes_no_parser(self, need_full, user_input, expected_return):
    parser = utils.YesNoParser(need_full)
    self.assertEqual(parser.parse(user_input), expected_return)
    self.assertEqual(repr(parser), '<YesNoParser({})>'.format(need_full))
    self.assertEqual(utils.YesNoParser(need_full), parser)
    self.assertNotEqual(utils.YesNoParser(not need_full), parser)

  @parameterized.parameters('Y', 'n', 'v', 'YEAH')
  def test_yes_no_parser__invalid_input(self, user_input):
    parser = utils.YesNoParser(True)
    with self.assertRaises(ValueError):
      parser.parse(user_input)

  @parameterized.named_parameters(
      ('Empty String Allowed', True, '', ''),
      ('Non-empty String', False, 'this', 'this'),
      ('Excess  whitespace', False, '  that  ', 'that'),
  )
  def test_string_parser(self, allow_empty_string, user_input, expected):
    parser = utils.StringParser(allow_empty_string)
    self.assertEqual(parser.parse(user_input), expected)
    self.assertEqual(utils.StringParser(allow_empty_string), parser)
    self.assertEqual(
        '<StringParser(allow_empty_string={})>'.format(allow_empty_string),
        repr(parser))
    self.assertEqual('StringParser', str(parser))

  def test_string_parser__invalid_input(self):
    parser = utils.StringParser(False)
    with self.assertRaises(ValueError):
      parser.parse('')

  @parameterized.parameters('asdf-1234', 'a1234-asdf-grab-n-go')
  def test_project_id_parser(self, arg):
    parser = utils.ProjectIDParser()
    self.assertEqual(parser.parse(arg), arg)
    self.assertEqual(
        '<RegExParser({!r}, {!r})>'.format(
            utils._PROJECT_ID_REGEX,
            utils._PROJECT_REQUIREMENTS),
        repr(parser))
    self.assertEqual(utils.ProjectIDParser(), parser)

  @parameterized.named_parameters(
      ('Cannot start with number', '1-grab-n-go'),
      ('Cannot start with hyphen', '-grab-n-go'),
      ('Must be more than 5 characters', 'grabn'),
      ('Must be less than 31 characters',
       'grab-n-go-1234567890-qwertyuiop'),
      ('Cannot include other special characters', 'asdf!@#$.?1234'),
  )
  def test_project_id_parser__invalid_input(self, arg):
    parser = utils.ProjectIDParser()
    with self.assertRaises(ValueError):
      parser.parse(arg)

  @parameterized.parameters(
      'NOREPLY@example.com',
      'noreply@this.io',
      'noreply+filtered@this-is-my.blog',
  )
  def test_email_parser(self, arg):
    parser = utils.EmailParser()
    self.assertEqual(parser.parse(arg), arg)
    self.assertEqual(
        '<RegExParser({!r}, {!r})>'.format(
            utils._EMAIL_REGEX, utils._EMAIL_REQUIREMENTS), repr(parser))
    self.assertEqual(utils.EmailParser(), parser)

  @parameterized.parameters(
      '1234-asdf.apps.googleusercontent.com',
      'aslkdjfhaslkdjfh',
      'asdf@kjalhsdjf',
      '',
  )
  def test_email_parser__invalid_input(self, arg):
    parser = utils.EmailParser()
    with self.assertRaises(ValueError):
      parser.parse(arg)

  @parameterized.parameters(
      '1234-asdf.apps.googleusercontent.com',
      '1234123434576-asdkjlahgfkf.apps.googleusercontent.com',
      '1halksjhdf234-asdjkhasdf8972342134f.apps.googleusercontent.com',
      'uhasdf02381234-asjkahsgdkjg872bdf.apps.googleusercontent.com',
  )
  def test_client_id_parser(self, arg):
    parser = utils.ClientIDParser()
    self.assertEqual(parser.parse(arg), arg)
    self.assertEqual(
        '<RegExParser({!r}, {!r})>'.format(
            utils._CLIENT_ID_REGEX, utils._CLIENT_ID_REQUIREMENTS),
        repr(parser))
    self.assertEqual(utils.ClientIDParser(), parser)

  @parameterized.parameters('noreply@example.com', 'asdfiuyhqwer', '1234', '')
  def test_client_id_parser__invalid_input(self, arg):
    parser = utils.ClientIDParser()
    with self.assertRaises(ValueError):
      parser.parse(arg)

  @parameterized.parameters(
      ('user-01-01-01', 'user-01-01-01'),
      ('USER-01-01-01', 'user-01-01-01'),
      ('UsEr-01-01-01', 'user-01-01-01'),
      ('01user-01', '01user-01'),
  )
  def test_version_parser(self, user_input, expected):
    parser = utils.VersionParser()
    self.assertEqual(parser.parse(user_input), expected)

  @parameterized.named_parameters(
      ('Invalid symbol %', '%USER'),
      ('Invalid symbol $', 'user$'),
      ('Invalid symbol ?', 'user?-01'),
      ('Reserved version: default', 'default'),
      ('Reserved version: latest', 'latest'),
      ('Cannot start with ah-', 'ah-user-01'),
  )
  def test_version_parser__invalid(self, user_input):
    parser = utils.VersionParser()
    with self.assertRaises(ValueError):
      parser.parse(user_input)

  @parameterized.named_parameters(
      ('Empty Allowed', True, '', []),
      ('Not Empty Allowed', True, '1,two, this', ['1', 'two', 'this']),
      ('Not Empty Not Allowed', False, 'this,that, the-other',
       ['this', 'that', 'the-other']),
  )
  def test_list_parser(self, allow_empty_list, user_input, expected):
    parser = utils.ListParser(allow_empty_list)
    self.assertEqual(parser.parse(user_input), expected)
    self.assertEqual('ListParser', str(parser))
    self.assertEqual(
        '<ListParser(allow_empty_list={!r})>'.format(allow_empty_list),
        repr(parser))
    self.assertEqual(utils.ListParser(allow_empty_list), parser)
    self.assertNotEqual(utils.ListParser(not allow_empty_list), parser)

  @parameterized.parameters(('',), ([],))
  def test_list_parser__invalid_input(self, arg):
    parser = utils.ListParser(False)
    with self.assertRaises(ValueError):
      parser.parse(arg)

  @parameterized.named_parameters(
      ('Short, upper, True', False, 'Y', True),
      ('Long, lower, True', True, 'yes', True),
      ('Short, lower, False', False, 'n', False),
      ('Long, upper, False', True, 'NO', False),
  )
  def test_prompt_yes_no(self, need_full, user_input, expected):
    with mock.patch.object(utils, 'input', return_value=user_input):
      actual = utils.prompt_yes_no('MESSAGE', need_full)
    self.assertEqual(actual, expected)

  @parameterized.named_parameters(
      ('Empty String Allowed', True, '', ''),
      ('Non-empty String', False, 'this', 'this'),
      ('Excess  whitespace', False, '  that  ', 'that'),
  )
  def test_prompt_string(self, allow_empty_string, user_input, expected):
    with mock.patch.object(utils, 'input', return_value=user_input):
      actual = utils.prompt_string(
          'MESSAGE', allow_empty_string, default=user_input)
    self.assertEqual(actual, expected)

  @parameterized.named_parameters(
      ('30 Chars', 'thisone-1234-is-a-weird-long-1',
       'thisone-1234-is-a-weird-long-1'),
      ('6 Chars', 'that-1', 'that-1'),
      ('Trailing whitespace', ' this-project ', 'this-project'),
  )
  def test_prompt_project_id(self, user_input, expected):
    with mock.patch.object(utils, 'input', return_value=user_input):
      actual = utils.prompt_project_id('MESSAGE', default=user_input)
    self.assertEqual(actual, expected)

  @parameterized.named_parameters(
      ('Too short', 'fail'),
      ('Too long', 'thisStringIsTooLongToBeAValidGCPProjectIDYo'),
      ('Invalid characters', 'asdfasdf%$'),
      ('Must start with letter', '1234asdf1234'),
  )
  def test_prompt_project_id_errors(self, user_input):
    with mock.patch.object(
        utils, 'input', side_effect=[user_input, 'valid-id']) as mock_input:
      response = utils.prompt_project_id('MESSAGE')
    # This call count should be two because when the ValueError is raised the
    # prompt is re-issued and a new input is expected.
    self.assertEqual(mock_input.call_count, 2)
    self.assertEqual(response, 'valid-id')

  @parameterized.named_parameters(
      ('Middle of the bounds', 0, 10, 5, None, 5),
      ('Maximum', 0, 5, None, '5', 5),
      ('Minimum', 0, 5, None, '0', 0),
      ('No Bounds', None, None, None, '100000', 100000),
  )
  def test_prompt_int(self, minimum, maximum, default, user_input, expected):
    with mock.patch.object(utils, 'input', return_value=user_input):
      actual = utils.prompt_int('MESSAGE', minimum, maximum, default=default)
    self.assertEqual(actual, expected)

  @parameterized.named_parameters(
      ('Empty Allowed', True, '', []),
      ('Not Empty Allowed', True, '1,two, this', ['1', 'two', 'this']),
      ('Not Empty Not Allowed', False, 'this,that, the-other',
       ['this', 'that', 'the-other']),
  )
  def test_prompt_csv(self, allow_empty_list, user_input, expected):
    with mock.patch.object(utils, 'input', return_value=user_input):
      actual = utils.prompt_csv('MESSAGE', allow_empty_list=allow_empty_list)
    self.assertEqual(actual, expected)

  @parameterized.named_parameters(
      ('First case insensitive', ['one', 'TWO', 'Three'], False, 'one', 'one'),
      ('Second case insensitive', ['one', 'TWO', 'Three'], False, 'tWo', 'TWO'),
      ('Case Sensitive', ['one', 'TWO', 'Three'], True, 'Three', 'Three'),
  )
  def test_prompt_enum(self, values, case_sensitive, user_input, expected):
    with mock.patch.object(utils, 'input', return_value=user_input):
      actual = utils.prompt_enum(
          'MESSAGE', accepted_values=values, case_sensitive=case_sensitive)
    self.assertEqual(actual, expected)


if __name__ == '__main__':
  absltest.main()
