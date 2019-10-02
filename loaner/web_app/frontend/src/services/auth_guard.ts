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
import {ActivatedRouteSnapshot, CanActivate, Router, RouterStateSnapshot} from '@angular/router';
import {of} from 'rxjs';
import {catchError, map} from 'rxjs/operators';

import {LoanerSnackBar} from './snackbar';
import {UserService} from './user';

@Injectable()
export class AuthGuard implements CanActivate {
  /** URL to navigate in case the user isn't authorized. */
  private authorizationUrl = 'authorization';

  constructor(
      private readonly snackbar: LoanerSnackBar,
      private router: Router,
      private userService: UserService,
  ) {}

  canActivate(route: ActivatedRouteSnapshot, state: RouterStateSnapshot) {
    const destinationUrl = state.url;
    return this.userService.loadUser().pipe(
        map(user => {
          const requiredPermissions =
              route.data['requiredPermissions'] as string[];
          if (!requiredPermissions) {
            return true;
          }
          const userCanAccess =
              isAllowedAccess(requiredPermissions, user.permissions);

          if (!userCanAccess) {
            if (destinationUrl.match(/^\/bootstrap/)) {
              const errorMessage =
                  `User ${user.email} is not allowed to setup the application.
                 Please contact your administator.`;
              this.snackbar.open(errorMessage, /* sticky notification */ true);
              throw new Error(errorMessage);
            } else {
              const errorMessage =
                  `User ${user.email} is not allowed to access page
                   ${destinationUrl}. Please contact your administator.`;
              this.snackbar.open(errorMessage);
              this.router.navigate(['/']);
            }
          }

          return userCanAccess;
        }),
        catchError(() => {
          this.router.navigate([this.authorizationUrl], {
            queryParams: {
              'returnUrl': destinationUrl,
            }
          });
          return of(false);
        }));
  }
}

/**
 * Return if whether a set of current permissions intersects with the allowed
 * permissions.
 *
 * @param permissionsAllowed Permissions that are allowed access.
 * @param currentPermissions Permissions that the user currently has.
 */
const isAllowedAccess =
    (permissionsAllowed: string[], currentPermissions: string[]) => {
      const intersectedPermissions =
          currentPermissions
              .reduce(
                  (acc: string[], curr) =>
                      [...acc,
                       ...permissionsAllowed.filter(
                           permission => permission.trim().toUpperCase() ===
                               curr.trim().toUpperCase())],
                  [])
              .sort();
      return intersectedPermissions.length === permissionsAllowed.length &&
          permissionsAllowed.sort().every(
              (element, index) => intersectedPermissions[index] === element);
    };
