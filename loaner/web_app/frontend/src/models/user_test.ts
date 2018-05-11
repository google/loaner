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

  it('should verify user does not have permission', () => {
    expect(user.hasPermission(CONFIG.appPermissions.READ_SHELVES)).toBe(false);
  });

  it('should verify user does have permission', () => {
    user.permissions = [CONFIG.appPermissions.READ_SHELVES];
    expect(user.hasPermission(CONFIG.appPermissions.READ_SHELVES)).toBe(true);
  });
});
