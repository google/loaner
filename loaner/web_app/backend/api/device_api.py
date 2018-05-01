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

import datetime
import logging
from protorpc import message_types

from google.appengine.api import datastore_errors

import endpoints

from loaner.web_app.backend.api import auth
from loaner.web_app.backend.api import permissions
from loaner.web_app.backend.api import root_api
from loaner.web_app.backend.api import shelf_api
from loaner.web_app.backend.api.messages import device_message
from loaner.web_app.backend.lib import api_utils
from loaner.web_app.backend.lib import user as user_lib
from loaner.web_app.backend.models import config_model
from loaner.web_app.backend.models import device_model

_NO_DEVICE_MSG = (
    'Device could not be found using device_identifier "%s".')
_NO_IDENTIFIERS_MSG = 'No identifier supplied to find device.'
_BAD_URLKEY_MSG = 'No device found because the URL-safe key was invalid: %s'
_ASSIGNMENT_MISMATCH_MSG = (
    'Unable to perform this action. Device is currently assigned to another '
    'user.')
_LIST_DEVICES_USER_MISMATCH_MSG = (
    'Unable to perform this action because you do not have permission.')
_SHELF_NOT_FOUND_MSG = (
    "Unable to find a shelf for the given device's shelf: %s")


@root_api.ROOT_API.api_class(resource_name='device', path='device')
class DeviceApi(root_api.Service):
  """This class is for the Device API."""

  @auth.method(
      device_message.DeviceRequest,
      message_types.VoidMessage,
      name='enroll',
      path='enroll',
      http_method='POST',
      permission=permissions.Permissions.ENROLL_DEVICE)
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
      device_message.DeviceRequest,
      message_types.VoidMessage,
      name='unenroll',
      path='unenroll',
      http_method='POST',
      permission=permissions.Permissions.UNENROLL_DEVICE)
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
      device_message.DeviceRequest,
      message_types.VoidMessage,
      name='auditable',
      path='auditable',
      http_method='POST',
      permission=permissions.Permissions.DEVICE_AUDIT)
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
      device_message.DeviceRequest,
      device_message.Device,
      name='get',
      path='get',
      http_method='POST',
      permission=permissions.Permissions.GET_DEVICE)
  def get_device(self, request):
    """Gets a device using any identifier in device_message.DeviceRequest."""
    device = _get_device(request)
    last_reminder_message = api_utils.build_reminder_message(
        device.last_reminder)
    next_reminder_message = api_utils.build_reminder_message(
        device.next_reminder)

    guest_enabled, max_extend_date, guest_permitted = get_loan_data(device)
    if device.shelf:
      shelf_message = api_utils.build_shelf_message(device.shelf.get())
    else:
      shelf_message = None

    device = _build_device_message(
        device=device, shelf_message=shelf_message,
        last_reminder_message=last_reminder_message,
        next_reminder_message=next_reminder_message,
        guest_enabled=guest_enabled, max_extend_date=max_extend_date,
        guest_permitted=guest_permitted)
    return device

  @auth.method(
      device_message.Device,
      device_message.ListDevicesResponse,
      name='list',
      path='list',
      http_method='POST',
      permission=permissions.Permissions.LIST_DEVICES)
  def list_devices(self, request):
    """Lists all devices based on any device attribute."""
    self.check_xsrf_token(self.request_state)
    query, sort_options, returned_fields = (
        self.set_search_query_options(request))
    if not query:
      shelf_query = ''
      if request.shelf:
        shelf_urlsafe_key = request.shelf.shelf_request.urlsafe_key
        if not shelf_urlsafe_key:
          shelf_urlsafe_key = shelf_api.get_shelf(
              request.shelf.shelf_request).key.urlsafe()
        request.shelf = None
        shelf_query = ':'.join(('shelf', shelf_urlsafe_key))
      query = self.to_query(request, device_model.Device)
      query = ' '.join((query, shelf_query))

    cursor = self.get_search_cursor(request.page_token)
    search_results = device_model.Device.search(
        query_string=query, query_limit=request.page_size,
        cursor=cursor, sort_options=sort_options,
        returned_fields=returned_fields)
    new_search_cursor = None
    if search_results.cursor:
      new_search_cursor = search_results.cursor.web_safe_string
    messages = []
    for document in search_results.results:
      message = self.document_to_message(device_message.Device(), document)
      device = _get_device(device_message.DeviceRequest(urlkey=document.doc_id))
      guest_enabled, max_extend_date, guest_permitted = get_loan_data(device)
      message.guest_enabled = guest_enabled
      message.max_extend_date = max_extend_date
      message.guest_permitted = guest_permitted
      message.next_reminder = api_utils.build_reminder_message(
          device.next_reminder)
      message.last_reminder = api_utils.build_reminder_message(
          device.last_reminder)
      messages.append(message)

    return device_message.ListDevicesResponse(
        devices=messages,
        additional_results=bool(new_search_cursor),
        page_token=new_search_cursor)

  @auth.method(
      message_types.VoidMessage,
      device_message.ListUserDeviceResponse,
      name='user_devices',
      path='user_devices',
      http_method='POST',
      permission=permissions.Permissions.LIST_USER_DEVICES,
      allow_assignee=True)
  def list_user_devices(self, request, roles_permitted=None):
    """Lists all devices assigned to the user."""
    del roles_permitted  # Unused, as this is only for assignees.
    self.check_xsrf_token(self.request_state)
    user = user_lib.get_user_email()
    device_messages = []
    for device in device_model.Device.list_by_user(user):
      return_dates = device.calculate_return_dates()
      guest_enabled, max_extend_date, guest_permitted = get_loan_data(device)
      device_messages.append(
          device_message.Device(
              serial_number=device.serial_number,
              asset_tag=device.asset_tag,
              device_model=device.device_model,
              due_date=device.due_date,
              last_heartbeat=device.last_heartbeat,
              assignment_date=device.assignment_date,
              max_extend_date=max_extend_date,
              mark_pending_return_date=device.mark_pending_return_date,
              return_date=return_dates.default,
              guest_enabled=guest_enabled,
              guest_permitted=guest_permitted))
    return device_message.ListUserDeviceResponse(devices=device_messages)

  @auth.method(
      device_message.DeviceRequest,
      message_types.VoidMessage,
      name='enable_guest_mode',
      path='enable_guest_mode',
      http_method='POST',
      permission=permissions.Permissions.ENABLE_GUEST_MODE,
      allow_assignee=True)
  def enable_guest_mode(self, request, roles_permitted=None):
    """Enables Guest Mode for a given device."""
    self.check_xsrf_token(self.request_state)
    device = _get_device(request)
    user_email = user_lib.get_user_email()
    if roles_permitted == ['user']:
      _confirm_assignee_action(user_email, device)
    try:
      device.enable_guest_mode(user_email)
    except device_model.EnableGuestError as err:
      raise endpoints.InternalServerErrorException(str(err))
    except (
        device_model.UnassignedDeviceError,
        device_model.GuestNotAllowedError) as err:
      raise endpoints.UnauthorizedException(str(err))
    else:
      return message_types.VoidMessage()

  @auth.method(
      device_message.ExtendLoanRequest,
      message_types.VoidMessage,
      name='extend_loan',
      path='extend_loan',
      http_method='POST',
      permission=permissions.Permissions.EXTEND_LOAN,
      allow_assignee=True)
  def extend_loan(self, request, roles_permitted=None):
    """Extends the current loan for a given device."""
    self.check_xsrf_token(self.request_state)
    device = _get_device(request.device)
    user_email = user_lib.get_user_email()
    if roles_permitted == ['user']:
      _confirm_assignee_action(user_email, device)
    try:
      device.loan_extend(
          extend_date_time=request.extend_date,
          user_email=user_email)
      return message_types.VoidMessage()
    except device_model.ExtendError as err:
      raise endpoints.BadRequestException(str(err))
    except device_model.UnassignedDeviceError as err:
      raise endpoints.UnauthorizedException(str(err))

  @auth.method(
      device_message.DamagedRequest,
      message_types.VoidMessage,
      name='mark_damaged',
      path='mark_damaged',
      http_method='POST',
      permission=permissions.Permissions.MARK_DAMAGED,
      allow_assignee=True)
  def mark_damaged(self, request, roles_permitted=None):
    """Marks that a device is damaged."""
    self.check_xsrf_token(self.request_state)
    device = _get_device(request.device)
    user_email = user_lib.get_user_email()
    if roles_permitted == ['user']:
      _confirm_assignee_action(user_email, device)
    device.mark_damaged(
        user_email=user_email,
        damaged_reason=request.damaged_reason)
    return message_types.VoidMessage()

  @auth.method(
      device_message.DeviceRequest,
      message_types.VoidMessage,
      name='mark_lost',
      path='mark_lost',
      http_method='POST',
      permission=permissions.Permissions.MARK_LOST,
      allow_assignee=True)
  def mark_lost(self, request, roles_permitted=None):
    """Marks that a device is lost."""
    self.check_xsrf_token(self.request_state)
    device = _get_device(request)
    user_email = user_lib.get_user_email()
    if roles_permitted == ['user']:
      _confirm_assignee_action(user_email, device)
    device.mark_lost(user_email=user_email)
    return message_types.VoidMessage()

  @auth.method(
      device_message.DeviceRequest,
      message_types.VoidMessage,
      name='mark_pending_return',
      path='mark_pending_return',
      http_method='POST',
      permission=permissions.Permissions.MARK_PENDING_RETURN,
      allow_assignee=True)
  def mark_pending_return(self, request, roles_permitted=None):
    """Marks that a device is pending return."""
    self.check_xsrf_token(self.request_state)
    device = _get_device(request)
    user_email = user_lib.get_user_email()
    if roles_permitted == ['user']:
      _confirm_assignee_action(user_email, device)
    try:
      device.mark_pending_return(user_email=user_email)
    except device_model.UnassignedDeviceError as err:
      raise endpoints.UnauthorizedException(str(err))
    return message_types.VoidMessage()

  @auth.method(
      device_message.DeviceRequest,
      message_types.VoidMessage,
      name='resume_loan',
      path='resume_loan',
      http_method='POST',
      permission=permissions.Permissions.RESUME_LOAN,
      allow_assignee=True)
  def resume_loan(self, request, roles_permitted=None):
    """Resumes a loan for a given device."""
    self.check_xsrf_token(self.request_state)
    device = _get_device(request)
    user_email = user_lib.get_user_email()
    if roles_permitted == ['user']:
      _confirm_assignee_action(user_email, device)
    device.resume_loan(user_email=user_email)
    return message_types.VoidMessage()


