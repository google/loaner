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

"""API endpoint that handles requests related to email templates for App."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from protorpc import message_types
from google.appengine.api import datastore_errors

import endpoints


from loaner.web_app.backend.api import auth
from loaner.web_app.backend.api import permissions
from loaner.web_app.backend.api import root_api
from loaner.web_app.backend.api.messages import template_messages
from loaner.web_app.backend.models import template_model

_FIELD_MISSING_MSG = 'Please double-check you provided all necessary fields.'


@root_api.ROOT_API.api_class(
    resource_name='template', path='template')
class TemplateApi(root_api.Service):
  """Endpoints API service class for Template resource."""

  @auth.method(
      message_types.VoidMessage,
      template_messages.ListTemplatesResponse,
      name='list',
      path='list',
      http_method='GET',
      permission=permissions.Permissions.READ_CONFIGS)
  def list(self, request):
    """Gets a list of all template values."""
    self.check_xsrf_token(self.request_state)
    response_message = []
    for template in template_model.Template.get_all():
      response_message.append(template_messages.Template(
          name=template.name,
          body=template.body,
          title=template.title))
    return template_messages.ListTemplatesResponse(templates=response_message)

  @auth.method(
      template_messages.UpdateTemplateRequest,
      message_types.VoidMessage,
      name='update',
      path='update',
      http_method='POST',
      permission=permissions.Permissions.MODIFY_CONFIG)

  def update(self, request):
    """Updates a given email template value."""
    self.check_xsrf_token(self.request_state)
    template = template_model.Template.get(request.name)
    try:
      template.update(
          name=request.name, title=request.title, body=request.body)
    except datastore_errors.BadValueError as err:
      raise endpoints.BadRequestException(
          'Template update failed due to: %s' % err)
    return message_types.VoidMessage()

  @auth.method(
      template_messages.RemoveTemplateRequest,
      message_types.VoidMessage,
      name='remove',
      path='remove',
      http_method='POST',
      permission=permissions.Permissions.MODIFY_CONFIG)

  def remove(self, request):
    """Removes an email template given a name."""
    self.check_xsrf_token(self.request_state)
    try:
      template = template_model.Template.get(request.name)
      template.remove()
    except KeyError as error:
      raise endpoints.BadRequestException(str(error))
    return message_types.VoidMessage()

  @auth.method(
      template_messages.CreateTemplateRequest,
      message_types.VoidMessage,
      name='create',
      path='create',
      http_method='POST',
      permission=permissions.Permissions.MODIFY_CONFIG)
  def create(self, request):
    """Creates a new template and inserts the instance into datastore."""
    self.check_xsrf_token(self.request_state)
    try:
      template_model.Template.create(
          name=request.template.name,
          title=request.template.title,
          body=request.template.body)
    except datastore_errors.BadValueError as err:
      raise endpoints.BadRequestException(
          'Template creation failed due to: %s' % err)
    return message_types.VoidMessage()
