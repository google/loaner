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

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import endpoints

from loaner.web_app.backend.api import auth
from loaner.web_app.backend.api import root_api
from loaner.web_app.backend.api.messages import chrome_messages
from loaner.web_app.backend.lib import user as user_lib
from loaner.web_app.backend.models import config_model
from loaner.web_app.backend.models import device_model

_NO_DEVICE_ID_MSG = 'Device ID must be provided.'


@root_api.ROOT_API.api_class(resource_name='chrome', path='chrome')
class ChromeApi(root_api.Service):
  """Google Endpoints Frameworks API service class for the GnG Chrome App."""

  @auth.method(
      chrome_messages.HeartbeatRequest,
      chrome_messages.HeartbeatResponse,
      name='heartbeat',
      path='heartbeat',
      http_method='GET')
  def heartbeat(self, request):
    """Heartbeat check-in for devices."""
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
    silent_onboarding = config_model.Config.get('silent_onboarding')
    return chrome_messages.HeartbeatResponse(
        is_enrolled=is_enrolled,
        start_assignment=start_assignment,
        silent_onboarding=silent_onboarding,
    )
