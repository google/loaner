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

"""Grab n Go environment specific constants."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import json

from absl import flags

FLAGS = flags.FLAGS

flags.DEFINE_string(
    'app_name', 'Grab n Go', 'The official display name of the application.')
flags.DEFINE_list(
    'app_domains', [],
    'A list of domains that will be authorized to access the application.')
flags.DEFINE_string('my_customer', 'my_customer', 'The G Suite customer ID.')
flags.DEFINE_string('chrome_client_id', '', 'The Chrome App OAuth2 Client ID.')
flags.DEFINE_string('web_client_id', '', 'The Web App OAuth2 Client ID.')
flags.DEFINE_string(
    'secrets_filepath', '',
    'The path including the name of the file relative to the Bazel WORKSPACE.\n'
    'e.g. For the production project: loaner/web_app/prod-client-secret.json'
)
flags.DEFINE_string(
    'admin_email', '',
    'The email address to use to access the Google Admin SDK Directory API.')
flags.DEFINE_string(
    'send_email_as', '',
    'The email address from which application related emails will come from.')
flags.DEFINE_string(
    'superadmins_group', '',
    'The name of the group for whom to grant super admin privileges to.')


class AppConstants(object):
  """The Grab n Go Application Configuration object."""

  def __init__(
      self, project, app_name, app_domains, my_customer, chrome_client_id,
      web_client_id, secrets_filepath, admin_email, send_email_as,
      superadmins_group):
    """Initializes a new AppConstants object.

    Args:
      project: str, the Google Cloud Project ID for this configuration.
      app_name: str, the display name of the web application.
      app_domains: List[str], a list of G Suite domains (e.g. ['google.com'])
          authorized to access the web application and endpoints APIs.
      my_customer: str, the G Suite customer ID or the generic 'my_customer'.
      chrome_client_id: str, the OAuth2 Client ID for the companion Chrome app.
      web_client_id: str, the OAuth2 Client ID for the web application.
      secrets_filepath: str, the absolute path to the secrets file for the
          Google Admin SDK Directory API role account.
      admin_email: str, the email address for the administrator account
          granting access to the Google Admin SDK Directory API.
      send_email_as: str, the email address for all application emails to come
          from.
      superadmins_group: str, the name of the group for which contains the
          email addresses of the users to be granted super admin access.
    """
    self._project = project
    self._app_name = app_name
    self._app_domains = app_domains
    self._my_customer = my_customer
    self._chrome_client_id = chrome_client_id
    self._web_client_id = web_client_id
    self._secrets_filepath = secrets_filepath
    self._admin_email = admin_email
    self._send_email_as = send_email_as
    self._superadmins_group = superadmins_group

  def __str__(self):
    return '{!r} for project: {!r}'.format(
        self.__class__.__name__, self.project)

  def __repr__(self):
    return '<{0}({1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, {9}, {10})>'.format(
        self.__class__.__name__, self.project, self.app_name, self.app_domains,
        self.my_customer, self.chrome_client_id, self.web_client_id,
        self.secrets_filepath, self.admin_email, self.send_email_as,
        self.superadmins_group)

  def __eq__(self, other):
    return self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not self.__eq__(other)

  @property
  def project(self):
    """Getter for the Google Cloud Project ID."""
    return self._project

  @property
  def app_name(self):
    """Getter for the web application display name."""
    return self._app_name

  @property
  def app_domains(self):
    """Getter for the authorized G Suite domains."""
    return self._app_domains

  @property
  def my_customer(self):
    """Getter for the G Suite customer ID."""
    return self._my_customer

  @property
  def chrome_client_id(self):
    """Getter for the OAuth2 Client ID for the Chrome app."""
    return self._chrome_client_id

  @property
  def web_client_id(self):
    """Getter for the OAuth2 Client ID for the Web app."""
    return self._web_client_id

  @property
  def secrets_filepath(self):
    """Getter for the absolute path to the secrets for the role account."""
    return self._secrets_filepath

  @property
  def admin_email(self):
    """Getter for the admin email address."""
    return self._admin_email

  @property
  def send_email_as(self):
    """Getter for the email address used to send email from."""
    return self._send_email_as

  @property
  def superadmins_group(self):
    """Getter for the super admins group name."""
    return self._superadmins_group

  def to_json(self):
    """Convert the AppConstants object to a json string for storage."""
    return json.dumps({
        'project': self.project,
        'app_name': self.app_name,
        'app_domains': self.app_domains,
        'my_customer': self.my_customer,
        'chrome_client_id': self.chrome_client_id,
        'web_client_id': self.web_client_id,
        'secrets_filepath': self.secrets_filepath,
        'admin_email': self.admin_email,
        'send_email_as': self.send_email_as,
        'superadmins_group': self.superadmins_group,
    })
