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

"""Testing utilities."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import StringIO
import sys


def test_stdout(func):
  """Decorator to replace stdout with StringIO for testing.

  Example Usage:
    @test_utils.test_stdout
    def test_output(self):
      sys.stdout.write('this')
      self.assertEqual(sys.stdout.getvalue(), 'this')

  Args:
    func: callable, the function to replace stdout for.

  Returns:
    The wrapped test function.
  """
  def wrapper(*args, **kwargs):
    try:
      new_out = StringIO.StringIO()
      stdout = sys.stdout
      sys.stdout = new_out
      func(*args, **kwargs)
    finally:
      sys.stdout = stdout
  return wrapper
