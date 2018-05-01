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

"""Helper functions for sending email."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import datetime

from absl import logging
import html2text

from google.appengine.api import mail
from loaner.web_app import constants
from loaner.web_app.backend.models import config_model


class Error(Exception):
  """General Error class for this module."""


class SendEmailError(Error):
  """Error raised when we cannot send an e-mail."""


def send_user_email(device, template_name, force_send=False):
  """Sends an email reminder to a Device borrower.

  Args:
    device: device_model.Device object for device, assigned_user, and loan
        details.
    template_name: str, name of the template to get from datastore.
    force_send: bool, if an email should be sent no matter the environment.

  Raises:
    SendEmailError: if the data pertaining to the loan is incomplete.
  """
  if ((not device.assigned_user) or (not device.due_date) or
      (not device.assignment_date)):
    raise SendEmailError(
        'Cannot send reminder e-mail for device with serial {}; '
        'loan data incomplete.'.format(device.serial_number))

  assignment_date = device.assignment_date.strftime('%b %e, %Y')
  due_date = device.due_date.strftime('%b %e, %Y')
  template_dict = {
      'asset_tag': device.asset_tag or '',
      'assignment_date': assignment_date,
      'device_key': device.key.urlsafe(),
      'due_date': due_date,
      'img_banner': config_model.Config.get('img_banner_primary'),
      'img_button_manage': config_model.Config.get('img_button_manage'),
      'origin': constants.ORIGIN,
      'serial_number': device.serial_number or '',
  }
  title, body = constants.TEMPLATE_LOADER.render(template_name, template_dict)
  email_dict = {
      'to': device.assigned_user,
      'subject': title,
      'body': html2text.html2text(body),
      'html': body,
  }
  # We want each different subject to generate a unique hash.
  logging.info('Sending email to %s\nSubject: %s.', device.assigned_user, title)
  _send_email(force_send, **email_dict)


def send_shelf_audit_email(shelf, force_send=False):
  """Sends a shelf audit email.

  Args:
    shelf: shelf_model.Shelf object for location details.
    force_send: bool, if an email should be sent no matter the environment.

  Raises:
    SendEmailError: if the data pertaining to the audit is incomplete.
  """
  timedelta_since_audit = datetime.datetime.utcnow() - shelf.last_audit_time
  template_dict = {
      'friendly_name': shelf.friendly_name,
      'hours_since_audit': int(timedelta_since_audit.total_seconds() / 3600),
      'location': shelf.location,
      'origin': constants.ORIGIN,
  }
  title, body = constants.TEMPLATE_LOADER.render(
      'shelf_audit_request', template_dict)
  email_dict = {
      'to': shelf.responsible_for_audit,
      'subject': title,
      'body': html2text.html2text(body),
      'html': body,
  }
  # We want each different subject to generate a unique hash.
  logging.info(
      'Sending email to %s\nSubject: %s.', shelf.responsible_for_audit, title)
  _send_email(force_send, **email_dict)


def _send_email(force_send, **kwargs):
  """Sends email using App Engine's email API.

  Args:
    force_send: bool, if an email should be sent no matter the environment.
    **kwargs: kwargs for the email api.
  """
  kwargs['sender'] = constants.EMAIL_FROM
  if force_send and not constants.ON_PROD:
    if constants.ON_DEV:
      kwargs['subject'] = '[dev] ' + kwargs['subject']
    elif constants.ON_LOCAL:
      kwargs['subject'] = '[local] ' + kwargs['subject']
    elif constants.ON_QA:
      kwargs['subject'] = '[qa] ' + kwargs['subject']
  if constants.ON_PROD or force_send:
    try:
      mail.send_mail(**kwargs)
    except mail.InvalidEmailError as error:
      logging.error(
          'Email helper failed to send mail due to an error: %s. (Kwargs: %s)',
          error.message, str(kwargs))
  else:
    logging.debug('On dev, not sending email.')
    for key, value in kwargs.iteritems():
      logging.debug('%r: %r', key, value)
