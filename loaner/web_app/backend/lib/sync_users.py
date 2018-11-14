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

"""Loaner Sync User Lib."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import logging

from google.appengine.ext import ndb

from loaner.web_app import constants
from loaner.web_app.backend.clients import directory
from loaner.web_app.backend.models import user_model


def sync_user_roles():
  """Syncs all of the elevated user roles for each user in Google groups."""
  logging.info('Syncing user roles.')

  client = directory.DirectoryApiClient(constants.ADMIN_EMAIL)
  superadmins_from_group = client.get_all_users_in_group(
      constants.SUPERADMINS_GROUP)
  _add_or_remove_user_roles(superadmins_from_group, 'superadmin')

  all_roles = user_model.Role.query().fetch()
  for role in all_roles:
    if role.associated_group:
      users_from_group = client.get_all_users_in_group(role.associated_group)
      _add_or_remove_user_roles(users_from_group, role.name)


def _add_or_remove_user_roles(group_users, role):
  """Add or remove a user's role based on Google group membership.

  This will check the datastore users that are passed (ndb_users) against the
  users in the Google group that are passed (group_users). It will do nothing
  with the union of both. It will add the given role to the users that are in
  the Google group and not in the datastore users (creating a user object in
  datastore if nessesary). Similarly, it will remove the user permissions if
  the ndb_users are not in group_users.

  Args:
    group_users: list, a list of users from a Google Group.
    role: str, the role to add or remove from user.
  """
  if role == 'superadmin':
    users_keys = user_model.User.query(
        user_model.User.superadmin == True).fetch(keys_only=True)  # pylint: disable=g-explicit-bool-comparison,singleton-comparison
  else:
    role_key = ndb.Key(user_model.Role, role)
    users_keys = user_model.User.query(
        user_model.User.roles.IN([role_key])).fetch(keys_only=True)
  ndb_user_ids = [user.id() for user in users_keys]
  users_to_add_role = set(group_users) - set(ndb_user_ids)
  users_to_remove_role = set(ndb_user_ids) - set(group_users)
  for user_email in users_to_add_role:
    user = user_model.User.get_user(user_email)
    if role == 'superadmin':
      user.update(superadmin=True)
    else:
      new_roles = user.role_names
      new_roles.append(role)
      user.update(roles=new_roles)
  for user_email in users_to_remove_role:
    user = user_model.User.get_user(user_email)
    if role == 'superadmin':
      user.update(superadmin=False)
    else:
      new_roles = user.role_names
      new_roles.remove(role)
      user.update(roles=new_roles)
