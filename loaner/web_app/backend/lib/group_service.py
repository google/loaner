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

"""Helper service for retrieving group memebership.

This module allows integration of other grouping services. Simply replace
the logic in get_users_for_group with your own system and any time any part of
the app gets group memberships it will call this method.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from loaner.web_app import constants
from loaner.web_app.backend.clients import directory


def get_users_for_group(group_name):
  """Retrieves users for a given group.

  Args:
    group_name: str, the name of the group to get membership for.

  Returns:
    A list of all user's email addresses in the group provided.
  """
  directory_client = directory.DirectoryApiClient(
      user_email=constants.ADMIN_USERNAME)
  return directory_client.get_all_users_in_group(group_name)


