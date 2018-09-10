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

"""API endpoint that handles requests related to Devices."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from protorpc import message_types

from google.appengine.api import datastore_errors

import endpoints

from loaner.web_app.backend.api import auth
from loaner.web_app.backend.api import permissions
from loaner.web_app.backend.api import root_api
from loaner.web_app.backend.api import shelf_api
from loaner.web_app.backend.api.messages import device_messages
from loaner.web_app.backend.clients import directory
from loaner.web_app.backend.lib import api_utils
from loaner.web_app.backend.lib import search_utils
from loaner.web_app.backend.lib import user as user_lib
from loaner.web_app.backend.models import config_model
from loaner.web_app.backend.models import device_model
from loaner.web_app.backend.models import user_model


_NO_DEVICE_MSG = (
    'Device could not be found using device_identifier "%s".')
_NO_IDENTIFIERS_MSG = 'No identifier supplied to find device.'
_BAD_URLKEY_MSG = 'No device found because the URL-safe key was invalid: %s'
_LIST_DEVICES_USER_MISMATCH_MSG = (
    'Unable to perform this action because you do not have permission.')
_SHELF_NOT_FOUND_MSG = (
    "Unable to find a shelf for the given device's shelf: %s")


@root_api.ROOT_API.api_class(resource_name='device', path='device')
class DeviceApi(root_api.Service):
  """This class is for the Device API."""

  @auth.method(
      device_messages.DeviceRequest,
      message_types.VoidMessage,
      name='enroll',
      path='enroll',
      http_method='POST',
      permission=permissions.Permissions.MODIFY_DEVICE)
  def enroll(self, request):
    """Enrolls a device in the program."""
    self.check_xsrf_token(self.request_state)
    user_email = user_lib.get_user_email()
    try:
      device_model.Device.enroll(
          asset_tag=request.asset_tag,
          serial_number=request.serial_number,
          user_email=user_email)
    except (
        datastore_errors.BadValueError,
        device_model.DeviceCreationError) as error:
      raise endpoints.BadRequestException(str(error))
    return message_types.VoidMessage()

  @auth.method(
      device_messages.DeviceRequest,
      message_types.VoidMessage,
      name='unenroll',
      path='unenroll',
      http_method='POST',
      permission=permissions.Permissions.MODIFY_DEVICE)
  def unenroll(self, request):
    """Unenrolls a device from the program."""
    self.check_xsrf_token(self.request_state)
    device = _get_device(request)
    user_email = user_lib.get_user_email()
    try:
      device.unenroll(user_email)
    except device_model.FailedToUnenrollError as error:
      raise endpoints.BadRequestException(str(error))
    return message_types.VoidMessage()

  @auth.method(
      device_messages.DeviceRequest,
      message_types.VoidMessage,
      name='unlock',
      path='unlock',
      http_method='POST',
      permission=permissions.Permissions.ADMINISTRATE_LOAN)
  def unlock(self, request):
    """Unlocks a device if it is locked or has been marked as lost."""
    self.check_xsrf_token(self.request_state)
    device = _get_device(request)
    user_email = user_lib.get_user_email()
    try:
      device.unlock(user_email)
    except (
        directory.DirectoryRPCError,
        device_model.UnableToMoveToDefaultOUError) as error:
      raise endpoints.BadRequestException(str(error))
    return message_types.VoidMessage()

  @auth.method(
      device_messages.DeviceRequest,
      message_types.VoidMessage,
      name='auditable',
      path='auditable',
      http_method='POST',
      permission=permissions.Permissions.AUDIT_SHELF)
  def device_audit_check(self, request):
    """Runs prechecks on a device to see if it can be audited."""
    self.check_xsrf_token(self.request_state)
    device = _get_device(request)
    try:
      device.device_audit_check()
    except (
        device_model.DeviceNotEnrolledError,
        device_model.UnableToMoveToShelfError) as err:
      raise endpoints.BadRequestException(str(err))
    return message_types.VoidMessage()

  @auth.method(
      device_messages.DeviceRequest,
      device_messages.Device,
      name='get',
      path='user/get',
      http_method='POST')
  def get_device(self, request):
    """Gets a device using any identifier in device_messages.DeviceRequest."""
    device = _get_device(request)
    if not device.enrolled:
      raise endpoints.BadRequestException(
          device_model.DEVICE_NOT_ENROLLED_MSG % device.identifier)
    user_email = user_lib.get_user_email()
    datastore_user = user_model.User.get_user(user_email)
    if (permissions.Permissions.READ_DEVICES not in
        datastore_user.get_permissions()):
      if device.assigned_user != user_email:
        raise endpoints.UnauthorizedException(
            'You do not have the proper permission to perform this action. '
            'Please contact your IT administrator if you feel like this is in '
            'error.')
    directory_client = directory.DirectoryApiClient(user_email)
    try:
      given_name = directory_client.given_name(user_email)
    except (
        directory.DirectoryRPCError, directory.GivenNameDoesNotExistError):
      given_name = None
    message = api_utils.build_device_message_from_model(
        device, config_model.Config.get('allow_guest_mode'))
    message.given_name = given_name
    return message

  @auth.method(
      device_messages.Device,
      device_messages.ListDevicesResponse,
      name='list',
      path='list',
      http_method='POST',
      permission=permissions.Permissions.READ_DEVICES)
  def list_devices(self, request):
    """Lists all devices based on any device attribute."""
    self.check_xsrf_token(self.request_state)
    if request.page_size <= 0:
      raise endpoints.BadRequestException(
          'The value for page_size must be greater than 0.')
    query, sort_options, returned_fields = (
        search_utils.set_search_query_options(request.query))
    if not query:
      shelf_query = ''
      if request.shelf:
        shelf_urlsafe_key = request.shelf.shelf_request.urlsafe_key
        if not shelf_urlsafe_key:
          shelf_urlsafe_key = shelf_api.get_shelf(
              request.shelf.shelf_request).key.urlsafe()
        request.shelf = None
        shelf_query = ':'.join(('shelf', shelf_urlsafe_key))
      query = search_utils.to_query(request, device_model.Device)
      query = ' '.join((query, shelf_query))

    offset = search_utils.calculate_page_offset(
        page_size=request.page_size, page_number=request.page_number)

    search_results = device_model.Device.search(
        query_string=query, query_limit=request.page_size,
        offset=offset, sort_options=sort_options,
        returned_fields=returned_fields)
    total_pages = search_utils.calculate_total_pages(
        page_size=request.page_size, total_results=search_results.number_found)
    guest_permitted = config_model.Config.get('allow_guest_mode')
    messages = []
    for document in search_results.results:
      message = search_utils.document_to_message(
          document, device_messages.Device())
      message.guest_permitted = guest_permitted
      messages.append(message)

    return device_messages.ListDevicesResponse(
        devices=messages,
        total_results=search_results.number_found,
        total_pages=total_pages)

  @auth.method(
      message_types.VoidMessage,
      device_messages.ListUserDeviceResponse,
      name='user_devices',
      path='user/devices',
      http_method='POST')
  def list_user_devices(self, request):
    """Lists all devices assigned to the user."""
    self.check_xsrf_token(self.request_state)
    user = user_lib.get_user_email()
    guest_permitted = config_model.Config.get('allow_guest_mode')
    device_message_list = []
    for device in device_model.Device.list_by_user(user):
      device_message_list.append(
          api_utils.build_device_message_from_model(device, guest_permitted))
    return device_messages.ListUserDeviceResponse(devices=device_message_list)

  @auth.method(
      device_messages.DeviceRequest,
      message_types.VoidMessage,
      name='enable_guest_mode',
      path='user/enable_guest_mode',
      http_method='POST')
  def enable_guest_mode(self, request):
    """Enables Guest Mode for a given device."""
    self.check_xsrf_token(self.request_state)
    device = _get_device(request)
    user_email = user_lib.get_user_email()
    try:
      device.enable_guest_mode(user_email)
    except device_model.EnableGuestError as err:
      raise endpoints.InternalServerErrorException(str(err))
    except (
        device_model.UnassignedDeviceError,
        device_model.GuestNotAllowedError,
        device_model.UnauthorizedError) as err:
      raise endpoints.UnauthorizedException(str(err))
    else:
      return message_types.VoidMessage()

  @auth.method(
      device_messages.ExtendLoanRequest,
      message_types.VoidMessage,
      name='extend_loan',
      path='user/extend_loan',
      http_method='POST')
  def extend_loan(self, request):
    """Extends the current loan for a given device."""
    self.check_xsrf_token(self.request_state)
    device = _get_device(request.device)
    user_email = user_lib.get_user_email()
    try:
      device.loan_extend(
          extend_date_time=request.extend_date,
          user_email=user_email)
      return message_types.VoidMessage()
    except device_model.ExtendError as err:
      raise endpoints.BadRequestException(str(err))
    except (
        device_model.UnassignedDeviceError,
        device_model.UnauthorizedError)as err:
      raise endpoints.UnauthorizedException(str(err))

  @auth.method(
      device_messages.DamagedRequest,
      message_types.VoidMessage,
      name='mark_damaged',
      path='user/mark_damaged',
      http_method='POST')
  def mark_damaged(self, request):
    """Marks that a device is damaged."""
    self.check_xsrf_token(self.request_state)
    device = _get_device(request.device)
    user_email = user_lib.get_user_email()
    try:
      device.mark_damaged(
          user_email=user_email,
          damaged_reason=request.damaged_reason)
    except device_model.UnauthorizedError as err:
      raise endpoints.UnauthorizedException(str(err))
    return message_types.VoidMessage()

  @auth.method(
      device_messages.DeviceRequest,
      message_types.VoidMessage,
      name='undamaged',
      path='undamaged',
      http_method='POST')
  def mark_undamaged(self, request):
    """Clears a device's damaged state."""
    self.check_xsrf_token(self.request_state)
    device = _get_device(request)
    try:
      device.mark_undamaged(user_email=user_lib.get_user_email())
    except device_model.UnauthorizedError as err:
      raise endpoints.UnauthorizedException(str(err))
    return message_types.VoidMessage()

  @auth.method(
      device_messages.DeviceRequest,
      message_types.VoidMessage,
      name='mark_lost',
      path='user/mark_lost',
      http_method='POST')
  def mark_lost(self, request):
    """Marks that a device is lost."""
    self.check_xsrf_token(self.request_state)
    device = _get_device(request)
    user_email = user_lib.get_user_email()
    try:
      device.mark_lost(user_email=user_email)
    except device_model.UnauthorizedError as err:
      raise endpoints.UnauthorizedException(str(err))
    return message_types.VoidMessage()

  @auth.method(
      device_messages.DeviceRequest,
      message_types.VoidMessage,
      name='mark_pending_return',
      path='user/mark_pending_return',
      http_method='POST')
  def mark_pending_return(self, request):
    """Marks that a device is pending return."""
    self.check_xsrf_token(self.request_state)
    device = _get_device(request)
    user_email = user_lib.get_user_email()
    try:
      device.mark_pending_return(user_email=user_email)
    except (
        device_model.UnassignedDeviceError,
        device_model.UnauthorizedError) as err:
      raise endpoints.UnauthorizedException(str(err))
    return message_types.VoidMessage()

  @auth.method(
      device_messages.DeviceRequest,
      message_types.VoidMessage,
      name='resume_loan',
      path='user/resume_loan',
      http_method='POST')
  def resume_loan(self, request):
    """Resumes a loan for a given device."""
    self.check_xsrf_token(self.request_state)
    device = _get_device(request)
    user_email = user_lib.get_user_email()
    try:
      device.resume_loan(user_email=user_email)
    except device_model.UnauthorizedError as err:
      raise endpoints.UnauthorizedException(str(err))
    return message_types.VoidMessage()


