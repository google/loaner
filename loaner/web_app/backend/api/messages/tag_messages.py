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

"""Tag messages for Tag API."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from protorpc import messages


class Tag(messages.Message):
  """Tag ProtoRPC message.

  Attributes:
    name: str, The unique name of the tag.
    hidden: bool, Whether the tag is hidden in the frontend, defaults to False.
    color: str, The color of the tag, one of the material design color palette.
    protect: bool, Whether the tag is protected from user manipulation; this
      field will only be included in response messages.
    description: str, The description for the tag.
  """
  name = messages.StringField(1)
  hidden = messages.BooleanField(2, default=False)
  color = messages.StringField(3)
  protect = messages.BooleanField(4)
  description = messages.StringField(5)


class CreateTagRequest(messages.Message):
  """CreateTagRequest ProtoRPC message.

  Attributes:
    tag: Tag, A tag to create.
  """
  tag = messages.MessageField(Tag, 1)


class TagRequest(messages.Message):
  """TagRequest ProtoRPC message.

  Attributes:
    urlsafe_key: str, The urlsafe representation of the ndb.Key for the
      requested tag.
  """
  urlsafe_key = messages.StringField(1)
