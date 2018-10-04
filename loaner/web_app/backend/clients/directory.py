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

"""Directory API library."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


import httplib
import logging

# pylint: disable=unused-import,g-bad-import-order,g-import-not-at-top
from loaner.web_app.backend.common import google_cloud_lib_fixer

import google_auth_httplib2
from googleapiclient import errors
from googleapiclient.discovery import build
from google.oauth2 import service_account

from loaner.web_app import constants


DEVICE_ID = u'deviceId'
MODEL = u'model'
ORG_UNIT_PATH = u'orgUnitPath'
SERIAL_NUMBER = u'serialNumber'
_NEXT_PAGE = 'nextPageToken'

_NO_DEVICE_MSG = 'Device with serial number %s does not exist in the directory.'


class Error(Exception):
  """Base Error class for the Directory API Client."""


class UnauthorizedUserError(Error):
  """Raised when the user provided is not authorized for access."""


class DirectoryRPCError(Error):
  """Raised when a directory api call fails."""


class DeviceDoesNotExistError(Error):
  """Raised when a device does not exist in the Directory API."""


class DeviceAlreadyDisabledError(Error):
  """Raised when trying to disable a device that is already disabled."""


class GivenNameDoesNotExistError(Error):
  """Rasied when a given name does not exist for a user."""


class DirectoryApiClient(object):
  """Directory service instance."""

  def __init__(self, user_email=None):
    self._client = self._create_directory_service(user_email)

  def _create_directory_service(self, user_email=None):
    """Build and return a Google Admin SDK Directory API service object.

    Args:
      user_email: String, The email address of the user that needs permission to
        access the admin APIs.

    Returns:
      Google Admin SDK Directory API service object.

    Raises:
      UnauthorizedUserError: If a user email is not provided.
    """
    if user_email and user_email.split('@')[1] in constants.APP_DOMAINS:
      credentials = service_account.Credentials.from_service_account_file(
          filename=constants.SECRETS_FILE,
          scopes=constants.DIRECTORY_SCOPES,
          subject=constants.ADMIN_EMAIL)

      logging.info('Created delegated credentials for %s.', user_email)
    else:
      raise UnauthorizedUserError('User Email not provided.')

    return build(
        serviceName='admin',
        version='directory_v1',
        http=google_auth_httplib2.AuthorizedHttp(credentials=credentials))

  def get_chrome_device(self, device_id):
    """Query for a Chrome device inside of an organization by deviceId.

    Args:
      device_id: String, The unique ID of the Chrome device.

    Returns:
      A dictionary based on a JSON object of kind
        admin#directory#chromeosdevice. For reference: https://goo.gl/8mQbXD

    Raises:
      DirectoryRPCError: An error when the RPC call to the directory API fails.
    """
    try:
      return self._client.chromeosdevices().get(
          customerId=constants.CUSTOMER_ID,
          deviceId=device_id,
          fields=constants.CHROME_FIELDS_MASK).execute()
    except errors.HttpError as err:
      if err.resp.status == httplib.NOT_FOUND:
        return None
      else:
        logging.error(
            'Directory API get Chrome device failed with a %s exception '
            'because %s.', str(type(err)), err.resp.reason)
        raise DirectoryRPCError(err.resp.reason)

  def get_chrome_device_by_serial(self, serial_number):
    """Query for a Chrome device inside of an organization by serial number.

    Args:
      serial_number: String, The unique serial number of the Chrome device.

    Returns:
      A dictionary based on a JSON object of kind
        admin#directory#chromeosdevice. For reference: https://goo.gl/8mQbXD

    Raises:
      DirectoryRPCError: An error when the RPC call to the directory API fails.
    """
    try:
      return self._client.chromeosdevices().list(
          customerId=constants.CUSTOMER_ID,
          maxResults=1,
          query='id:' + serial_number,
          fields=constants.CHROME_LIST_FIELDS_MASK).execute()[
              'chromeosdevices'][0]
    except errors.HttpError as err:
      logging.error(
          'Directory API get Chrome device failed with a %s exception '
          'because %s.', str(type(err)), err.resp.reason)
      raise DirectoryRPCError(err.resp.reason)
    except KeyError:
      logging.error(_NO_DEVICE_MSG, serial_number)
      raise DeviceDoesNotExistError(_NO_DEVICE_MSG % serial_number)

  def get_org_unit(self, org_unit_path):
    """Query for an Organizational Unit inside of an organization by full path.

    Args:
      org_unit_path: String, The full path of an Organizational Unit.

    Returns:
      A dictionary based on a JSON object of kind admin#directory#orgUnits.
        For reference: https://goo.gl/QvZV3E

    Raises:
      DirectoryRPCError: An error when the RPC call to the directory API fails.
    """
    try:
      return self._client.orgunits().get(
          customerId=constants.CUSTOMER_ID,
          orgUnitPath=org_unit_path,
          fields=constants.ORG_UNIT_FIELDS_MASK).execute()
    except errors.HttpError as err:
      if err.resp.status == httplib.NOT_FOUND:
        return None
      else:
        logging.error(
            'Directory API get Organizational Unit failed with a %s exception '
            'because %s.', str(type(err)), err.resp.reason)
        raise DirectoryRPCError(err.resp.reason)

  def insert_org_unit(
      self, name, parent_org_unit_path=None, description=None,
      block_inheritance=False):
    """Query for an Organizational Unit inside of an organization by full path.

    Args:
      name: String, The name of the new Organizational Unit.
      parent_org_unit_path: String, The full path of the Parent Organizational
        Unit.
      description: String, The description of the new Organizational Unit.
      block_inheritance: Boolean, True blocks inheritance from the Parent.

    Returns:
      A dictionary based on a JSON object of kind admin#directory#orgUnits.
        For reference: https://goo.gl/QvZV3E

    Raises:
      DirectoryRPCError: An error when the RPC call to the directory API fails.
    """
    logging.info(
        'Creating new org unit (%s), inside parent (%s).', name,
        parent_org_unit_path)
    try:
      return self._client.orgunits().insert(
          customerId=constants.CUSTOMER_ID,
          body={
              'name': name,
              'parentOrgUnitPath': parent_org_unit_path,
              'description': description,
              'blockInheritance': block_inheritance
          }).execute()
    except errors.HttpError as err:
      logging.error(
          'Directory API get Organizational Unit failed with a %s exception '
          'because %s.', str(type(err)), err.resp.reason)
      raise DirectoryRPCError(err.resp.reason)

  def move_chrome_device_org_unit(self, device_id, org_unit_path):
    """Move a Chrome device into a new Organizational Unit.

    Args:
      device_id: String, The unique Chrome DeviceId.
      org_unit_path: String, The OrgUnitPath for the Organizational Unit to
        which this Chrome device should now belong.

    Raises:
      DirectoryRPCError: An error when the RPC call to the directory API fails.
    """
    # This is here to catch false device ids. The moveDevicesToOu does not fail
    # for devices that do not exist in this organization.
    self.get_chrome_device(device_id)
    logging.info(
        'Moving device with device ID %r to OU %r.', device_id, org_unit_path)
    try:
      self._client.chromeosdevices().moveDevicesToOu(
          customerId=constants.CUSTOMER_ID,
          orgUnitPath=org_unit_path,
          body={
              'deviceIds': [device_id]
          }).execute()
    except errors.HttpError as err:
      logging.error(
          'Directory API move Chrome device Org Unit failed with a %s '
          'exception because %s.', str(type(err)), err.resp.reason)
      raise DirectoryRPCError(err.resp.reason)

  def disable_chrome_device(self, device_id):
    """Disable a Chrome device within an organization.

    Args:
      device_id: String, The unique Chrome device id.

    Raises:
      DirectoryRPCError: An error when the RPC call to the directory API fails.
    """
    logging.info('Disabling chrome device %s.', device_id)
    try:
      self._client.chromeosdevices().action(
          customerId=constants.CUSTOMER_ID,
          resourceId=device_id,
          body={
              'action': 'disable'
          }).execute()
    except errors.HttpError as err:
      if err.resp.status == httplib.PRECONDITION_FAILED:
        raise DeviceAlreadyDisabledError(err.resp.reason)
      logging.error(
          'Directory API call to disable Chrome device failed with a %s '
          'exception because %s.', str(type(err)), err.resp.reason)
      raise DirectoryRPCError(err.resp.reason)

  def reenable_chrome_device(self, device_id):
    """Re-enable a Chrome device within an organization.

    Args:
      device_id: String, The unique Chrome device id.

    Raises:
      DirectoryRPCError: An error when the RPC call to the directory API fails.
    """
    logging.info('Re-enabling chrome device %s.', device_id)
    try:
      self._client.chromeosdevices().action(
          customerId=constants.CUSTOMER_ID,
          resourceId=device_id,
          body={
              'action': 'reenable'
          }).execute()
    except errors.HttpError as err:
      logging.error(
          'Directory API call to reenable Chrome device failed with a %s '
          'exception because %s.', str(type(err)), err.resp.reason)
      raise DirectoryRPCError(err.resp.reason)

  def given_name(self, user_email):
    """Get the given name of a user.

    Args:
      user_email: String, The email address of the user.

    Returns:
      A string containing the given name for a user.

    Raises:
      DirectoryRPCError: An error when the RPC call to the directory API fails.
    """
    try:
      return self._client.users().get(
          userKey=user_email,
          fields=constants.USER_NAME_FIELDS_MASK).execute()['name']['givenName']
    except errors.HttpError as err:
      logging.error(
          'Directory API given_name failed with a %s exception because %s.',
          str(type(err)), err.resp.reason)
      raise DirectoryRPCError(err.resp.reason)
    except KeyError as err:
      logging.info(
          'The given name for this user (%s) does not exist.', user_email)
      raise GivenNameDoesNotExistError(str(err))

  def get_all_users_in_group(self, group_email):
    """Retrieves all of the users in a particular Google Group.

    Args:
      group_email: str, the email address of the group.

    Returns:
      A list of all user's email addresses in the group provided.
    """
    users = []
    response = self._users_in_group(group_email)
    if not response.get(_NEXT_PAGE):
      members = response.get('members')
      if members:
        for member in members:
          users.append(member['email'])
      return users

    while response.get(_NEXT_PAGE):
      for member in response['members']:
        users.append(member['email'])
      response = self._users_in_group(group_email, response.get(_NEXT_PAGE))

    for member in response['members']:
      users.append(member['email'])

    return users

  def _users_in_group(self, group_email, page_token=None):
    """List the users in a group.

    Args:
      group_email: String, The email address of the group for whose users to
        return.
      page_token: String, The optional page token to query for.

    Returns:
      A dictionary based on a JSON object of kind admin#directory#members.
        For reference: https://goo.gl/YXiFq1

    Raises:
      DirectoryRPCError: An error when the RPC call to the directory API fails.
    """
    try:
      return self._client.members().list(
          groupKey=group_email,
          pageToken=page_token,
          fields=constants.GROUP_MEMBER_FIELDS_MASK).execute()
    except errors.HttpError as err:
      logging.error(
          'Directory API group members failed with a %s exception because %s.',
          str(type(err)), err.resp.reason)
      raise DirectoryRPCError(err.resp.reason)
