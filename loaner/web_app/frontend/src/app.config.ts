// Copyright 2018 Google Inc. All Rights Reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS-IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import {ConfigService, PROGRAM_NAME} from '../../../shared/config';

export interface Permissions {
  ADMINISTRATE_LOAN: string;
  AUDIT_DEVICE: string;
  AUDIT_SHELF: string;
  BOOTSTRAP: string;
  CLEAR_INDICES: string;
  DATASTORE_IMPORT: string;
  READ_CONFIGS: string;
  READ_DEVICES: string;
  READ_SHELVES: string;
  READ_SURVEYS: string;
  MODIFY_CONFIG: string;
  MODIFY_DEVICE: string;
  MODIFY_ROLE: string;
  MODIFY_SHELF: string;
  MODIFY_SURVEY: string;
  MODIFY_TAG: string;
  REINDEX_SEARCH: string;
}

/**
 * Contains permissions for the app to render the elements in the frontend.
 *
 * This schema must match the schema on web_app/backend/auth/permissions.py file
 * or the elements won't be able to be rendered correctly.
 */
export const APPLICATION_PERMISSIONS: Permissions = {
  ADMINISTRATE_LOAN: 'administrate_loan',
  AUDIT_DEVICE: 'audit_device',
  AUDIT_SHELF: 'audit_shelf',
  BOOTSTRAP: 'bootstrap',
  CLEAR_INDICES: 'clear_indices',
  DATASTORE_IMPORT: 'datastore_import',
  READ_CONFIGS: 'read_configs',
  READ_DEVICES: 'read_devices',
  READ_SHELVES: 'read_shelves',
  READ_SURVEYS: 'read_surveys',
  MODIFY_CONFIG: 'modify_config',
  MODIFY_DEVICE: 'modify_device',
  MODIFY_ROLE: 'modify_role',
  MODIFY_SHELF: 'modify_shelf',
  MODIFY_SURVEY: 'modify_survey',
  MODIFY_TAG: 'modify_tag',
  REINDEX_SEARCH: 'reindex_search',
};

/**
 * Configuration object with environment specific variables.
 */
export interface Config {
  appName: string;
  endpointsHostname: string;
  apiName?: string;
  apiVersion?: string;
  gapiClientId: string;
  scope: string[];
  appPermissions: Permissions;
}

/** Default configuration for the application with dev default values. */
export const CONFIG: Config = {
  appName: PROGRAM_NAME || 'Grab n Go',
  endpointsHostname: new ConfigService().endpointsApiUrl || '',
  apiName: 'loaner',
  apiVersion: 'v1',
  gapiClientId: new ConfigService().webClientId || '',
  scope: ['email'],
  appPermissions: APPLICATION_PERMISSIONS,
};