def _build_device_message(
    device, shelf_message, last_reminder_message, next_reminder_message,
    max_extend_date=None, guest_enabled=None, guest_permitted=None):
  """Builds a device_message.Device message with the passed device's attributes.

  Args:
    device: device_model.Device, an instance of device used to populate the
        ProtoRPC message.
    shelf_message: ProtoRPC message containing a shelf_messages.Shelf.
    last_reminder_message: ProtoRPC message containing a
        device_message.Reminder.
    next_reminder_message: ProtoRPC message containing a
        device_message.Reminder.
    max_extend_date: datetime, Indicates maximum extend date a device can have.
    guest_enabled: bool, Indicates if guest mode has been already enabled.
    guest_permitted: bool, Indicates if guest mode has been allowed.

  Returns:
    A device_message.Device ProtoRPC message.
  """
  message = device_message.Device(
      serial_number=device.serial_number,
      asset_tag=device.asset_tag,
      urlkey=device.key.urlsafe(),
      enrolled=device.enrolled,
      device_model=device.device_model,
      due_date=device.due_date,
      last_known_healthy=device.last_known_healthy,
      shelf=shelf_message,
      assigned_user=device.assigned_user,
      assignment_date=device.assignment_date,
      current_ou=device.current_ou,
      ou_changed_date=device.ou_changed_date,
      locked=device.locked,
      lost=device.lost,
      mark_pending_return_date=device.mark_pending_return_date,
      chrome_device_id=device.chrome_device_id,
      last_heartbeat=device.last_heartbeat,
      damaged=device.damaged,
      damaged_reason=device.damaged_reason,
      last_reminder=last_reminder_message,
      next_reminder=next_reminder_message)

  if device.assigned_user is not None:
    return_dates = device.calculate_return_dates()
    message.return_date = return_dates.default
  if max_extend_date is not None:
    message.max_extend_date = max_extend_date
  if guest_enabled is not None:
    message.guest_enabled = guest_enabled
  if guest_permitted is not None:
    message.guest_permitted = guest_permitted

  return message


