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

import {HttpClient} from '@angular/common/http';
import {Injectable} from '@angular/core';
import {Observable, of, ReplaySubject, throwError} from 'rxjs';
import {map, switchMap} from 'rxjs/operators';

import {User} from '../models/user';

import {ApiService} from './api';
import {AuthService} from './auth';
import {LoanerSnackBar} from './snackbar';

/** Class to connect to the backend's User Service API methods. */
@Injectable()
export class UserService extends ApiService {
  /** Implements ApiService's apiEndpoint requirement. */
  apiEndpoint = 'user';
  /** User instance of the current logged in user. */
  user!: User;
  /** A subject sending the loaded user. */
  private userLoadedSubject = new ReplaySubject<User>(1);

  constructor(
      private readonly authService: AuthService,
      snackbar: LoanerSnackBar,
      http: HttpClient,
  ) {
    super(snackbar, http);
    this.loadUser();
  }

  /**
   * Retrieves the current logged in user's role.
   *
   * @param shouldNotify If whether the user should be notified case the API
   *  call fails. Defaults to true.
   */
  private getUser(shouldNotify = true): Observable<User> {
    return this.get<User>('get', {}, shouldNotify)
        .pipe(map(response => new User(response)));
  }

  /** Returns a observable for when the user info is loaded in the service. */
  whenUserLoaded(): Observable<User> {
    return this.userLoadedSubject.asObservable();
  }

  /**
   * Loads user info from gapi library and from GnG's user API.
   *
   * @returns Observable of user logged in with gapi and internal app info.
   *    Steps:
   *    First we make sure gapi library is loaded.
   *    After loaded, if user isn't signed in, redirects to authorization.
   *    If already signed in, user information is fetch from Google credentials,
   *    Loads user information from GnG endpoints API.
   */
  loadUser(): Observable<User> {
    if (this.user) {
      return this.userLoadedSubject.asObservable();
    }

    return this.authService.whenLoaded().pipe(
        switchMap(() => {
          if (!this.authService.isSignedIn) {
            return throwError('Client not signed in. Redirecting.');
          }
          return this.authService.whenSignedIn();
        }),
        switchMap((user: gapi.auth2.GoogleUser) => {
          this.user = new User();
          this.user.email = user.getBasicProfile().getEmail();
          this.user.givenName = user.getBasicProfile().getGivenName();
          return this.getUser();
        }),
        switchMap(user => {
          this.user.permissions = user.permissions;
          this.user.superadmin = user.superadmin;
          this.userLoadedSubject.next(this.user);
          this.userLoadedSubject.complete();
          return of(this.user);
        }),
    );
  }
}
