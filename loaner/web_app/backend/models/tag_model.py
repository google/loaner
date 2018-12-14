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

from google.appengine.api import datastore_errors
from google.appengine.ext import deferred
from google.appengine.ext import ndb

from loaner.web_app.backend.lib import api_utils
from loaner.web_app.backend.models import base_model


_MODELS_WITH_TAGS = ()

_TAG_COLORS = frozenset((
    'red', 'pink', 'purple', 'deep purple', 'indigo', 'blue', 'light blue',
    'cyan', 'teal', 'green', 'light green', 'lime', 'yellow', 'amber', 'orange',
    'deep orange', 'brown', 'grey', 'blue grey'))


class Tag(base_model.BaseModel):
  """Datastore model representing a tag.

  Attributes:
    name: str, a unique name for the tag.
    hidden: bool, whether a tag is hidden in the frontend UI.
    protect: bool, whether a tag is protected from user manipulation.
    color: str, the UI color of the tag in human-readable format.
    description: Optional[str], a description for the tag.
  """
  name = ndb.StringProperty(required=True)
  hidden = ndb.BooleanProperty(required=True)
  protect = ndb.BooleanProperty(required=True)
  color = ndb.StringProperty(choices=_TAG_COLORS, required=True)
  description = ndb.StringProperty()

  @classmethod
  def create(
      cls, user_email, name, hidden, protect, color, description=None):
    """Creates a new tag.

    Args:
      user_email: str, email of the user creating the tag.
      name: str, a unique name for the tag.
      hidden: bool, whether a tag is hidden in the frontend UI.
      protect: bool, whether a tag is protected from user manipulation.
      color: str, the UI color of the tag in human-readable format.
      description: Optional[str], a description for the tag.

    Returns:
      The new Tag entity.
    """
    tag = cls(
        name=name,
        hidden=hidden,
        protect=protect,
        color=color,
        description=description)
    tag.put()
    logging.info('Creating a new tag with name %r.', name)
    tag.stream_to_bq(user_email, 'Created a new tag with name %r.' % name)
    return tag

  @classmethod
  def get(cls, urlsafe_key):
    """Gets a Tag by its urlsafe key.

    Args:
      urlsafe_key: str, the urlsafe encoding of the requested tag's ndb.Key.

    Returns:
      A Tag model entity.
    """
    return api_utils.get_ndb_key(urlsafe_key).get()

  def update(self, user_email, **kwargs):
    """Updates an existing tag.

    Args:
      user_email: str, email of the user creating the tag.
      **kwargs: kwargs for the update API.
    """
    if kwargs['name'] != self.name:
      logging.info(
          'Renaming the tag with name %r to %r.', self.name, kwargs['name'])

    self.populate(**kwargs)
    self.put()
    logging.info(
        'Updating a tag with urlsafe key %r and name %r.',
        self.key.urlsafe(), self.name)
    self.stream_to_bq(
        user_email, 'Updated a tag with name %r.' % self.name)

  def _pre_put_hook(self):
    """Checks that a Tag entity with a given name does not already exist.

    Raises:
      datastore_errors.BadValueError: when a tag with the given name exists.
    """
    tag_key = Tag.query(Tag.name == self.name).get(keys_only=True)
    if tag_key and tag_key != self.key:
      raise datastore_errors.BadValueError(
          'A Tag entity with name %r already exists.' % self.name)

  @classmethod
  def _pre_delete_hook(cls, key):
    """Cleans up any entities that reference the key.

    Note that this operation can have a long tail in that it requires a bulk tag
    disassociation across potentially many entities in Datastore.

    Args:
      key: ndb.Key, a Tag model key.
    """
    logging.info(
        'Destroying the tag with urlsafe key %r and name %r.',
        key.urlsafe(), key.get().name)
    for model in _MODELS_WITH_TAGS:
      deferred.defer(_delete_tags, model, key)


def _delete_tags(model, key, cursor=None, num_updated=0, batch_size=100):
  """Cleans up any entities on the given model that reference the given key.

  Args:
    model: ndb.Model, a Model with a repeated TagData property.
    key: ndb.Key, a Tag model key.
    cursor: Optional[datastore_query.Cursor], pointing to the last result.
    num_updated: int, the number of entities that were just updated.
    batch_size: int, the number of entities to include in the batch.
  """
  entities, next_cursor, more = model.query(
      model.tags.tag_key == key).fetch_page(batch_size, start_cursor=cursor)
  for entity in entities:
    entity.tags = [tag for tag in entity.tags if tag.tag_key != key]
  ndb.put_multi(entities)

  num_updated += len(entities)
  logging.info(
      'Destroyed %d occurrence(s) of the tag with URL safe key %r',
      len(entities), key.urlsafe())
  if more:
    deferred.defer(
        _delete_tags, model, key,
        cursor=next_cursor, num_updated=num_updated, batch_size=batch_size)
  else:
    logging.info(
        'Destroyed a total of %d occurrence(s) of the tag with URL safe key %r',
        num_updated, key.urlsafe())


class TagData(ndb.Model):
  """A model representing a tag reference and its informational field.

  Note that when applying this as a repeated StructuredProperty to an ndb.Model,
  the property name must be 'tags'.

  Attributes:
    tag_key: ndb.Key, a reference to a Tag entity.
    more_info: str, an informational field about this particular tag reference.
  """
  tag_key = ndb.KeyProperty(Tag)
  more_info = ndb.StringProperty()
