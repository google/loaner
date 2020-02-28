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

import {Injectable} from '@angular/core';
import {map, tap} from 'rxjs/operators';

import {GetRoleRequestApiParams, ListRolesResponse, ListRolesResponseApiParams, Role, RoleApiParams} from '../models/role';

import {ApiService} from './api';

/** A role service that manages API calls for the backend. */
@Injectable()
export class RoleService extends ApiService {
  /** Implements ApiService's apiEndpoint requirement. */
  apiEndpoint = 'role';

  create(role: Role) {
    const params: RoleApiParams = role.toApiMessage();
    return this.post<void>('create', params).pipe(tap(() => {
      this.snackBar.open(`Role ${role.name} created.`);
    }));
  }

  update(role: Role) {
    const params: RoleApiParams = role.toApiMessage();
    return this.post<void>('update', params).pipe(tap(() => {
      this.snackBar.open(`Role ${role.name} has been updated.`);
    }));
  }

  getRole(role: Role) {
    const request: GetRoleRequestApiParams = {name: role.name};
    return this.get<RoleApiParams>('get', request)
        .pipe(map((retrievedRole: RoleApiParams) => new Role(retrievedRole)));
  }

  list() {
    return this.post<ListRolesResponseApiParams>('list').pipe(map(res => {
      const roles = res.roles && res.roles.map(role => new Role(role)) || [];
      const retrievedRoles: ListRolesResponse = {
        roles,
      };
      return retrievedRoles;
    }));
  }

  delete(role: Role) {
    const params: RoleApiParams = role.toApiMessage();
    return this.post<void>('delete', params).pipe(tap(() => {
      this.snackBar.open(`Role ${role.name} has been destroyed.`);
    }));
  }
}
