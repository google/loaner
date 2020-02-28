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
"""Tests for web_app.backend.common.google_cloud_lib_fixer."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys
import warnings

import mock
from requests_toolbelt.adapters import appengine

from absl.testing import absltest

from loaner.web_app.backend.common import fake_monotonic


class GoogleCloudLibFixerTest(absltest.TestCase):

  def testGoogleCloudLibFixer(self):
    with mock.patch.object(appengine, 'monkeypatch') as monkeypatch_mock:
      with mock.patch.object(warnings, 'filterwarnings') as filterwarnings_mock:
        # The test subject is imported there as it is a script by nature.
        from loaner.web_app.backend.common import google_cloud_lib_fixer  # pylint: disable=g-import-not-at-top, unused-variable
        monkeypatch_mock.assert_called_once_with()
        filterwarnings_mock.assert_called_once_with(
            'ignore', message=r'urllib3 is using URLFetch.*')
        self.assertEqual(fake_monotonic, sys.modules['monotonic'])


if __name__ == '__main__':
  absltest.main()
