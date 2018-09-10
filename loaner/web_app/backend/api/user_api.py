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

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from protorpc import message_types

from loaner.web_app.backend.api import auth
from loaner.web_app.backend.api import permissions
from loaner.web_app.backend.api import root_api
from loaner.web_app.backend.api.messages import user_messages
from loaner.web_app.backend.lib import user as user_lib
from loaner.web_app.backend.models import user_model


@root_api.ROOT_API.api_class(resource_name='user', path='user')
class UserApi(root_api.Service):
  """Endpoints API service class for UserApi settings resource."""

  @auth.method(
      message_types.VoidMessage,
      user_messages.User,
      name='get',
      path='get',
      http_method='GET')
  def get(self, request):
    """Gets user details for the logged in user."""
    user = user_model.User.get_user(email=user_lib.get_user_email())
    return user_messages.User(
        email=user.key.id(),
        roles=user.role_names,
        permissions=user.get_permissions(),
        superadmin=user.superadmin)


@root_api.ROOT_API.api_class(resource_name='role', path='role')
class RoleApi(root_api.Service):
  """Endpoints API service class for Role and Role-related User requests."""

  @auth.method(
      user_messages.Role,
      message_types.VoidMessage,
      name='create',
      path='create',
      http_method='POST',
      permission=permissions.Permissions.MODIFY_ROLE)
  def create(self, request):
    """Creates a new role."""
    self.check_xsrf_token(self.request_state)
    user_model.Role.create(
        name=request.name,
        role_permissions=request.permissions,
        associated_group=request.associated_group)
    return message_types.VoidMessage()

  @auth.method(
      user_messages.GetRoleRequest,
      user_messages.Role,
      name='get',
      path='get',
      http_method='GET',
      permission=permissions.Permissions.READ_ROLES)
  def get(self, request):
    """Gets a role."""
    self.check_xsrf_token(self.request_state)
    role = user_model.Role.get_by_name(request.name)
    return user_messages.Role(
        name=role.name,
        permissions=role.permissions,
        associated_group=role.associated_group)

  @auth.method(
      user_messages.Role,
      message_types.VoidMessage,
      name='update',
      path='update',
      http_method='POST',
      permission=permissions.Permissions.MODIFY_ROLE)
  def update(self, request):
    """Updates a role's permissions or associated group. Cannot edit name."""
    self.check_xsrf_token(self.request_state)
    role = user_model.Role.get_by_name(request.name)
    role.update(
        permissions=request.permissions,
        associated_group=request.associated_group)
    return message_types.VoidMessage()
