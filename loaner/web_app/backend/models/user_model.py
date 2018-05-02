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


class User(ndb.Model):
  """Datastore model representing a user.

  Attributes:
    roles: list, A list of roles the user belongs to.
  """
  roles = ndb.StringProperty(repeated=True)

  @classmethod
  def get_user(cls, email, opt_roles=None):
    """Retrieves the user model, creating a new entity if necessary.

    Args:
      email: str, The user's email.
      opt_roles: list|str|, Optional list of roles for a new user.

    Returns:
      The user model for the current user.
    """
    user = cls.get_or_insert(email)
    if not user.roles:
      user.update_user(roles=['user'])
    if opt_roles:
      for role in opt_roles:
        user.roles.append(role)
      user.roles = list(set(user.roles))
      user.put()
    return user

  def update_user(self, **params):
    """Update user in datastore.

    Args:
      **params: A kwarg the key value pairs to update in the model.
    """
    self.populate(**params)
    self.put()
