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
import {User} from './user';


describe('UserModel', () => {
  let user: User;

  beforeEach(() => {
    user = new User();
  });

  it('requires all permissions on hasAllPermissions', () => {
    user.permissions = [
      CONFIG.appPermissions.READ_SHELVES,
      CONFIG.appPermissions.READ_DEVICES,
    ];

    expect(user.hasAllPermissions(
               CONFIG.appPermissions.READ_SHELVES,
               ))
        .toBe(true);
    expect(user.hasAllPermissions(
               CONFIG.appPermissions.READ_SHELVES,
               CONFIG.appPermissions.READ_DEVICES))
        .toBe(true);
    expect(user.hasAllPermissions(
               CONFIG.appPermissions.READ_SHELVES,
               CONFIG.appPermissions.READ_DEVICES,
               CONFIG.appPermissions.READ_SURVEYS))
        .toBe(false);
    expect(user.hasAllPermissions(CONFIG.appPermissions.READ_SURVEYS))
        .toBe(false);
  });

  it('requires any permission on hasAnyPermission', () => {
    user.permissions = [
      CONFIG.appPermissions.READ_CONFIGS,
      CONFIG.appPermissions.READ_DEVICES,
      CONFIG.appPermissions.READ_SHELVES,
    ];
    expect(user.hasAnyPermission(CONFIG.appPermissions.READ_DEVICES))
        .toBe(true);
    expect(user.hasAnyPermission(
               CONFIG.appPermissions.READ_DEVICES,
               CONFIG.appPermissions.READ_SHELVES))
        .toBe(true);
    expect(user.hasAnyPermission(
               CONFIG.appPermissions.READ_SURVEYS,
               CONFIG.appPermissions.READ_CONFIGS,
               ))
        .toBe(true);
    expect(user.hasAnyPermission(CONFIG.appPermissions.READ_SURVEYS))
        .toBe(false);
  });

  it('aliases hasPermission to hasAllPermissions', () => {
    expect(user.hasPermission).toBe(user.hasAllPermissions);
  });
});
