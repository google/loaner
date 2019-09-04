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

from absl.testing import parameterized
import mock

from loaner.web_app.backend.lib import send_email
from loaner.web_app.backend.models import config_model
from loaner.web_app.backend.models import shelf_model
from loaner.web_app.backend.testing import loanertest


class RequestShelfAuditTest(parameterized.TestCase, loanertest.ActionTestCase):
  """Test the NotifyShelfAuditors Action class."""

  def setUp(self):
    self.testing_action = 'request_shelf_audit'
    super(RequestShelfAuditTest, self).setUp()

  def test_run_no_shelf(self):
    self.assertRaisesRegexp(  # Raises generic because imported != loaded.
        Exception, '.*did not receive a shelf.*', self.action.run)

  @parameterized.named_parameters(
      {'testcase_name': 'audit_email_sent', 'config_get_return': True,
       'email_call_count': 1,},
      {'testcase_name': 'no_audit_email_sent', 'config_get_return': False,
       'email_call_count': 0,},
  )
  def test_run_success(self, config_get_return, email_call_count):
    shelf = shelf_model.Shelf.enroll(
        loanertest.USER_EMAIL, 'US-BLD', 24, 'Overlook Hotel', 40.6892534,
        -74.0466891, 1.0, loanertest.USER_EMAIL)

    with mock.patch.object(
        config_model.Config, 'get', return_value=config_get_return):
      with mock.patch.object(
          send_email, 'send_shelf_audit_email') as mock_email:
        self.action.run(shelf=shelf)
        self.assertEqual(mock_email.call_count, email_call_count)
        self.assertTrue(shelf.audit_requested)


if __name__ == '__main__':
  loanertest.main()