def _get_identifier_from_request(device_request):
  """Parses the DeviceMessage for an identifier to use to get a Device entity.

  Args:
    device_request: device_message.DeviceRequest message.

  Returns:
    The name of the usable device identifier as a string.

  Raises:
    endpoints.BadRequestException: if there are no identifiers in DeviceRequest.
  """
  if getattr(device_request, 'urlkey', None):
    return 'urlkey'

  for device_identifier in [
      'asset_tag', 'chrome_device_id', 'serial_number', 'unknown_identifier']:
    if getattr(device_request, device_identifier, None):
      return device_identifier
  raise endpoints.BadRequestException(_NO_IDENTIFIERS_MSG)


def _get_device(device_request):
  """Gets a device using any identifier, including unknown_identifier.

  If unknown_identifier is supplied, this will try it as both asset_tag and
  serial_number.

  Args:
    device_request: device_message.DeviceRequest message.

  Returns:
    A device model, or None if one could not be found.

  Raises:
    endpoints.BadRequestException: if a supplied URL-safe key is invalid.
    endpoints.NotFoundException: if there is no such device, or there was an
        exception in getting the device.
  """
  device_identifier = _get_identifier_from_request(device_request)

  if device_identifier == 'urlkey':
    try:
      device = device_model.Device.get(urlkey=device_request.urlkey)
    except device_model.DeviceIdentifierError as e:
      logging.error(
          'Invalid URL-safe key rased a %s error (key: %s, error: %s).',
          str(type(e)), device_request.urlkey, e)
      raise endpoints.BadRequestException(
          _BAD_URLKEY_MSG % device_request.urlkey)
  else:
    device = device_model.Device.get(
        **{device_identifier: getattr(device_request, device_identifier)})
  if not device:
    raise endpoints.NotFoundException(
        _NO_DEVICE_MSG % getattr(device_request, device_identifier))
  return device


def _confirm_assignee_action(user_email, device):
  """Checks that the user is allowed to perform the action.

  Args:
    user_email: str, the email address of the user taking the action.
    device: device_model.Device, the device used for checking the assigned user.

  Raises:
    endpoints.UnauthorizedException: when the assigned user does not match.
  """
  if device.assigned_user != user_email:
    raise endpoints.UnauthorizedException(_ASSIGNMENT_MISMATCH_MSG)


def get_loan_data(device):
  """Retrieves the data from the device model regarding a loan.

  Args:
    device: device_model.Device, the device that the method will extract data
        related to particular loan.

  Returns:
    A tuple of: (Guest already enabled for this loan, max_extend_date, guest
        permitted to this application)
  """
  guest_enabled = None
  max_extend_date = None
  guest_permitted = None
  if device.is_assigned:
    guest_enabled = device.guest_enabled
    max_extend_date_time, default_date = device.calculate_return_dates()
    del default_date  # Unused.
    max_extend_date = datetime.datetime.combine(
        max_extend_date_time.date(), datetime.datetime.min.time())
    guest_permitted = config_model.Config.get('allow_guest_mode')
  return (guest_enabled, max_extend_date, guest_permitted)
