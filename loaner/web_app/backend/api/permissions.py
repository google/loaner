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


class Permissions(object):
  """Permissions for all API method calls."""
  AUDIT_SHELF = 'audit_shelf'
  BOOTSTRAP = 'bootstrap'
  CLEAR_INDICES = 'clear_indices'
  CREATE_SURVEY = 'create_survey'
  DATASTORE_IMPORT = 'datastore_import'
  DEVICE_AUDIT = 'device_audit'
  DISABLE_SHELF = 'disable_shelf'
  EDIT_SHELF = 'edit_shelf'
  ENABLE_GUEST_MODE = 'enable_guest_mode'
  ENABLE_SHELF = 'enable_shelf'
  ENROLL_DEVICE = 'enroll_device'
  ENROLL_SHELF = 'enroll_shelf'
  EXTEND_LOAN = 'extend_loan'
  GET_CONFIG = 'get_config'
  GET_DEVICE = 'get_device'
  GET_SHELF = 'get_shelf'
  GET_USER = 'get_user'
  LIST_CONFIGS = 'list_configs'
  LIST_DEVICES = 'list_devices'
  LIST_SHELVES = 'list_shelves'
  LIST_SURVEYS = 'list_surveys'
  LIST_DEVICES = 'list_devices'
  LIST_USER_DEVICES = 'list_user_devices'
  LIST_USERBYROLE = 'list_user'
  MARK_DAMAGED = 'mark_damaged'
  MARK_LOST = 'mark_lost'
  MARK_PENDING_RETURN = 'mark_pending_return'
  PATCH_SURVEY = 'patch_survey'
  REINDEX_SEARCH = 'reindex_search'
  RESPONSIBLE_FOR_AUDIT = 'responsible_for_audit'
  RESUME_LOAN = 'resume_loan'
  UNENROLL_DEVICE = 'unenroll_device'
  UPDATE_CONFIG = 'update_config'
  UPDATE_SHELF = 'update_shelf'
  UPDATE_USER = 'update_user'


ROLES = {
    'technical-admin': [
        Permissions.AUDIT_SHELF,
        Permissions.BOOTSTRAP,
        Permissions.CREATE_SURVEY,
        Permissions.CLEAR_INDICES,
        Permissions.DATASTORE_IMPORT,
        Permissions.DEVICE_AUDIT,
        Permissions.DISABLE_SHELF,
        Permissions.EDIT_SHELF,
        Permissions.ENABLE_SHELF,
        Permissions.ENROLL_DEVICE,
        Permissions.ENABLE_GUEST_MODE,
        Permissions.ENROLL_SHELF,
        Permissions.EXTEND_LOAN,
        Permissions.GET_CONFIG,
        Permissions.GET_DEVICE,
        Permissions.GET_SHELF,
        Permissions.GET_USER,
        Permissions.LIST_CONFIGS,
        Permissions.LIST_DEVICES,
        Permissions.LIST_SHELVES,
        Permissions.LIST_SURVEYS,
        Permissions.LIST_USER_DEVICES,
        Permissions.LIST_USERBYROLE,
        Permissions.MARK_DAMAGED,
        Permissions.MARK_LOST,
        Permissions.MARK_PENDING_RETURN,
        Permissions.PATCH_SURVEY,
        Permissions.REINDEX_SEARCH,
        Permissions.RESPONSIBLE_FOR_AUDIT,
        Permissions.RESUME_LOAN,
        Permissions.UNENROLL_DEVICE,
        Permissions.UPDATE_CONFIG,
        Permissions.UPDATE_SHELF,
        Permissions.UPDATE_USER
    ],
    'operational-admin': [
        Permissions.ENABLE_GUEST_MODE,
        Permissions.ENROLL_DEVICE,
        Permissions.EXTEND_LOAN,
        Permissions.GET_CONFIG,
        Permissions.GET_DEVICE,
        Permissions.GET_SHELF,
        Permissions.GET_USER,
        Permissions.LIST_CONFIGS,
        Permissions.LIST_DEVICES,
        Permissions.LIST_SHELVES,
        Permissions.LIST_USER_DEVICES,
        Permissions.LIST_USERBYROLE,
        Permissions.MARK_DAMAGED,
        Permissions.MARK_LOST,
        Permissions.MARK_PENDING_RETURN,
        Permissions.RESPONSIBLE_FOR_AUDIT,
        Permissions.RESUME_LOAN,
        Permissions.UNENROLL_DEVICE,
    ],
    'technician': [
        Permissions.AUDIT_SHELF,
        Permissions.DEVICE_AUDIT,
        Permissions.ENROLL_DEVICE,
        Permissions.GET_CONFIG,
        Permissions.GET_DEVICE,
        Permissions.GET_SHELF,
        Permissions.GET_USER,
        Permissions.LIST_CONFIGS,
        Permissions.LIST_DEVICES,
        Permissions.LIST_SHELVES,
        Permissions.LIST_USER_DEVICES,
        Permissions.RESPONSIBLE_FOR_AUDIT,
        Permissions.UNENROLL_DEVICE
    ],
    'user': [
        Permissions.ENABLE_GUEST_MODE,
        Permissions.EXTEND_LOAN,
        Permissions.GET_DEVICE,
        Permissions.LIST_USER_DEVICES,
        Permissions.MARK_DAMAGED,
        Permissions.MARK_LOST,
        Permissions.MARK_PENDING_RETURN,
        Permissions.RESUME_LOAN,
    ]
}

