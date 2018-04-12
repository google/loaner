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

"""User messages for User API."""

from protorpc import messages


class UserResponse(messages.Message):
  """UserResponse response for ProtoRPC message.

  Attributes:
    email: str, The user email to be displayed.
    roles: list|str|, The roles of the user to be displayed.
  """
  email = messages.StringField(1)
  roles = messages.StringField(2, repeated=True)
