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

"""Template messages for Template API."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from protorpc import messages


class TemplateType(messages.Enum):
  TITLE = 1
  BODY = 2


class Template(messages.Message):
  """ConfigResponse response for ProtoRPC message.

  Attributes:
    name: str, The name of the name being requested.
    body: str, the text of the body.
    title: str, the subject line or title of the template.
  """
  name = messages.StringField(1)
  body = messages.StringField(2)
  title = messages.StringField(3)


class ListTemplatesResponse(messages.Message):
  """ListTemplatesResponse response for ProtoRPC message.

  Attributes:
    configs: TemplateResponse, The name and corresponding value being
        returned.
  """
  templates = messages.MessageField(Template, 1, repeated=True)


class UpdateTemplate(messages.Message):
  """UpdateConfig request for ProtoRPC message.

  Attributes:
    name: str, The name of the name being requested.
    body: str, the text of the body.
    title: str, the subject line or title of the template.
  """
  name = messages.StringField(1)
  body = messages.StringField(2)
  title = messages.StringField(3)


class UpdateTemplateRequest(messages.Message):
  """UpdateTemplateRequest request for ProtoRPC message.

  Attributes:
    name: str, The name of the name being requested.
    body: str, the text of the body.
    title: str, the subject line or title of the template.
  """
  name = messages.StringField(1)
  body = messages.StringField(2)
  title = messages.StringField(3)


class RemoveTemplateRequest(messages.Message):
  """UpdateTemplateRequest request for ProtoRPC message.

  Attributes:
    name: The template to remove / delete.
  """
  name = messages.StringField(1)


class CreateTemplateRequest(messages.Message):
  """CreateTemplateRequest ProtoRPC message.

  Attributes:
    template: Template, A Template to create.
  """
  template = messages.MessageField(Template, 1)
