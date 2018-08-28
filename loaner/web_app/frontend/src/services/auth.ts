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

import {Injectable, NgZone} from '@angular/core';
import {Observable, of, ReplaySubject} from 'rxjs';
import {switchMap} from 'rxjs/operators';

import {CONFIG} from '../app.config';

import {LoanerSnackBar} from './snackbar';

export declare interface Token {
  id: string;
  expirationTime: number;
}

// tslint:disable-next-line:no-any Declaration of window.gapi for gapi client.
const gapi = (window as any)['gapi'];
/* How many minutes before oauth expiring we want to force a refresh. */
const FIVE_MINUTES_IN_MILLISECONDS = 5 * 60 * 1000;

/** Authentication service that loads and holds states of the gapi client. */
@Injectable()
export class AuthService {
  /** Whether the user is currently signed into OAuth. */
  isSignedIn = false;
  /** Logged in user token ID. */
  token!: string;
  /** Time at which token will expire in the next 5 minutes. */
  tokenExpirationTime!: number;
  /** Whether the API has completed loading. */
  loaded = false;
  /** A subject the latest token id retrieved from gapi. */
  tokenSubject = new ReplaySubject<Token>(1);
  /** A subject sending a boolean whether the api is loaded. */
  private apiLoadedSubject = new ReplaySubject<boolean>(1);
  /** A subject sending a the client that's signed in. */
  private isSignedInSubject = new ReplaySubject<gapi.auth2.GoogleUser>(1);
  /** The GoogleAuth instance. */
  private authInstance!: gapi.auth2.GoogleAuth;
  /** The GoogleUser instance of the current user logged in. */
  private currentUser!: gapi.auth2.GoogleUser;

  constructor(
      private readonly ngZone: NgZone,
      private readonly snackbar: LoanerSnackBar,
  ) {
    if (!this.loaded) {
      this.loadClient();
    }
  }

  /** Loads thee gapi oauth client. */
  private loadClient() {
    gapi['load']('client:auth2', this.initClient.bind(this));
  }

  /** Inits Google gapi library with application's credentials. */
  private initClient() {
    gapi['client']['init']({
      discoveryDocs: [
        `${CONFIG.endpointsHostname}/discovery/v1/apis/${CONFIG.apiName}/${
            CONFIG.apiVersion}/rest`,
      ],
      clientId: CONFIG.gapiClientId,
      scope: CONFIG.scope.join(' ')
    })
        .then(
            () => {
              this.loaded = true;
              this.authInstance = gapi.auth2.getAuthInstance();

              // Listen for sign-in state changes.
              this.authInstance.isSignedIn.listen(
                  this.updateSigninStatus.bind(this));

              // Handle the initial sign-in state.
              this.updateSigninStatus(this.authInstance.isSignedIn.get());

              this.ngZone.run(() => {
                this.apiLoadedSubject.next(this.loaded);
                this.apiLoadedSubject.complete();
              });
            },
            // tslint:disable-next-line:no-any Promise rejection is type any.
            (error: any) => {
              if (error && error.details) {
                this.snackbar.open(
                    error.details, /* sticky notification */ true);
              }

              throw error;
            });
  }

  private updateToken(token: Token) {
    this.token = token.id;
    this.tokenExpirationTime =
        token.expirationTime - FIVE_MINUTES_IN_MILLISECONDS;
    this.tokenSubject.next(token);
  }

  /** Returns a stream of the client's loading status. */
  whenLoaded(): Observable<boolean> {
    return this.apiLoadedSubject.asObservable();
  }

  /** Returns a stream of the client's signin status. */
  whenSignedIn(): Observable<gapi.auth2.GoogleUser> {
    return this.isSignedInSubject.asObservable();
  }

  /** Reloads the token ID with gapi client. */
  reloadAuth() {
    this.currentUser.reloadAuthResponse().then(newAuthResponse => {
      const token: Token = {
        id: newAuthResponse.access_token,
        expirationTime: newAuthResponse.expires_at,
      };
      this.updateToken(token);
    });
  }

  /** Updates the sign in status based on the signin result. */
  updateSigninStatus(isSignedIn: boolean) {
    if (isSignedIn) {
      this.isSignedIn = isSignedIn;
      this.currentUser = this.authInstance.currentUser.get();

      const authResponse = this.currentUser.getAuthResponse();

      this.updateToken({
        id: authResponse.access_token,
        expirationTime: authResponse.expires_at,
      });

      this.isSignedInSubject.next(this.currentUser);
    }
  }

  getUserObservable(): Observable<gapi.auth2.GoogleUser> {
    return this.isSignedInSubject.asObservable().pipe(
        switchMap(() => of(this.currentUser)));
  }

  signIn() {
    return this.authInstance.signIn();
  }

  signOut() {
    this.authInstance.signOut();
  }
}
