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

from loaner.web_app.backend.api import auth
from loaner.web_app.backend.api import permissions
from loaner.web_app.backend.api import root_api
from loaner.web_app.backend.api.messages import config_messages
from loaner.web_app.backend.lib import utils
from loaner.web_app.backend.models import config_model

_FIELD_MISSING_MSG = 'Please double-check you provided all necessary fields.'


@root_api.ROOT_API.api_class(
    resource_name='config', path='config')
class ConfigAPI(root_api.Service):
  """Endpoints API service class for Config config resource."""

  @auth.method(
      config_messages.GetConfigRequest,
      config_messages.ConfigResponse,
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

    if request.config_type == config_messages.ConfigType.STRING:
      response_message = config_messages.ConfigResponse(
          string_value=setting_value)
    elif request.config_type == config_messages.ConfigType.INTEGER:
      response_message = config_messages.ConfigResponse(
          integer_value=setting_value)
    elif request.config_type == config_messages.ConfigType.BOOLEAN:
      response_message = config_messages.ConfigResponse(
          boolean_value=setting_value)
    elif request.config_type == config_messages.ConfigType.LIST:
      response_message = config_messages.ConfigResponse(
          list_value=setting_value)
    return response_message

  @auth.method(
      message_types.VoidMessage,
      config_messages.ListConfigsResponse,
      name='list',
      path='list',
      http_method='GET',
      permission=permissions.Permissions.READ_CONFIGS)
  def list_configs(self, request):
    """Gets a list of all config values."""
    self.check_xsrf_token(self.request_state)
    response_message = []
    config_defaults = utils.load_config_from_yaml()
    for setting in config_defaults:
      setting_value = config_model.Config.get(setting)
      if isinstance(setting_value, basestring):
        response_message.append(config_messages.ConfigResponse(
            name=setting, string_value=setting_value))
      if (isinstance(setting_value, int) and not isinstance(setting_value, bool)
          or isinstance(setting_value, float)):
        response_message.append(config_messages.ConfigResponse(
            name=setting, integer_value=setting_value))
      if isinstance(setting_value, bool) and isinstance(setting_value, int):
        response_message.append(config_messages.ConfigResponse(
            name=setting, boolean_value=setting_value))
      if isinstance(setting_value, list):
        response_message.append(config_messages.ConfigResponse(
            name=setting, list_value=setting_value))
    return config_messages.ListConfigsResponse(configs=response_message)

  @auth.method(
      config_messages.UpdateConfigRequest,
      message_types.VoidMessage,
      name='update',
      path='update',
      http_method='POST',
      permission=permissions.Permissions.MODIFY_CONFIG)
  def update_config(self, request):
    """Updates a given config value."""
    self.check_xsrf_token(self.request_state)
    for config in request.config:
      try:
        if config.config_type == config_messages.ConfigType.STRING:
          config_model.Config.set(
              name=config.name, value=config.string_value)
        elif config.config_type == config_messages.ConfigType.INTEGER:
          config_model.Config.set(
              name=config.name, value=config.integer_value)
        elif config.config_type == config_messages.ConfigType.BOOLEAN:
          config_model.Config.set(
              name=config.name, value=config.boolean_value)
        elif config.config_type == config_messages.ConfigType.LIST:
          config_model.Config.set(
              name=config.name, value=config.list_value)
      except KeyError as error:
        raise endpoints.BadRequestException(str(error))

    return message_types.VoidMessage()
