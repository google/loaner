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

"""Tests for backend.lib.utils."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import datetime
from loaner.web_app.backend.lib import utils
from loaner.web_app.backend.testing import loanertest


class UtilsTest(loanertest.TestCase):
  """Unit tests for loaner minder utils module."""

  def testConvertDatetimeToUnix(self):
    timestamp = datetime.datetime(2016, 8, 1, 1, 1)
    unix_timestamp = utils.datetime_to_unix(timestamp)
    self.assertEqual(unix_timestamp, 1470013260)

  def testConvertDatetimeToUnix_milliseconds(self):
    timestamp = datetime.datetime(2016, 8, 1, 1, 1)
    unix_timestamp = utils.datetime_to_unix(timestamp, True)
    self.assertEqual(unix_timestamp, 1470013260000)

  def test_is_weekend_or_monday(self):
    date = datetime.datetime(2017, 10, 21)  # Saturday.
    self.assertTrue(utils.is_weekend_or_monday(date))

    date = datetime.datetime(2017, 10, 22)  # Sunday.
    self.assertTrue(utils.is_weekend_or_monday(date))

    date = datetime.datetime(2017, 10, 23)  # Monday.
    self.assertTrue(utils.is_weekend_or_monday(date))

    date = datetime.datetime(2017, 10, 20)  # Friday.
    self.assertFalse(utils.is_weekend_or_monday(date))

    date = datetime.datetime(2017, 10, 18)  # Wednesday.
    self.assertFalse(utils.is_weekend_or_monday(date))


if __name__ == '__main__':
  loanertest.main()
