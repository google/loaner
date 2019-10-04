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

import {Component} from '@angular/core';
import {async, TestBed} from '@angular/core/testing';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {ActivatedRouteSnapshot, RouterStateSnapshot} from '@angular/router';
import {RouterTestingModule} from '@angular/router/testing';
import {of} from 'rxjs';

import {CONFIG} from '../app.config';
import {MaterialModule} from '../core/material_module';
import {User} from '../models/user';
import {UserServiceMock} from '../testing/mocks';

import {AuthGuard} from './auth_guard';
import {LoanerSnackBar} from './snackbar';
import {UserService} from './user';

@Component({
  template: `never-used`,
})
class DummyAuthComponent {
}

describe('AuthGuard service', () => {
  let authGuard: AuthGuard;
  let userService: UserService;
  const stateMock = jasmine.createSpyObj<RouterStateSnapshot>(
      'RouterStateSnapshot', ['toString']);
  const activatedRouteMock = new ActivatedRouteSnapshot();

  beforeEach(() => {
    TestBed
        .configureTestingModule({
          declarations: [DummyAuthComponent],
          imports: [
            BrowserAnimationsModule,
            RouterTestingModule.withRoutes([
              {path: 'authorization', component: DummyAuthComponent},
            ]),
            MaterialModule,
          ],
          providers: [
            AuthGuard,
            LoanerSnackBar,
            {provide: UserService, useClass: UserServiceMock},
            {provide: RouterStateSnapshot, useValue: stateMock},
          ],
        })
        .compileComponents();

    authGuard = TestBed.get(AuthGuard);
    userService = TestBed.get(UserService);
  });

  it('returns true with all permissions are passed.', async(() => {
       spyOn(userService, 'loadUser').and.returnValue(of(new User({
         'permissions': [
           CONFIG.appPermissions.READ_DEVICES,
           CONFIG.appPermissions.READ_SHELVES,
         ],
       })));
       activatedRouteMock.data = {
         'requiredPermissions': [
           CONFIG.appPermissions.READ_SHELVES,
           CONFIG.appPermissions.READ_DEVICES,
         ],
       };
       authGuard.canActivate(activatedRouteMock, stateMock)
           .subscribe(canActivateRoute => {
             expect(canActivateRoute).toBeTruthy();
           });
     }));

  it('returns false with none permissions passed.', async(() => {
       spyOn(userService, 'loadUser').and.returnValue(of(new User({
         'permissions': [],
       })));
       activatedRouteMock.data = {
         'requiredPermissions': [
           CONFIG.appPermissions.READ_DEVICES,
           CONFIG.appPermissions.READ_SHELVES,
         ],
       };
       authGuard.canActivate(activatedRouteMock, stateMock)
           .subscribe(canActivateRoute => {
             expect(canActivateRoute).toBeFalsy();
           });
     }));

  it('returns false with one of permissions passed.', async(() => {
       spyOn(userService, 'loadUser').and.returnValue(of(new User({
         'permissions': [
           CONFIG.appPermissions.READ_SHELVES,
         ],
       })));
       activatedRouteMock.data = {
         'requiredPermissions': [
           CONFIG.appPermissions.READ_DEVICES,
           CONFIG.appPermissions.READ_SHELVES,
         ],
       };
       authGuard.canActivate(activatedRouteMock, stateMock)
           .subscribe(canActivateRoute => {
             expect(canActivateRoute).toBeFalsy();
           });
     }));
});
