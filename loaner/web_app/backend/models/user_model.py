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

"""A model representing a Grab n Go user."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from google.appengine.ext import ndb

from loaner.web_app.backend.api import permissions

_SUPERADMIN_RESERVED_ERROR = (
    'Cannot create a role named "superadmin", that name is reserved.')
_UPDATE_ROLE_NAME_ERROR = "Cannot update a role's name, generate a new role."
_ROLE_NOT_FOUND = 'Role with name %s was not found.'
_ROLE_ALREADY_EXISTS = 'Role with name %s already exists'


class Error(Exception):
  """Base error class for the module."""


class CreateRoleError(Error):
  """When a Role cannot be created."""


class UpdateRoleError(Error):
  """Raised when there is an error updating Role attributes."""


class RoleNotFoundError(Error):
  """Raised when a role isn't found for a given name."""


class Role(ndb.Model):
  """Datastore model representing a role.

  Attributes:
    permissions: list|str|, a list of string Permissions for that role.
    associated_group: str, name of the Google Group (or other permission
        container) used to associate this role to users automatically.
  """
  permissions = ndb.StringProperty(repeated=True)
  associated_group = ndb.StringProperty()

  @property
  def name(self):
    """String name of the Role."""
    return self.key.string_id()

  @classmethod
  def create(cls, name, role_permissions=None, associated_group=None):
    """Creates a new role.

    Args:
      name: str, name of the new role.
      role_permissions: list|str|, zero or more Permissions to include.
      associated_group: str, name of the Google Group (or other permission
        container) used to associate this group of permissions to users.

    Returns:
      Created Role.

    Raises:
      CreateRoleError: If a role fails to be created.
    """
    if name == 'superadmin':
      raise CreateRoleError(_SUPERADMIN_RESERVED_ERROR)
    if cls.get_by_name(name):
      raise CreateRoleError(_ROLE_ALREADY_EXISTS, name)
    new_role = cls(
        key=ndb.Key(cls, name),
        permissions=role_permissions or [],
        associated_group=associated_group)
    new_role.put()
    return new_role

  @classmethod
  def get_by_name(cls, name):
    """Gets a role by its name.

    Args:
      name: str, name of the role.

    Returns:
      Role object.
    """
    return ndb.Key(cls, name).get()

  def update(self, **kwargs):
    """Updates a role's permissions or associated group."""
    if kwargs.get('name'):
      raise UpdateRoleError(_UPDATE_ROLE_NAME_ERROR)
    self.populate(**kwargs)
    self.put()


class User(ndb.Model):
  """Datastore model representing a user.

  Attributes:
    roles: list, a list of roles the user belongs to.
    superadmin: bool, whether the user is a superadmin which grants all
        permissions by default.
  """
  roles = ndb.KeyProperty(repeated=True)
  superadmin = ndb.BooleanProperty(default=False)

  @property
  def role_names(self):
    """Returns list|str| of role names."""
    return [name.string_id() for name in self.roles]

  @classmethod
  def get_user(cls, email):
    """Retrieves the user model, creating a new entity if necessary.

    Args:
      email: str, the user's email.

    Returns:
      The user model for the current user.
    """
    return cls.get_or_insert(email)

  def update(self, roles=None, superadmin=None):
    """Updates a user's attributes.

    Args:
      roles: list|str|, Optional list of Roles for user.
      superadmin: bool, if the user is superadmin.

    Raises:
      RoleNotFoundError: If a non-existent role is added.
    """
    if roles:
      self.roles = []
      for role_name in roles:
        role = Role.get_by_name(role_name)
        if not role:
          raise RoleNotFoundError(_ROLE_NOT_FOUND, role_name)
        self.roles.append(role.key)
    elif roles == []:  # pylint: disable=g-explicit-bool-comparison
      self.roles = []
    if superadmin is not None:
      self.superadmin = superadmin
    self.put()

  def get_permissions(self):
    """Get permisisons for user.

    Returns:
      Iterable of string Permissions.
    """
    if self.superadmin:
      return permissions.Permissions.ALL
    user_permissions = []
    for role in self.roles:
      for permission in role.get().permissions:
        user_permissions.append(permission)
    return list(set(user_permissions))
