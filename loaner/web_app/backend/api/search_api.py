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

"""Helper api to test search functionality."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from protorpc import message_types

from loaner.web_app.backend.api import auth
from loaner.web_app.backend.api import permissions
from loaner.web_app.backend.api import root_api
from loaner.web_app.backend.api.messages import search_messages
from loaner.web_app.backend.models import device_model
from loaner.web_app.backend.models import shelf_model


@root_api.ROOT_API.api_class(resource_name='search', path='search')
class SearchApi(root_api.Service):
  """Endpoints API service class for search helper methods."""

  @auth.method(
      search_messages.SearchMessage,
      message_types.VoidMessage,
      name='clear',
      path='clear',
      http_method='GET',
      permission=permissions.Permissions.CLEAR_INDICES)
  def clear(self, request):
    """Clears a search index for the given type."""
    if request.model == search_messages.SearchIndexEnum.DEVICE:
      device_model.Device.clear_index()
    elif request.model == search_messages.SearchIndexEnum.SHELF:
      shelf_model.Shelf.clear_index()
    return message_types.VoidMessage()

  @auth.method(
      search_messages.SearchMessage,
      message_types.VoidMessage,
      name='reindex',
      path='reindex',
      http_method='GET',
      permission=permissions.Permissions.REINDEX_SEARCH)
  def reindex(self, request):
    """Reindexes a search index for the given type."""
    if request.model == search_messages.SearchIndexEnum.DEVICE:
      device_model.Device.index_entities_for_search()
    elif request.model == search_messages.SearchIndexEnum.SHELF:
      shelf_model.Shelf.index_entities_for_search()
    return message_types.VoidMessage()
