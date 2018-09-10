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

"""User messages for User API."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from protorpc import messages


class User(messages.Message):
  """User ProtoRPC message.

  Attributes:
    email: str, The user email to be displayed.
    roles: List[str], The roles of the user.
    permissions: List[str], The permissions the user has.
    superadmin: bool, If the user is designated as a superadmin.
  """
  email = messages.StringField(1)
  roles = messages.StringField(2, repeated=True)
  permissions = messages.StringField(3, repeated=True)
  superadmin = messages.BooleanField(4)


class Role(messages.Message):
  """Role ProtoRPC message.

  Attributes:
    name: str, The role's name. Immutable once set.
    permissions: List[str], The permissions associated with the role.
    associated_group: str, The name of the Google Group (or other permissions
        container) used to associate this role to users automatically.
  """
  name = messages.StringField(1, required=True)
  permissions = messages.StringField(2, repeated=True)
  associated_group = messages.StringField(3)


class GetRoleRequest(messages.Message):
  """Get a role by name.

  Attributes:
    name: str, The role's name.
  """
  name = messages.StringField(1, required=True)
