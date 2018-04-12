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

"""API endpoint that handles requests related to users."""

from protorpc import message_types

from loaner.web_app.backend.api import auth
from loaner.web_app.backend.api import root_api
from loaner.web_app.backend.api.messages import user_messages
from loaner.web_app.backend.lib import user as user_lib
from loaner.web_app.backend.models import user_model


@root_api.ROOT_API.api_class(resource_name='user', path='user')
class UserApi(root_api.Service):
  """Endpoints API service class for UserApi settings resource."""

  @auth.method(
      message_types.VoidMessage,
      user_messages.UserResponse,
      name='get',
      path='get',
      http_method='GET')
  def get(self, request):
    """Get user details for the logged in user."""
    user = user_model.User.get_user(email=user_lib.get_user_email())
    return user_messages.UserResponse(
        email=user.key.id(), roles=user.roles)
