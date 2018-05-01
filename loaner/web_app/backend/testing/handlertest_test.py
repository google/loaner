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

"""Tests for backend.testing.handlertest."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import mock

from loaner.web_app.backend.clients import directory  # pylint: disable=unused-import
from loaner.web_app.backend.testing import handlertest


class HandlerTestCaseTest(handlertest.HandlerTestCase):
  """Test the test loanertest HandlerTestCase methods."""

  def test_handler_testapp_HTTP200(self):
    with mock.patch(
        '__main__.directory.DirectoryApiClient'):
      response = self.testapp.get(r'/')
    self.assertEqual(response.status_int, 302)
    response = self.testapp.get(r'/bootstrap/setup')
    self.assertEqual(response.status_int, 200)


if __name__ == '__main__':
  handlertest.main()
