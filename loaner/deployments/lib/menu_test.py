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

"""Tests for deployments.lib.menu."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from absl.testing import parameterized

from absl.testing import absltest
from loaner.deployments.lib import menu


class _TestMenu(object):
  """This is an object to be used when testing the callback functionality."""

  def __init__(self):
    self._count = 0

  @property
  def count(self):
    return self._count

  def add(self, amount):
    self._count += amount
    return self


class MenuTest(parameterized.TestCase, absltest.TestCase):

  @parameterized.parameters(1, 2, 10)
  def test_option__with_callback(self, amount):
    option = menu.Option('name', 'description', _TestMenu().add)
    self.assertEqual('name', option.name)
    self.assertEqual('description', option.description)
    self.assertEqual(option.callback(amount).count, amount)

  def test_option__without_callback(self):
    no_call_option = menu.Option('null', 'This option has no callback')
    self.assertEqual('null', no_call_option.name)
    self.assertEqual('This option has no callback', no_call_option.description)
    self.assertIsNone(no_call_option.callback)

    self.assertEqual(
        repr(no_call_option),
        '<Option(null, This option has no callback, None)>')
    self.assertEqual(
        no_call_option, menu.Option('null', 'This option has no callback'))
    self.assertNotEqual(no_call_option, menu.Option('OTHER', 'Other option'))


if __name__ == '__main__':
  absltest.main()
