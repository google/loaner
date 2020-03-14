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

# Lint as: python3
"""Tests for web_app.backend.lib.utils_py23_migration."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import datetime
from loaner.web_app.backend.lib import utils
from absl.testing import absltest


class UtilsPy23MigrationTest(absltest.TestCase):

  def testConvertDatetimeToUnix(self):
    timestamp = datetime.datetime(2016, 8, 1, 1, 1)
    unix_timestamp = utils.datetime_to_unix(timestamp)
    self.assertEqual(unix_timestamp, 1470013260)

  def testConvertDatetimeToUnix_milliseconds(self):
    timestamp = datetime.datetime(2016, 8, 1, 1, 1)
    unix_timestamp = utils.datetime_to_unix(timestamp, True)
    self.assertEqual(unix_timestamp, 1470013260000)

  def testIsWeekendOrMonday(self):
    date = datetime.datetime(2017, 10, 21)
    self.assertTrue(utils.is_weekend_or_monday(date))

    date = datetime.datetime(2017, 10, 22)
    self.assertTrue(utils.is_weekend_or_monday(date))

    date = datetime.datetime(2017, 10, 23)
    self.assertTrue(utils.is_weekend_or_monday(date))

    date = datetime.datetime(2017, 10, 20)
    self.assertFalse(utils.is_weekend_or_monday(date))

    date = datetime.datetime(2017, 10, 18)
    self.assertFalse(utils.is_weekend_or_monday(date))


if __name__ == '__main__':
  absltest.main()
