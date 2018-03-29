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
    user = new User({
      roles: [CONFIG.roles.USER],
    });
  });

  it('should verify user isUser', () => {
    expect(user.isUser).toBe(true);
    user.roles = [];
    expect(user.isUser).toBe(false);
  });

  it('should verify user isTechnician', () => {
    expect(user.isTechnician).toBe(false);
    user.roles.push(CONFIG.roles.TECHNICIAN);
    expect(user.isTechnician).toBe(true);
  });

  it('should verify user isOperationalAdmin', () => {
    expect(user.isOperationalAdmin).toBe(false);
    user.roles.push(CONFIG.roles.OPERATIONAL_ADMIN);
    expect(user.isOperationalAdmin).toBe(true);
  });

  it('should verify user isTechnician', () => {
    expect(user.isTechnicalAdmin).toBe(false);
    user.roles.push(CONFIG.roles.TECHNICAL_ADMIN);
    expect(user.isTechnicalAdmin).toBe(true);
  });

  it('should verify user has roles', () => {
    expect(user.hasRole(CONFIG.roles.TECHNICAL_ADMIN)).toBe(false);
    expect(user.hasRole(CONFIG.roles.USER)).toBe(true);
    user.roles.push(CONFIG.roles.TECHNICAL_ADMIN);
    expect(user.hasRole(CONFIG.roles.TECHNICAL_ADMIN)).toBe(true);
  });
});
