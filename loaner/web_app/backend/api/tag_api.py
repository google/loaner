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
    user_email = user.get_user_email()
    self.check_xsrf_token(self.request_state)
    try:
      # The protect attribute will always be set to false because an
      # end-user will not have the ability to mark a tag as protected in
      # the web app.
      tag_model.Tag.create(
          user_email=user_email,
          name=request.tag.name,
          visible=request.tag.visible,
          color=request.tag.color,
          protect=False,
          description=request.tag.description)
    except (tag_model.CreateTagError, datastore_errors.BadValueError) as err:
      raise endpoints.BadRequestException(
          'Tag creation failed due to: %s' % str(err))

    return message_types.VoidMessage()
