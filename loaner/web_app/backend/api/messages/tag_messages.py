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
    urlsafe_key: str, The urlsafe representation of the ndb.Key of the tag; this
      field will only be included in response messages.
  """
  name = messages.StringField(1)
  hidden = messages.BooleanField(2, default=False)
  color = messages.StringField(3)
  protect = messages.BooleanField(4)
  description = messages.StringField(5)
  urlsafe_key = messages.StringField(6)


class CreateTagRequest(messages.Message):
  """CreateTagRequest ProtoRPC message.

  Attributes:
    tag: Tag, A tag to create.
  """
  tag = messages.MessageField(Tag, 1)


class UpdateTagRequest(messages.Message):
  """UpdateTagRequest ProtoRPC message.

  Attributes:
    tag: Tag, A tag to update.
  """
  tag = messages.MessageField(Tag, 1)


class TagRequest(messages.Message):
  """TagRequest ProtoRPC message.

  Attributes:
    urlsafe_key: str, The urlsafe representation of the ndb.Key for the
      requested tag.
  """
  urlsafe_key = messages.StringField(1)


class ListTagRequest(messages.Message):
  """ListTagRequest ProtoRPC message.

  Attributes:
    page_size: int, The number of results to return.
    cursor: str, The base64-encoded cursor string specifying where to start the
      query.
    page_index: int, A human-readable page index to navigate to that will be
      used in the calculation of the offset.
    include_hidden_tags: bool, Whether to include hidden tags in the results.
  """
  page_size = messages.IntegerField(1, default=10)
  cursor = messages.StringField(2)
  page_index = messages.IntegerField(3, default=1)
  include_hidden_tags = messages.BooleanField(4, default=False)


class ListTagResponse(messages.Message):
  """ListTagResponse ProtoRPC message.

  Attributes:
    tags: List[Tag], The list of tags being returned.
    cursor: str, The base64-encoded cursor string denoting the position of the
      last result retrieved.
    has_additional_results: bool, Whether there are additional results to be
      retrieved.
  """
  tags = messages.MessageField(Tag, 1, repeated=True)
  cursor = messages.StringField(2)
  has_additional_results = messages.BooleanField(3)
  total_pages = messages.IntegerField(4)


class TagData(messages.Message):
  """TagData ProtoRPC message.

  Attributes:
    tag: Tag, an instance of a Tag entity.
    more_info: str, an informational field about this particular tag reference.
  """
  tag = messages.MessageField(Tag, 1)
  more_info = messages.StringField(2)
