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
import math

from google.appengine.api import datastore_errors
from google.appengine.ext import deferred
from google.appengine.ext import ndb

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

    Raises:
      datastore_errors.BadValueError: If the tag name is an empty string.
    """
    tag = cls(
        name=name,
        hidden=hidden,
        protect=protect,
        color=color,
        description=description)
    if not name:
      raise datastore_errors.BadValueError('The tag name must not be empty.')
    tag.put()
    logging.info('Creating a new tag with name %r.', name)
    tag.stream_to_bq(user_email, 'Created a new tag with name %r.' % name)
    return tag

  @classmethod
  def get(cls, name):
    """Gets a Tag by its name.

    Args:
      name: str, the name of the tag.

    Returns:
      A Tag model entity.
    """
    return cls.query(cls.name == name).get()

  def update(self, user_email, **kwargs):
    """Updates an existing tag.

    Args:
      user_email: str, email of the user creating the tag.
      **kwargs: kwargs for the update API.

    Raises:
      datastore_errors.BadValueError: If the tag name is an empty string.
    """
    if not kwargs['name']:
      raise datastore_errors.BadValueError('The tag name must not be empty.')

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
      deferred.defer(_delete_tags, model, key.get())

  @classmethod
  def list(cls, page_size=10, page_index=1, include_hidden_tags=False,
           cursor=None):
    """Fetches tags entities from datastore.

    Args:
      page_size: int, The number of results to return.
      page_index: int, The page index to offset the results from.
      include_hidden_tags: bool, Whether to include hidden tags in the results.
      cursor: Optional[datastore_query.Cursor], pointing to the last
        result.

    Returns:
      A tuple of a list of Tag instances, a datastore_query.Cursor instance,
      and a boolean representing whether or not there are additional results to
      retrieve. For example:

      ([tag_model.Tag instance_1, ..., tag_model.Tag instance_pagesize - 1],
       datastore_query.Cursor instance,
       True)
    """
    query_object = cls.query()
    if not include_hidden_tags:
      query_object = query_object.filter(cls.hidden == False)  # pylint: disable=singleton-comparison,g-explicit-bool-comparison
    return query_object.fetch_page(
        page_size=page_size, start_cursor=cursor,
        offset=(page_index - 1) * page_size), int(
            math.ceil(query_object.count() / page_size))


def _delete_tags(model, tag, cursor=None, num_updated=0, batch_size=100):
  """Cleans up any entities on the given model that reference the given key.

  Args:
    model: ndb.Model, a Model with a repeated TagData property.
    tag: Tag, an instance of a Tag model.
    cursor: Optional[datastore_query.Cursor], pointing to the last result.
    num_updated: int, the number of entities that were just updated.
    batch_size: int, the number of entities to include in the batch.
  """
  entities, next_cursor, more = model.query(
      model.tags.tag == tag).fetch_page(batch_size, start_cursor=cursor)

  for entity in entities:
    entity.tags = [
        model_tag for model_tag in entity.tags if model_tag.tag != tag
    ]
  ndb.put_multi(entities)

  num_updated += len(entities)
  logging.info(
      'Destroyed %d occurrence(s) of the tag with URL safe key %r',
      len(entities), tag.key.urlsafe())
  if more:
    deferred.defer(
        _delete_tags, model, tag,
        cursor=next_cursor, num_updated=num_updated, batch_size=batch_size)
  else:
    logging.info(
        'Destroyed a total of %d occurrence(s) of the tag with URL safe key %r',
        num_updated, tag.key.urlsafe())


class TagData(ndb.Model):
  """A model representing a tag reference and its informational field.

  Note that when applying this as a repeated StructuredProperty to an ndb.Model,
  the property name must be 'tags'.

  Attributes:
    tag: Tag, an instance of a Tag entity.
    more_info: str, an informational field about this particular tag reference.
  """
  tag = ndb.StructuredProperty(Tag)
  more_info = ndb.StringProperty()
