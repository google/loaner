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

"""Config messages for Config API."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from protorpc import messages


class ConfigType(messages.Enum):
  STRING = 1
  INTEGER = 2
  BOOLEAN = 3
  LIST = 4


class GetConfigRequest(messages.Message):
  """GetConfigRequest request for ProtoRPC message.

  Attributes:
    name: str, The name of the name being requested.
    config_type: ConfigType, The type of config for which to request.
  """
  name = messages.StringField(1)
  config_type = messages.EnumField(ConfigType, 2)


class ConfigResponse(messages.Message):
  """ConfigResponse response for ProtoRPC message.

  Attributes:
    name: str, The name of the name being returned..
    string_value: str, The string value of the name.
    integer_value: int, The integer value of the name.
    boolean_value: bool, The boolean value of the seting.
    list_value: list, The list value of the name.
  """
  name = messages.StringField(1)
  string_value = messages.StringField(2)
  integer_value = messages.IntegerField(3)
  boolean_value = messages.BooleanField(4)
  list_value = messages.StringField(5, repeated=True)


class ListConfigsResponse(messages.Message):
  """ListConfigsResponse response for ProtoRPC message.

  Attributes:
    configs: ConfigResponse, The name and corresponding value being
        returned.
  """
  configs = messages.MessageField(ConfigResponse, 1, repeated=True)


class UpdateConfig(messages.Message):
  """UpdateConfig request for ProtoRPC message.

  Attributes:
    name: str, The name of the name being requested.
    config_type: ConfigType, The type of config for which to request.
    string_value: str, The string value of the name being updated.
    integer_value: int, The integer value of the name being updated.
    boolean_value: bool, The boolean value of the seting being updated.
    list_value: list, The list value of the name being updated.
  """
  name = messages.StringField(1, required=True)
  config_type = messages.EnumField(ConfigType, 2, required=True)
  string_value = messages.StringField(3)
  integer_value = messages.IntegerField(4)
  boolean_value = messages.BooleanField(5)
  list_value = messages.StringField(6, repeated=True)


class UpdateConfigRequest(messages.Message):
  """UpdateConfigRequest request for ProtoRPC message.

  Attributes:
    config: UpdateConfig, The configuration name, type, and value to update.
  """
  config = messages.MessageField(UpdateConfig, 1, repeated=True)
