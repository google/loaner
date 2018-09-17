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

from absl.testing import absltest
from loaner.deployments.lib import test_utils
from loaner.deployments.lib import utils


class UtilTest(parameterized.TestCase, absltest.TestCase):

  @parameterized.parameters(
      (1, 'one', 'one\n'),
      (2, 'two breaks', 'two\nbreaks\n'),
      (3, 'three line breaks', 'three\nline\nbreaks\n'),
      (4, 'four line breaks\n', 'four\nline\nbreaks\n\n'),
      (5, 'in text requires five breaks', 'in\ntext\nrequires\nfive\nbreaks\n'),
  )
  @test_utils.test_stdout
  def test_write(self, wrap, text, want):
    with flagsaver.flagsaver(wrap_width=wrap):
      utils.write(text)
      self.assertEqual(sys.stdout.getvalue(), want)


if __name__ == '__main__':
  absltest.main()
