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

"""The entry point for the GnG Loaners Chrome App."""

import endpoints

from loaner.web_app.backend.api import auth
from loaner.web_app.backend.api import device_api
from loaner.web_app.backend.api import root_api
from loaner.web_app.backend.api.messages import chrome_message
from loaner.web_app.backend.clients import directory
from loaner.web_app.backend.lib import user as user_lib
from loaner.web_app.backend.models import device_model

DEVICE_ID = u'deviceId'
MODEL = u'model'
ORG_UNIT_PATH = u'orgUnitPath'
STATUS = u'status'
SERIAL_NUMBER = u'serialNumber'

_NO_DEVICE_ID_MSG = 'Device ID must be provided.'
_NOT_GNG_MSG = 'This device was not found to be a Grab n Go Loaner.'


@root_api.ROOT_API.api_class(resource_name='chrome', path='chrome')
class ChromeApi(root_api.Service):
  """Google Endpoints Frameworks API service class for the GnG Chrome App."""

  @auth.method(
      chrome_message.HeartbeatRequest,
      chrome_message.HeartbeatResponse,
      name='heartbeat',
      path='heartbeat',
      http_method='GET')
  def heartbeat(self, request):
    """Heartbeat check-in for Chrome devices."""
    if not request.device_id:
      raise endpoints.BadRequestException(_NO_DEVICE_ID_MSG)

    user_email = user_lib.get_user_email()
    device = device_model.Device.get(chrome_device_id=request.device_id)

    is_enrolled = False
    start_assignment = False
    if device:
      if device.enrolled:
        is_enrolled = True
        if device.assigned_user == user_email:
          device.loan_resumes_if_late(user_email)
        else:
          start_assignment = True
          device.loan_assign(user_email)

    else:
      try:
        device = device_model.Device.create_unenrolled(
            request.device_id, user_email)
      except device_model.DeviceCreationError as e:
        raise endpoints.NotFoundException(str(e))

    device.record_heartbeat()
    return chrome_message.HeartbeatResponse(
        is_enrolled=is_enrolled, start_assignment=start_assignment)

  @auth.method(
      chrome_message.LoanRequest,
      chrome_message.LoanResponse,
      name='loan',
      path='loan',
      http_method='POST')
  def get_loan(self, request):
    """Get the current loan for a given Chrome device."""
    if not request.device_id:
      raise endpoints.BadRequestException(_NO_DEVICE_ID_MSG)

    device = device_model.Device.get(chrome_device_id=request.device_id)

    if not device:
      raise endpoints.NotFoundException(_NOT_GNG_MSG)

    if request.need_name:
      user_email = user_lib.get_user_email()
      directory_client = directory.DirectoryApiClient(user_email=user_email)
      try:
        given_name = directory_client.given_name(user_email=user_email)
      except (
          directory.DirectoryRPCError, directory.GivenNameDoesNotExistError):
        given_name = None
    else:
      given_name = None

    guest_enabled, max_extend_date, due_date, guest_permitted = (
        device_api.get_loan_data(device))

    return chrome_message.LoanResponse(
        due_date=due_date,
        max_extend_date=max_extend_date,
        given_name=given_name,
        guest_permitted=guest_permitted,
        guest_enabled=guest_enabled)
