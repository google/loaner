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

"""Tests for web_app.backend.lib.send_email."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import datetime

import mock

from loaner.web_app.backend.lib import send_email
from loaner.web_app.backend.models import device_model
from loaner.web_app.backend.models import shelf_model
from loaner.web_app.backend.testing import loanertest


class EmailTest(loanertest.TestCase):

  def setUp(self):
    super(EmailTest, self).setUp()
    self.default_kwargs = {
        'subject': 'You are for sure a loaner borrower',
        'to': loanertest.USER_EMAIL,
        'body': 'A plain text e-mail.',
        'html': '<blink>A rich HTML e-mail.</blink>'
    }

  @mock.patch('__main__.send_email.mail.send_mail')
  @mock.patch('__main__.send_email.logging.debug')
  @mock.patch('__main__.send_email.logging.error')
  def test_send_email(
      self, mock_logerror, mock_logdebug, mock_gae_sendmail):
    """Test basic email function."""

    # Dev, so we only log.
    send_email.constants.ON_PROD = False
    send_email._send_email(False, **self.default_kwargs)
    assert mock_logdebug.called
    assert not mock_gae_sendmail.called

    # Dev but force send.
    mock_logdebug.reset_mock()
    send_email.constants.ON_PROD = False
    send_email._send_email(True, **self.default_kwargs)
    assert not mock_logdebug.called
    assert mock_gae_sendmail.called

    # Kneel before Prod.
    mock_logdebug.reset_mock()
    mock_gae_sendmail.reset_mock()
    send_email.constants.ON_PROD = True
    send_email._send_email(True, **self.default_kwargs)
    assert mock_gae_sendmail.called

    # Exception raised by GAE's send_mail function.
    send_email.constants.ON_PROD = True
    mock_gae_sendmail.side_effect = send_email.mail.InvalidEmailError
    send_email._send_email(True, **self.default_kwargs)
    assert mock_logerror.called

  @mock.patch('__main__.send_email.logging')
  @mock.patch('__main__.send_email._send_email')
  @mock.patch('__main__.send_email.constants.TEMPLATE_LOADER.render')
  def tests_send_user_email(self, mock_render, mock_sendemail, mock_logging):
    """Test sending mail to users."""
    now = datetime.datetime.utcnow()
    last_week = now - datetime.timedelta(days=7)
    test_device = device_model.Device(
        serial_number='12345ABC',
        chrome_device_id='4815162342',
        assigned_user=loanertest.USER_EMAIL,
        assignment_date=last_week,
        due_date=now)
    test_device.put()
    mock_render.return_value = ('Fake title', 'Fake body.')

    send_email.config_model.Config.set(
        'img_banner_primary', 'https://button.site/banners/primary.png')
    send_email.config_model.Config.set(
        'img_button_manage', 'https://button.site/manage.png')

    send_email.send_user_email(test_device, 'test_reminder_template')
    assert mock_logging.info.called
    assert mock_sendemail.called
    assert mock_render.called

  def tests_send_user_email_bad_device(self):
    """Test sending mail to users with devices with incomplete loan data."""
    now = datetime.datetime.utcnow()
    last_week = now - datetime.timedelta(days=7)
    test_device_no_assigned_user = device_model.Device(
        serial_number='12345ABC',
        chrome_device_id='4815162342',
        assignment_date=last_week,
        due_date=now)
    test_device_no_assignment_date = device_model.Device(
        serial_number='67890DEF',
        chrome_device_id='314159265',
        assigned_user=loanertest.USER_EMAIL,
        due_date=now)
    test_device_no_due_date = device_model.Device(
        serial_number='12345GHI',
        chrome_device_id='35897932',
        assigned_user=loanertest.USER_EMAIL,
        assignment_date=last_week)

    self.assertRaises(
        send_email.SendEmailError, send_email.send_user_email,
        test_device_no_assigned_user, 'test_reminder_template')
    self.assertRaises(
        send_email.SendEmailError, send_email.send_user_email,
        test_device_no_assignment_date, 'test_reminder_template')
    self.assertRaises(
        send_email.SendEmailError, send_email.send_user_email,
        test_device_no_due_date, 'test_reminder_template')

  @mock.patch('__main__.send_email.logging')
  @mock.patch('__main__.send_email._send_email')
  @mock.patch('__main__.send_email.constants.TEMPLATE_LOADER.render')
  def tests_send_shelf_audit_email(
      self, mock_render, mock_sendemail, mock_logging):
    """Test sending mail to users."""
    shelf = shelf_model.Shelf.enroll(
        loanertest.USER_EMAIL, 'US-BLD', 24, 'Overlook Hotel', 40.6892534,
        -74.0466891, 1.0, loanertest.USER_EMAIL)
    shelf.last_audit_time = datetime.datetime.utcnow()
    shelf.put()
    mock_render.return_value = ('Fake title', 'Fake body.')

    send_email.config_model.Config.set(
        'img_banner_primary', 'https://button.site/banners/primary.png')

    send_email.send_shelf_audit_email(shelf, 'shelf_audit_request')
    assert mock_logging.info.called
    assert mock_sendemail.called
    assert mock_render.called

  @mock.patch('__main__.send_email.mail.send_mail')
  def test_force_send(self, mock_gae_sendmail):
    """Tests Dev/Local/QA modification of subject field."""
    send_email.constants.ON_DEV = True
    send_email.constants.ON_LOCAL = False
    send_email.constants.ON_PROD = False
    send_email.constants.ON_QA = False

    # Dev
    send_email._send_email(force_send=True, **self.default_kwargs)

    # Local
    send_email.constants.ON_DEV = False
    send_email.constants.ON_LOCAL = True
    send_email._send_email(force_send=True, **self.default_kwargs)

    # QA
    send_email.constants.ON_LOCAL = False
    send_email.constants.ON_QA = True
    send_email._send_email(force_send=True, **self.default_kwargs)

    expected_calls = [
        mock.call(
            html=self.default_kwargs['html'], body=self.default_kwargs['body'],
            to=self.default_kwargs['to'], sender='noreply@{}'.format(
                loanertest.USER_DOMAIN),
            subject='[dev] You are for sure a loaner borrower'),
        mock.call(
            html=self.default_kwargs['html'], body=self.default_kwargs['body'],
            to=self.default_kwargs['to'], sender='noreply@{}'.format(
                loanertest.USER_DOMAIN),
            subject='[local] You are for sure a loaner borrower'),
        mock.call(
            html=self.default_kwargs['html'], body=self.default_kwargs['body'],
            to=self.default_kwargs['to'], sender='noreply@{}'.format(
                loanertest.USER_DOMAIN),
            subject='[qa] You are for sure a loaner borrower')
    ]

    mock_gae_sendmail.assert_has_calls(expected_calls)


if __name__ == '__main__':
  loanertest.main()
