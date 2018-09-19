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

import sys

from absl.testing import flagsaver
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
  )
  def test_write(self, wrap, text, expected_output):
    with flagsaver.flagsaver(wrap_width=wrap):
      utils.write(text)
      self.assertEqual(sys.stdout.getvalue(), expected_output)

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
        mock_write.assert_called_once_with(expected_message)
      mock_input.assert_called_once_with(expected_prompt)
    self.assertEqual(actual_output, expected_output)

  @parameterized.named_parameters(
      ('No parse attribute', {}),
      ('Invalid parse attribute', InvalidParser()),
  )
  def test_prompt__name_error(self, parser):
    with mock.patch.object(utils, 'input'):
      with self.assertRaises(NameError):
        utils.prompt('', None, None, parser)

  def test_prompt__value_error(self):
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
  )
  def test_yes_no_parser(self, need_full, user_input, expected_return):
    parser = utils.YesNoParser(need_full)
    self.assertEqual(parser.parse(user_input), expected_return)
    self.assertEqual(repr(parser), '<YesNoParser({})>'.format(need_full))

  @parameterized.parameters('Y', 'n', 'v', 'YEAH')
  def test_yes_no_parser_errors(self, user_input):
    parser = utils.YesNoParser(True)
    with self.assertRaises(ValueError):
      parser.parse(user_input)


if __name__ == '__main__':
  absltest.main()
