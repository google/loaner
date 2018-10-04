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

"""Tests for deployments.lib.config."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from absl import flags
from absl.testing import flagsaver
from absl.testing import parameterized

import mock

from absl.testing import absltest
from loaner.deployments.lib import app_constants
from loaner.deployments.lib import utils

FLAGS = flags.FLAGS

flags.DEFINE_string('app_constants_test_flag', '', 'Give me a value!')

FLAGS.register_key_flag_for_module(__name__, FLAGS['app_constants_test_flag'])


class AppConstantsTest(parameterized.TestCase, absltest.TestCase):

  def test_get_default_constants(self):
    constants = app_constants.get_default_constants()
    self.assertLen(constants, 7)

  @flagsaver.flagsaver(app_constants_test_flag='valid')
  def test_get_constants_from_flags(self):
    constants = app_constants.get_constants_from_flags(module=__name__)
    self.assertLen(constants, 1)
    self.assertEqual('valid', constants['app_constants_test_flag'].value)

  def test_get_constants_from_flags__not_parsed(self):
    FLAGS.__dict__['__flags_parsed'] = False
    constants = app_constants.get_constants_from_flags(module=__name__)
    FLAGS.__dict__['__flags_parsed'] = True
    self.assertLen(constants, 1)
    self.assertEqual('', constants['app_constants_test_flag'].value)

  @parameterized.parameters(
      ('DEFAULT', None, 'new', 'new'),
      ('', utils.StringParser(True), '', ''),
      ('yes', utils.YesNoParser(), 'no', False),
      ('', utils.ListParser(True), 'this,one', ['this', 'one']),
      ('', utils.StringParser(False), 'asdf', 'asdf'),
      ('1', flags.IntegerParser(), '10', 10),
      ('user@example.com', utils.EmailParser(), 'other@e.co', 'other@e.co'),
  )
  def test_constant_constructor(self, default, parser, new_value, expected):
    test_constant = app_constants.Constant('name', 'message', default, parser)
    self.assertEqual('name: {}'.format(default), str(test_constant))
    self.assertEqual(
        "<Constant('name', 'message', {!r}, {!r})>".format(default, parser),
        repr(test_constant))
    self.assertEqual(
        app_constants.Constant('name', 'message', default, parser),
        test_constant)
    self.assertNotEqual(
        app_constants.Constant('other', 'message', default, parser),
        test_constant)
    test_constant.value = new_value
    self.assertTrue(test_constant.valid)
    self.assertEqual(test_constant.value, expected)

  def test_constant_prompt(self):
    test_constant = app_constants.Constant(
        'name', 'messsage', '', utils.StringParser(False))
    self.assertFalse(test_constant.valid)
    with mock.patch.object(utils, 'prompt', return_value='VALID!'):
      test_constant.prompt()
      self.assertTrue(test_constant.valid)


if __name__ == '__main__':
  absltest.main()
