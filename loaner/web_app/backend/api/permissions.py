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

There are four main roles: Technical Admin, Operational Admin, Technician, and
Assignee. Each has a predefined set of permissions defined below. The
api.auth.method decorator checks to see if a user has permission to execute each
method.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


class Permissions(object):
  """Permissions for all API method calls."""
  ADMINISTRATE_LOAN = 'administrate_loan'
  AUDIT_SHELF = 'audit_shelf'
  BOOTSTRAP = 'bootstrap'
  CLEAR_INDICES = 'clear_indices'
  DATASTORE_IMPORT = 'datastore_import'
  READ_CONFIGS = 'read_configs'
  READ_DEVICES = 'read_devices'
  READ_ROLES = 'read_roles'
  READ_SHELVES = 'read_shelves'
  READ_SURVEYS = 'read_surveys'
  MODIFY_CONFIG = 'modify_config'
  MODIFY_DEVICE = 'modify_device'
  MODIFY_ROLE = 'modify_role'
  MODIFY_SHELF = 'modify_shelf'
  MODIFY_SURVEY = 'modify_survey'
  REINDEX_SEARCH = 'reindex_search'


Permissions.ALL = [
    getattr(Permissions, x) for x in dir(Permissions) if not x.startswith('__')
]
