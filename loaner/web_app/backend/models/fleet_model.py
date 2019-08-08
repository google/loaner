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

"""A model representing a fleet organization."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from google.appengine.ext import ndb
from loaner.web_app.backend.models import base_model


class Error(Exception):
  """Base error class for the module."""


class CreateFleetError(Error):
  """When a Fleet cannot be created."""


class Fleet(base_model.BaseModel):
  """Model for a fleet organization.

  Attributes:
    config: list|ndb.key|, The list of fleet specific config models.
    description: str, Optional text description of fleet.
    display_name: str, Optional display name, defaults to self.name.
  """
  config = ndb.KeyProperty(kind='Config', repeated=True)
  description = ndb.StringProperty()
  display_name = ndb.StringProperty()

  @property
  def name(self):
    """String name of Fleet organization."""
    return self.key.string_id()

  @classmethod
  def create(cls, acting_user, name, config,
             description=None, display_name=None):
    """Creates a new Fleet.

    Args:
      acting_user: str, email address of the user making the request.
      name: str, name of the Fleet.
      config: list|ndb.key|, The list of fleet specific config models.
      description: str, Optional text description of fleet.
      display_name: str, Optional display name, defaults to self.name.

    Returns:
      Created Fleet.

    Raises:
      CreateFleetError: If the fleet fails to be created.
    """
    if not name or not isinstance(name, str):
      raise CreateFleetError('Fleet name is invalid.', name)
    if cls.get_by_name(name):
      raise CreateFleetError('Fleet organization already exists', name)
    new_fleet = cls(
        key=ndb.Key(cls, name),
        config=config or [],
        description=description,
        display_name=display_name or name)
    new_fleet.put()
    new_fleet.stream_to_bq(acting_user, 'Created fleet %s' % display_name)
    return new_fleet

  @classmethod
  def default(cls, acting_user, display_name, description=None):
    """Creates a Fleet with default settings.

    Args:
      acting_user: str, email address of the user making the request.
      display_name: str, Required display name for default fleet.
      description: str, Optional text description of fleet.

    Returns:
      The default fleet.

    Raises:
      CreateFleetError: If the fleet fails to be created.
    """
    return cls.create(
        acting_user=acting_user,
        name='default',
        config=[],  # The default fleet uses only config_defaults settings.
        description=description or 'The default fleet organization',
        display_name=display_name)

  @classmethod
  def get_by_name(cls, name):
    """Gets a fleet by its name.

    Args:
      name: str, name of the fleet.

    Returns:
      Fleet object.
    """
    return ndb.Key(cls, name).get()

  @classmethod
  def list_all_fleets(cls):
    """Returns all fleets in datastore.

    Returns:
      List of Fleets.
    """
    return cls.query().fetch()
