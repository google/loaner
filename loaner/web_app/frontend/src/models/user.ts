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



/**
 * Interface with fields that come from our User API.
 */
export declare interface UserApiParams {
  permissions?: string[];
  superadmin?: boolean;
}

/** An user model with all its properties and methods. */
export class User {
  /** Given name of the user on Google's oauth credentials. */
  givenName = '';
  /** Email of the user on Google's oauth credentials. */
  email = '';
  /** Roles the user has. Only used in configuration view, not authorization. */
  roles: string[] = [];
  /** Permissions the user has. Used to route/enable/disable page elements. */
  permissions: string[] = [];
  /** If user is superadmin. Only used in configuration view. */
  superadmin = false;

  constructor(user: UserApiParams = {}) {
    this.permissions = user.permissions || this.permissions;
    this.superadmin = user.superadmin || this.superadmin;
  }

  /** Translates the User model object to the API message. */
  toApiMessage(): UserApiParams {
    return {
      permissions: this.permissions,
    };
  }

  /**
   * Checks if the user has one or more of the given permissions.
   * @param anyRequiredPermissions one or more permission to match.
   */
  hasAnyPermission(...anyRequiredPermissions: string[]): boolean {
    return anyRequiredPermissions.some(
        permission => this.permissions.includes(permission));
  }

  /**
   * Checks if the user has all of the given permissions.
   * @param allRequiredPermissions one or more permissions to match.
   */
  hasAllPermissions(...allRequiredPermissions: string[]): boolean {
    return allRequiredPermissions.every(
        permission => this.permissions.includes(permission));
  }

  /** Alias method for hasAllPermissions. */
  hasPermission = this.hasAllPermissions;
}
