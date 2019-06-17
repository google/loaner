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

"""API endpoint that handles requests related to Tags."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from protorpc import message_types

from google.appengine.api import datastore_errors

import endpoints

from loaner.web_app.backend.api import auth
from loaner.web_app.backend.api import permissions
from loaner.web_app.backend.api import root_api
from loaner.web_app.backend.api.messages import tag_messages
from loaner.web_app.backend.lib import api_utils
from loaner.web_app.backend.lib import user
from loaner.web_app.backend.models import tag_model


@root_api.ROOT_API.api_class(resource_name='tag', path='tag')
class TagApi(root_api.Service):
  """This class is for the Tag API."""

  @auth.method(
      tag_messages.CreateTagRequest,
      message_types.VoidMessage,
      name='create',
      path='create',
      http_method='POST',
      permission=permissions.Permissions.MODIFY_TAG)
  def create(self, request):
    """Creates a new tag and inserts the instance into datastore."""
    self.check_xsrf_token(self.request_state)
    try:
      tag_model.Tag.create(
          user_email=user.get_user_email(),
          name=request.tag.name,
          hidden=request.tag.hidden,
          color=request.tag.color,
          protect=request.tag.protect,
          description=request.tag.description)
    except datastore_errors.BadValueError as err:
      raise endpoints.BadRequestException(
          'Tag creation failed due to: %s' % err)

    return message_types.VoidMessage()

  @auth.method(
      tag_messages.TagRequest,
      message_types.VoidMessage,
      name='destroy',
      path='destroy',
      http_method='POST',
      permission=permissions.Permissions.MODIFY_TAG)
  def destroy(self, request):
    """Destroys a tag and removes all references via _pre_delete_hook method."""
    self.check_xsrf_token(self.request_state)
    key = api_utils.get_ndb_key(urlsafe_key=request.urlsafe_key)
    tag = key.get()
    if tag.protect:
      raise endpoints.BadRequestException(
          'Cannot destroy tag %s because it is protected.' % tag.name)
    key.delete()
    return message_types.VoidMessage()

  @auth.method(
      tag_messages.TagRequest,
      tag_messages.Tag,
      name='get',
      path='get',
      http_method='POST')
  def get(self, request):
    """Gets a tag by its urlsafe key."""
    self.check_xsrf_token(self.request_state)
    tag = api_utils.get_ndb_key(request.urlsafe_key).get()
    return tag_messages.Tag(
        name=tag.name,
        hidden=tag.hidden,
        color=tag.color,
        protect=tag.protect,
        description=tag.description)

  @auth.method(
      tag_messages.ListTagRequest,
      tag_messages.ListTagResponse,
      name='list',
      path='list',
      http_method='POST',
      permission=permissions.Permissions.READ_CONFIGS)
  def list(self, request):
    """Lists tags in datastore."""
    self.check_xsrf_token(self.request_state)

    if request.page_size <= 0:
      raise endpoints.BadRequestException(
          'The value for page size must be greater than 0.')

    cursor = None
    if request.cursor:
      cursor = api_utils.get_datastore_cursor(urlsafe_cursor=request.cursor)

    (tag_results, next_cursor,
     has_additional_results), total_pages = tag_model.Tag.list(
         page_size=request.page_size,
         page_index=request.page_index,
         include_hidden_tags=request.include_hidden_tags,
         cursor=cursor)
    tags_messages = []
    for tag in tag_results:
      message = tag_messages.Tag(
          name=tag.name, hidden=tag.hidden, color=tag.color,
          protect=tag.protect, description=tag.description,
          urlsafe_key=tag.key.urlsafe())
      tags_messages.append(message)

    return tag_messages.ListTagResponse(
        tags=tags_messages,
        cursor=next_cursor.urlsafe() if next_cursor else None,
        has_additional_results=has_additional_results,
        total_pages=total_pages)

  @auth.method(
      tag_messages.UpdateTagRequest,
      message_types.VoidMessage,
      name='update',
      path='update',
      http_method='POST',
      permission=permissions.Permissions.MODIFY_TAG)
  def update(self, request):
    """Updates an existing tag."""
    self.check_xsrf_token(self.request_state)
    key = api_utils.get_ndb_key(urlsafe_key=request.tag.urlsafe_key)
    tag = key.get()
    if tag.protect:
      raise endpoints.BadRequestException(
          'Cannot update tag %s because it is protected.' % tag.name)
    try:
      tag.update(
          user_email=user.get_user_email(),
          name=request.tag.name,
          hidden=request.tag.hidden,
          protect=request.tag.protect,
          color=request.tag.color,
          description=request.tag.description)
    except datastore_errors.BadValueError as err:
      raise endpoints.BadRequestException(
          'Tag update failed due to: %s' % str(err))
    return message_types.VoidMessage()
