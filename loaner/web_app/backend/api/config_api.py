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

"""API endpoint that handles requests related to config for App."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from protorpc import message_types

import endpoints

from loaner.web_app import config_defaults
from loaner.web_app.backend.api import auth
from loaner.web_app.backend.api import permissions
from loaner.web_app.backend.api import root_api
from loaner.web_app.backend.api.messages import config_message
from loaner.web_app.backend.models import config_model

_FIELD_MISSING_MSG = 'Please double-check you provided all necessary fields.'


@root_api.ROOT_API.api_class(
    resource_name='config', path='config')
class ConfigAPI(root_api.Service):
  """Endpoints API service class for Config config resource."""

  @auth.method(
      config_message.GetConfigRequest,
      config_message.ConfigResponse,
      name='get',
      path='get',
      http_method='GET',
      permission=permissions.Permissions.READ_CONFIGS)
  def get_config(self, request):
    """Gets the given config value."""
    self.check_xsrf_token(self.request_state)
    if not request.config_type or not request.name:
      raise endpoints.BadRequestException(_FIELD_MISSING_MSG)

    try:
      setting_value = config_model.Config.get(request.name)
    except KeyError as error:
      raise endpoints.BadRequestException(str(error))

    if request.config_type == config_message.ConfigType.STRING:
      response_message = config_message.ConfigResponse(
          string_value=setting_value)
    elif request.config_type == config_message.ConfigType.INTEGER:
      response_message = config_message.ConfigResponse(
          integer_value=setting_value)
    elif request.config_type == config_message.ConfigType.BOOLEAN:
      response_message = config_message.ConfigResponse(
          boolean_value=setting_value)
    elif request.config_type == config_message.ConfigType.LIST:
      response_message = config_message.ConfigResponse(list_value=setting_value)
    return response_message

  @auth.method(
      message_types.VoidMessage,
      config_message.ListConfigsResponse,
      name='list',
      path='list',
      http_method='GET',
      permission=permissions.Permissions.READ_CONFIGS)
  def list_configs(self, request):
    """Gets a list of all config values."""
    self.check_xsrf_token(self.request_state)
    response_message = []

    for setting in config_defaults.DEFAULTS:
      setting_value = config_model.Config.get(setting)
      if isinstance(setting_value, basestring):
        response_message.append(config_message.ConfigResponse(
            name=setting, string_value=setting_value))
      if (isinstance(setting_value, int) and not isinstance(setting_value, bool)
          or isinstance(setting_value, float)):
        response_message.append(config_message.ConfigResponse(
            name=setting, integer_value=setting_value))
      if isinstance(setting_value, bool) and isinstance(setting_value, int):
        response_message.append(config_message.ConfigResponse(
            name=setting, boolean_value=setting_value))
      if isinstance(setting_value, list):
        response_message.append(config_message.ConfigResponse(
            name=setting, list_value=setting_value))
    return config_message.ListConfigsResponse(configs=response_message)

  @auth.method(
      config_message.UpdateConfigRequest,
      message_types.VoidMessage,
      name='update',
      path='update',
      http_method='POST',
      permission=permissions.Permissions.MODIFY_CONFIG)
  def update_config(self, request):
    """Updates a given config value."""
    self.check_xsrf_token(self.request_state)
    if not request.config_type or not request.name:
      raise endpoints.BadRequestException(_FIELD_MISSING_MSG)
    try:
      if request.config_type == config_message.ConfigType.STRING:
        config_model.Config.set(
            name=request.name, value=request.string_value)
      elif request.config_type == config_message.ConfigType.INTEGER:
        config_model.Config.set(
            name=request.name, value=request.integer_value)
      elif request.config_type == config_message.ConfigType.BOOLEAN:
        config_model.Config.set(
            name=request.name, value=request.boolean_value)
      elif request.config_type == config_message.ConfigType.LIST:
        config_model.Config.set(
            name=request.name, value=request.list_value)
    except KeyError as error:
      raise endpoints.BadRequestException(str(error))

    return message_types.VoidMessage()
