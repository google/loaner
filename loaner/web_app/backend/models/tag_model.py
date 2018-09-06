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

"""A model representing a tag."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import logging

from google.appengine.ext import ndb

from loaner.web_app.backend.models import base_model
from loaner.web_app.backend.models import device_model

_CREATE_TAG_MSG = 'Creating a new tag with name %s.'
_RENAME_TAG_MSG = 'Renaming a tag with name %s to %s.'
_UPDATE_TAG_MSG = 'Updating a tag with name %s with properties %s.'
_DESTROYING_TAG_MSG = 'Destroying a tag with name %s.'
_DESTROYED_TAG_MSG = 'Destroyed a tag with key id %s.'

_MODELS_WITH_TAGS = (device_model.Device,)
_TAG_COLORS = ('red', 'pink', 'purple', 'deep purple', 'indigo', 'blue',
               'light blue', 'cyan', 'teal', 'green', 'light green', 'lime',
               'yellow', 'amber', 'orange', 'deep orange', 'brown', 'grey',
               'blue grey')


class CreateTagError(Exception):
  """Raised when creating a tag fails."""


class DestroyTagError(Exception):
  """Raised when destroying a tag fails."""


class UpdateTagError(Exception):
  """Raised when updating a tag fails."""


class Tag(base_model.BaseModel):
  """Datastore model representing a tag.

  Attributes:
    name: str, a unique name for the tag.
    visible: bool, whether a tag is visible in the frontend UI
    protect: bool, whether a tag is protected from user manipulation.
    color: str, the UI color of the tag in human-readable format.
    description: str, an optional description for the tag.
  """
  name = ndb.StringProperty(required=True)
  visible = ndb.BooleanProperty(required=True)
  protect = ndb.BooleanProperty(indexed=False, required=True)
  color = ndb.StringProperty(choices=_TAG_COLORS, indexed=False, required=True)
  description = ndb.StringProperty()

  @classmethod
  def create(
      cls, user_email, name, visible, protect, color, description=None):
    """Creates a new tag.

    Args:
      user_email: str, email of the user creating the tag.
      name: str, a unique name for the tag.
      visible: bool, whether a tag is visible in the frontend UI.
      protect: bool, whether a tag is protected from user manipulation.
      color: str, the UI color of the tag in human-readable format.
      description: str, a description for the tag.

    Returns:
      The new Tag entity.

    Raises:
      CreateTagError: if there is already a tag with the requested name.
    """
    tag = cls(
        name=name, visible=visible, protect=protect, color=color,
        description=description)
    if cls.get(name):
      raise CreateTagError(
          'Cannot create because a tag with name %r already exists.' % name)
    tag.put()
    logging.info(_CREATE_TAG_MSG, name)
    tag.stream_to_bq(user_email, _CREATE_TAG_MSG % name)
    return tag

  @classmethod
  def get(cls, name):
    """Get a Tag by name.

    Args:
      name: str, the name of the tag.

    Returns:
      A Tag model instance, or None.
    """
    return cls.query(cls.name == name).get()

  @classmethod
  def update(cls, user_email, name, visible, protect, color, description=None,
             new_name=None):
    """Updates an existing tag.

    Args:
      user_email: str, email of the user updating the tag.
      name: str, a unique name for the tag.
      visible: bool, whether a tag is visible in the frontend UI.
      protect: bool, whether a tag is protected from user manipulation.
      color: str, the UI color of the tag in human-readable format.
      description: str, a description for the tag.
      new_name: str, the new name for the tag in the case of a tag rename.

    Returns:
      The updated Tag entity.

    Raises:
      UpdateTagError: if there is not an existing tag to update.
    """
    tag = cls.get(name)
    if tag is None:
      raise UpdateTagError('A tag with name %s does not exist.' % name)

    if new_name:
      logging.info(_RENAME_TAG_MSG, name, new_name)

    name = new_name or name
    tag.populate(
        name=name, visible=visible, protect=protect, color=color,
        description=description)
    tag.put()
    logging.info(
        _UPDATE_TAG_MSG, name, (visible, protect, color, description))
    tag.stream_to_bq(
        user_email, _UPDATE_TAG_MSG %
        (name, (visible, protect, color, description)))
    return tag

  @classmethod
  def destroy(cls, name):
    """Destroys an existing tag and cleans up its references.

    A _pre_delete_hook() is defined on this class in order to clean up Tag
    references defined on any model defined in _MODELS_WITH_TAGS.

    Args:
      name: str, a unique name for the tag.

    Returns:
      None.

    Raises:
      DestroyTagError: if there is not an existing tag to destroy.
    """
    logging.info(_DESTROYING_TAG_MSG, name)
    tag = cls.get(name)
    if tag is None:
      raise DestroyTagError('A tag with name %s does not exist.' % name)
    return ndb.Key('Tag', tag.key.id()).delete()

  @classmethod
  def _pre_delete_hook(cls, key):
    """This _pre_delete_hook cleans up any entities that reference the key.

    Args:
      key: ndb.Key, a Tag model key.
    """
    for model in _MODELS_WITH_TAGS:
      entities = model.query(model.tags.tag_key == key).fetch()
      for entity in entities:
        entity.tags = [tag for tag in entity.tags if tag.tag_key != key]
      ndb.put_multi(entities)
    logging.info(_DESTROYED_TAG_MSG, key.id())
