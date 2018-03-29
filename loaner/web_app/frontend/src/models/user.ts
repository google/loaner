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



import {CONFIG} from '../app.config';

/**
 * Interface with fields that come from our User API.
 */
export declare interface UserApiParams {
  roles?: string[];
}

/** An user model with all its properties and methods. */
export class User {
  /** Given name of the user on Google's oauth credentials. */
  givenName = '';
  /** Email of the user on Google's oauth credentials. */
  email = '';
  /** Permission roles which the user pertains */
  roles: string[] = [];

  constructor(user: UserApiParams = {}) {
    this.roles = user.roles || this.roles;
  }

  /** Translates the User model object to the API message. */
  toApiMessage(): UserApiParams {
    return {
      roles: this.roles,
    };
  }

  get isUser(): boolean {
    return this.roles.includes(CONFIG.roles.USER);
  }

  get isTechnician(): boolean {
    return this.roles.includes(CONFIG.roles.TECHNICIAN);
  }

  get isOperationalAdmin(): boolean {
    return this.roles.includes(CONFIG.roles.OPERATIONAL_ADMIN);
  }

  get isTechnicalAdmin(): boolean {
    return this.roles.includes(CONFIG.roles.TECHNICAL_ADMIN);
  }

  hasRole(requiredRoles: string|string[]): boolean {
    if (typeof requiredRoles === 'string') {
      return this.roles.includes(requiredRoles);
    }

    let hasRole = false;
    for (const role of requiredRoles) {
      if (this.roles.includes(role)) {
        hasRole = true;
      }
    }
    return hasRole;
  }
}