def _get_identifier_from_request(device_request):
  """Parses the DeviceMessage for an identifier to use to get a Device entity.

  Args:
    device_request: device_messages.DeviceRequest message.

  Returns:
    The name of the usable device identifier as a string.

  Raises:
    endpoints.BadRequestException: if there are no identifiers in DeviceRequest.
  """
  if getattr(device_request, 'urlkey', None):
    return 'urlkey'

  for device_identifier in [
      'asset_tag', 'chrome_device_id', 'serial_number', 'identifier']:
    if getattr(device_request, device_identifier, None):
      return device_identifier
  raise endpoints.BadRequestException(_NO_IDENTIFIERS_MSG)


def _get_device(device_request):
  """Gets a device using any identifier, including identifier.

  If identifier is supplied, this will try it as both asset_tag and
  serial_number.

  Args:
    device_request: device_messages.DeviceRequest message.

  Returns:
    A device model, or None if one could not be found.

  Raises:
    endpoints.BadRequestException: if a supplied URL-safe key is invalid.
    endpoints.NotFoundException: if there is no such device, or there was an
        exception in getting the device.
  """
  device_identifier = _get_identifier_from_request(device_request)

  if device_identifier == 'urlkey':
    device = api_utils.get_ndb_key(device_request.urlkey).get()
  else:
    device = device_model.Device.get(
        **{device_identifier: getattr(device_request, device_identifier)})
  if not device:
    raise endpoints.NotFoundException(
        _NO_DEVICE_MSG % getattr(device_request, device_identifier))
  return device
