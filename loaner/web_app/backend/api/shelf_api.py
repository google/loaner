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

"""The entry point for the Shelf methods."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from absl import logging

from protorpc import message_types

from google.appengine.api import datastore_errors

import endpoints

from loaner.web_app.backend.api import auth
from loaner.web_app.backend.api import permissions
from loaner.web_app.backend.api import root_api
from loaner.web_app.backend.api.messages import shelf_messages
from loaner.web_app.backend.lib import api_utils
from loaner.web_app.backend.lib import search_utils
from loaner.web_app.backend.lib import user
from loaner.web_app.backend.models import device_model
from loaner.web_app.backend.models import shelf_model

_SHELF_DOES_NOT_EXIST_MSG = (
    'The shelf with location: %s does not exist. Please double '
    'check the location.')
_DEVICE_DOES_NOT_EXIST_MSG = (
    'The device_identifier: %s is either not enrolled or an invalid serial '
    'number has been entered.')


@root_api.ROOT_API.api_class(resource_name='shelf', path='shelf')
class ShelfApi(root_api.Service):
  """This class is for the Shelf API."""

  @auth.method(
      shelf_messages.EnrollShelfRequest,
      message_types.VoidMessage,
      name='enroll',
      path='enroll',
      http_method='POST',
      permission=permissions.Permissions.MODIFY_SHELF)
  def enroll(self, request):
    """Enrolls a shelf in the program."""
    user_email = user.get_user_email()
    self.check_xsrf_token(self.request_state)
    try:
      shelf_model.Shelf.enroll(
          user_email=user_email,
          friendly_name=request.friendly_name,
          location=request.location,
          latitude=request.latitude,
          longitude=request.longitude,
          altitude=request.altitude,
          capacity=request.capacity,
          audit_notification_enabled=request.audit_notification_enabled,
          responsible_for_audit=request.responsible_for_audit,
          audit_interval_override=request.audit_interval_override,
      )
    except (shelf_model.EnrollmentError, datastore_errors.BadValueError) as err:
      raise endpoints.BadRequestException(str(err))

    return message_types.VoidMessage()

  @auth.method(
      shelf_messages.ShelfRequest,
      shelf_messages.Shelf,
      name='get',
      path='get',
      http_method='POST',
      permission=permissions.Permissions.READ_SHELVES)
  def get(self, request):
    """Gets a shelf based on location."""
    self.check_xsrf_token(self.request_state)
    return api_utils.build_shelf_message_from_model(get_shelf(request))

  @auth.method(
      shelf_messages.ShelfRequest,
      message_types.VoidMessage,
      name='disable',
      path='disable',
      http_method='POST',
      permission=permissions.Permissions.MODIFY_SHELF)
  def disable(self, request):
    """Disables a shelf by its location."""
    self.check_xsrf_token(self.request_state)
    user_email = user.get_user_email()
    shelf = get_shelf(request)
    shelf.disable(user_email)

    return message_types.VoidMessage()

  @auth.method(
      shelf_messages.UpdateShelfRequest,
      message_types.VoidMessage,
      name='update',
      path='update',
      http_method='POST',
      permission=permissions.Permissions.MODIFY_SHELF)
  def update(self, request):
    """Gets a shelf using location to update its properties."""
    self.check_xsrf_token(self.request_state)
    user_email = user.get_user_email()
    shelf = get_shelf(request.shelf_request)
    kwargs = api_utils.to_dict(request, shelf_model.Shelf)
    shelf.edit(user_email=user_email, **kwargs)
    return message_types.VoidMessage()

  @auth.method(
      shelf_messages.Shelf,
      shelf_messages.ListShelfResponse,
      name='list',
      path='list',
      http_method='POST',
      permission=permissions.Permissions.READ_SHELVES)
  def list_shelves(self, request):
    """Lists enabled or all shelves based on any shelf attribute."""
    self.check_xsrf_token(self.request_state)
    if request.page_size <= 0:
      raise endpoints.BadRequestException(
          'The value for page_size must be greater than 0.')
    query, sort_options, returned_fields = (
        search_utils.set_search_query_options(request.query))
    if not query:
      query = search_utils.to_query(request, shelf_model.Shelf)

    offset = search_utils.calculate_page_offset(
        page_size=request.page_size, page_number=request.page_number)

    search_results = shelf_model.Shelf.search(
        query_string=query, query_limit=request.page_size,
        offset=offset, sort_options=sort_options,
        returned_fields=returned_fields)
    total_pages = search_utils.calculate_total_pages(
        page_size=request.page_size, total_results=search_results.number_found)

    shelves_messages = []
    for document in search_results.results:
      message = search_utils.document_to_message(
          document, shelf_messages.Shelf())
      message.shelf_request = shelf_messages.ShelfRequest()
      message.shelf_request.urlsafe_key = document.doc_id
      message.shelf_request.location = message.location
      shelves_messages.append(message)

    return shelf_messages.ListShelfResponse(
        shelves=shelves_messages,
        total_results=search_results.number_found,
        total_pages=total_pages)

  @auth.method(
      shelf_messages.ShelfAuditRequest,
      message_types.VoidMessage,
      name='audit',
      path='audit',
      http_method='POST',
      permission=permissions.Permissions.AUDIT_SHELF)
  def audit(self, request):
    """Performs an audit on a shelf based on location."""
    self.check_xsrf_token(self.request_state)
    shelf = get_shelf(request.shelf_request)
    user_email = user.get_user_email()
    devices_on_shelf = []
    shelf_string_query = 'shelf: {}'.format(shelf.key.urlsafe())
    devices_retrieved_on_shelf = device_model.Device.search(shelf_string_query)
    for device_identifier in request.device_identifiers:
      device = device_model.Device.get(identifier=device_identifier)
      if not device:
        raise endpoints.NotFoundException(
            _DEVICE_DOES_NOT_EXIST_MSG % device_identifier)
      if device.shelf:
        if device.shelf == shelf.key:
          devices_on_shelf.append(device.key.urlsafe())
          logging.info('Device %s is already on shelf.', device.identifier)
          continue
      try:
        device.move_to_shelf(shelf=shelf, user_email=user_email)
        devices_on_shelf.append(device.key)
      except device_model.UnableToMoveToShelfError as err:
        raise endpoints.BadRequestException(str(err))
    for device in devices_retrieved_on_shelf.results:
      if device.doc_id not in devices_on_shelf:
        api_utils.get_ndb_key(device.doc_id).get().remove_from_shelf(
            shelf=shelf, user_email=user_email)
    shelf.audit(user_email=user_email, num_of_devices=len(devices_on_shelf))

    return message_types.VoidMessage()


def get_shelf(request):
  """Gets a shelf using the location.

  Args:
    request: shelf_messages.ShelfRequest, the request message for a shelf.

  Returns:
    Shelf object.

  Raises:
    endpoints.NotFoundException when a shelf can not be found.
  """
  if request.urlsafe_key:
    shelf = api_utils.get_ndb_key(request.urlsafe_key).get()
  else:
    shelf = shelf_model.Shelf.get(location=request.location)
  if not shelf:
    raise endpoints.NotFoundException(
        _SHELF_DOES_NOT_EXIST_MSG % request.location)
  return shelf
