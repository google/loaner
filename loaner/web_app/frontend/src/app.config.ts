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

import {APIService, PROGRAM_NAME, WEB_APP_CLIENT_ID} from '../../../shared/config';

export interface Roles {
  USER: string;
  TECHNICIAN: string;
  OPERATIONAL_ADMIN: string;
  TECHNICAL_ADMIN: string;
}

/**
 * Contains roles for the app to render the elements in the frontend.
 *
 * This schema must match the schema on web_app/backend/auth/permissions.py file
 * or the elements won't be able to be rendered correctly.
 */
export const applicationRoles: Roles = {
  USER: 'user',
  TECHNICIAN: 'technician',
  OPERATIONAL_ADMIN: 'operational-admin',
  TECHNICAL_ADMIN: 'technical-admin',
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
  roles: Roles;
}

/** Default configuration for the application with dev default values. */
export const CONFIG: Config = {
  appName: PROGRAM_NAME || 'Grab n Go',
  endpointsHostname: new APIService().endpoints() || '',
  apiName: 'loaner',
  apiVersion: 'v1',
  gapiClientId: WEB_APP_CLIENT_ID || '',
  scope: ['email'],
  roles: applicationRoles,
};
