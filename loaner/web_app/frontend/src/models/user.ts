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
  }

  /** Translates the User model object to the API message. */
  toApiMessage(): UserApiParams {
    return {
      permissions: this.permissions,
    };
  }

  hasPermission(requiredPermissions: string|string[]): boolean {
    if (typeof requiredPermissions === 'string') {
      return this.permissions.includes(requiredPermissions);
    }

    let hasPermission = false;
    for (const permission of requiredPermissions) {
      if (this.permissions.includes(permission)) {
        hasPermission = true;
      }
    }
    return hasPermission;
  }
}
