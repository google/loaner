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

"""Tests for backend.handlers.task.process_emails."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import logging
import mock

from google.appengine.api import mail

from loaner.web_app.backend.testing import handlertest


class ReminderTest(handlertest.HandlerTestCase):

  @mock.patch.object(mail, 'send_mail', autospec=True)
  def test_post(self, mock_gae_send_email):
    request = {
        'sender': 'no-reply@example.com',
        'to': 'sample_user',
        'subject': 'Thank you for using Grab and Go!',
        'body': 'Thank you for returning your device.',
    }
    response = self.testapp.post('/_ah/queue/send-email', request)
    self.assertEqual(response.status_int, 200)

    mock_gae_send_email.assert_called_once_with(**request)

  @mock.patch.object(mail, 'send_mail', side_effect=mail.InvalidEmailError)
  @mock.patch.object(logging, 'error')
  def test_post_error(self, mock_logerror, mock_gae_sendmail):
    self.testapp.post('/_ah/queue/send-email', expect_errors=True)
    self.assertTrue(mock_logerror.called)


if __name__ == '__main__':
  handlertest.main()
