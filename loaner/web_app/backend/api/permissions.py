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

"""Define permissions for the app APIs.

To see actual permissions please check web_app/permissions.json.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import json
import os


# Run code on import.
class Permissions(object):
  """Permissions for all API method calls."""
  ALL = []


json_path = os.path.abspath(__file__).split(os.sep)
json_path = os.path.join(os.sep.join(json_path[:-3]), 'permissions.json')
with open(json_path) as f:
  permissions_json = json.load(f)

for key, value in permissions_json.iteritems():
  setattr(Permissions, key, value)
  Permissions.ALL.append(value)
