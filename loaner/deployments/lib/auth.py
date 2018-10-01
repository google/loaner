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

"""This library provides access to oauth."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import json
import os

from absl import flags
from absl import logging

import google_auth_httplib2

from googleapiclient.discovery import build

from oauth2client import client as oauth2_client
from oauth2client import file as client_file
from oauth2client import tools

from google.oauth2 import credentials

FLAGS = flags.FLAGS

flags.DEFINE_bool(
    'automatic_oauth', False,
    'If False (default), authentication will be manual requiring you to paste '
    'the OAuth2 code in the terminal.\n'
    'If True, a local web server will listen at '
    'http://localhost:8080/oauth2callback for the OAuth2 credential.\n'
    'Should you decide to set this to True, please ensure port 8080 is '
    'available and not blocked.',
)
flags.DEFINE_bool(
    'remove_creds', False, 'Set to True to remove credentials from disk.')


class InvalidCredentials(Exception):
  """Raised when we are unable to get valid OAuth2 Credentials."""


class CloudCredentials(object):
  """Google Cloud Authenticated Credentials with an api client generator."""

  def __init__(self, config, scopes):
    """Initializes the OAuth2 flow for user credentials.

    Args:
      config: common.ProjectConfig, the configuration for the Google Cloud
          Project.
      scopes: List[str], a list of the required scopes for this credential.
    """
    self._config = config
    self._credentials = self.get_credentials(scopes)

  def get_api_client(self, service, version, scopes):
    """Gets an authenticated api connection to the provided service and version.

    Args:
      service: str, the name of the service to connect to.
      version: str, the version of the service to connect to.
      scopes: List[str], a list of the required scopes for this api call.

    Returns:
      An authenticated api client connection.
    """
    if not self._credentials.has_scopes(scopes):
      scopes.extend(self._credentials.scopes)
      self._credentials = self.get_credentials(scopes)
    return build(
        serviceName=service, version=version,
        http=google_auth_httplib2.AuthorizedHttp(credentials=self._credentials))

  def get_credentials(self, scopes):
    """Get the user credentials for deployment.

    Args:
      scopes: List[str], a list of the required scopes for this credential.

    Returns:
      A credentials.Credentials object for the authenticated user.
    """
    if os.path.isfile(self._config.local_credentials_file_path):
      creds = self._get_credentials_from_file(scopes)
      if creds:
        return creds
    else:
      logging.info(
          'Credentials were not found locally, requesting new credentials.')
    return self._request_new_credentials(scopes)

  def _get_credentials_from_file(self, scopes):
    """Gets the OAuth2 credential from file if it contains the scopes provided.

    Args:
      scopes: List[str], a list of the required scopes for this credential.

    Returns:
      A credentials.Credentials object for the authenticated user or None if the
          stored credential does not contain the provided scopes.
    """
    with open(
        self._config.local_credentials_file_path, 'r') as json_file:
      data = json.load(json_file)
      if data['scopes'] and set(scopes).issubset(set(data['scopes'])):
        logging.info('The requested scopes are authorized by this credential.')
        return credentials.Credentials.from_authorized_user_info(data, scopes)
      else:
        logging.info(
            'The requested scopes are not authorized by this credential. '
            'Requesting new credentials...')
    return None

  def _request_new_credentials(self, scopes):
    """Create the user credentials without a local webserver.

    Args:
      scopes: List[str], a list of the required scopes for this credential.

    Returns:
      An instance of credentials.Credentials for the authenticated user.

    Raises:
      InvalidCredentials: when we are unable to get valid credentials for the
          user.
    """
    redirect = 'urn:ietf:wg:oauth:2.0:oob'
    creds_flags = argparse.ArgumentParser(
        parents=[tools.argparser]).parse_args(['--noauth_local_webserver'])
    if _run_local_web_server_for_auth():
      redirect = 'http://localhost:8080/oauth2callback'
      creds_flags = argparse.ArgumentParser(
          parents=[tools.argparser]).parse_args([
              '--auth_host_port=8080',
              '--auth_host_name=localhost',
          ])
    flow = oauth2_client.OAuth2WebServerFlow(
        client_id=self._config.client_id,
        client_secret=self._config.client_secret,
        scope=scopes,
        redirect_uri=redirect)
    try:
      old_credentials = tools.run_flow(
          flow, client_file.Storage(self._config.local_credentials_file_path),
          creds_flags)
    except oauth2_client.FlowExchangeError as err:
      raise InvalidCredentials(
          'Unable to get valid credentials: {}.'.format(err))

    if _remove_creds() and os.path.isfile(
        self._config.local_credentials_file_path):
      os.remove(self._config.local_credentials_file_path)

    return credentials.Credentials(
        token=old_credentials.access_token,
        refresh_token=old_credentials.refresh_token,
        id_token=old_credentials.id_token,
        token_uri=old_credentials.token_uri,
        client_id=old_credentials.client_id,
        client_secret=old_credentials.client_secret,
        scopes=list(old_credentials.scopes))


def _remove_creds():
  """Whether or not to remove the local credentials file during deployment.

  Returns:
    A bool, True if the credentials should be removed, otherwise False.
  """
  if FLAGS.is_parsed():
    return FLAGS.remove_creds
  return FLAGS['remove_creds'].default


def _run_local_web_server_for_auth():
  """Whether or not to run the local web server for OAuth2.

  Returns:
    A bool, True when the web server should run, otherwise False.
  """
  if FLAGS.is_parsed():
    return FLAGS.automatic_oauth
  return FLAGS['automatic_oauth'].default
