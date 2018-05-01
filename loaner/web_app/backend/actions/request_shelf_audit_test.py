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

"""Tests for backend.actions.request_shelf_audit."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import mock

from loaner.web_app.backend.lib import send_email  # pylint: disable=unused-import
from loaner.web_app.backend.models import shelf_model
from loaner.web_app.backend.testing import loanertest


class RequestShelfAuditTest(loanertest.ActionTestCase):
  """Test the NotifyShelfAuditors Action class."""

  def setUp(self):
    self.testing_action = 'request_shelf_audit'
    super(RequestShelfAuditTest, self).setUp()

  def test_run_no_shelf(self):
    self.assertRaisesRegexp(  # Raises generic because imported != loaded.
        Exception, '.*did not receive a shelf.*', self.action.run)

  @mock.patch('__main__.send_email.send_shelf_audit_email')
  def test_run_success(self, mock_sendshelfauditemail):
    shelf = shelf_model.Shelf.enroll(
        loanertest.USER_EMAIL, 'US-BLD', 24, 'Overlook Hotel', 40.6892534,
        -74.0466891, 1.0, loanertest.USER_EMAIL)

    self.action.run(shelf=shelf)
    mock_sendshelfauditemail.assert_called_with(shelf)
    self.assertTrue(shelf.audit_requested)


if __name__ == '__main__':
  loanertest.main()
