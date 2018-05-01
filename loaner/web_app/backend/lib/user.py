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

"""Loaner User Lib."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from google.appengine.api import users
import endpoints


class Error(Exception):
  """Default error class for this module."""


class UserNotFound(Error):
  """Raised when a user is not detected as being logged in."""


def get_user_email():
  """Retrieves the currently logged in user email.

  Returns:
    A string of the email address of the current user.

  Raises:
    UserNotFound: Raised if a user is not currently logged in.
  """

  try:
    current_user = endpoints.get_current_user() or users.get_current_user()
  except endpoints.InvalidGetUserCall:
    current_user = users.get_current_user()

  if current_user:

    return current_user.email()
  raise UserNotFound('get_user_email failed: No user account detected.')
