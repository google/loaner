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

import {HttpEvent, HttpHandler, HttpInterceptor, HttpRequest} from '@angular/common/http';
import {Injectable, NgZone} from '@angular/core';
import {Observable, timer} from 'rxjs';
import {delayWhen, finalize, mergeMap, retryWhen, takeWhile} from 'rxjs/operators';

const MAX_RETRIES = 10;

/**
 * Intercept the HttpRequest and apply the authorization header for the
 * Chrome application.
 */
@Injectable()
export class OAuthHttpInterceptor implements HttpInterceptor {
  private accessToken!: string;
  constructor(private zone: NgZone) {}

  intercept(originalRequest: HttpRequest<{}>, next: HttpHandler):
      Observable<HttpEvent<{}>> {
    let request: HttpRequest<{}>;
    // If the request is heading to Google Analytics, do not modify the original
    // request as otherwise it would send the authorization token.
    if (originalRequest.url.match('google-analytics.com')) {
      return next.handle(originalRequest);
    }
    return this.prepareRequest(originalRequest)
        .pipe(
            mergeMap((req: HttpRequest<{}>) => {
              request = req;
              return next.handle(request);
            }),

            retryWhen((errors: Observable<{}>) => {
              let debounceTime = 100;
              return errors.pipe(
                  takeWhile((_, attemptNumber) => attemptNumber < MAX_RETRIES),
                  delayWhen(() => {
                    console.error('Retrying http connection');
                    debounceTime = debounceTime * 2;
                    return timer(debounceTime);
                  }),
                  finalize(() => {
                    console.error(`Failed to complete http connection after ${
                        MAX_RETRIES} attempts`);
                  }));
            }));
  }

  private requestAuthToken(interactive = true): Observable<string> {
    return new Observable((observer) => {
      try {
        chrome.identity.getAuthToken({interactive}, (accessToken: string) => {
          this.zone.run(() => {
            if (accessToken) {
              observer.next(accessToken);
            } else {
              throw new Error('Unable to retrieve auth token');
            }
          });
        });
      } catch (error) {
        console.info(
            'This application needs to be run as a Chrome application');
        observer.error(error);
      }
    });
  }

  private prepareRequest(originalRequest: HttpRequest<{}>):
      Observable<HttpRequest<{}>> {
    return new Observable((observer) => {
      this.requestAuthToken().subscribe(
          (authToken) => {
            this.accessToken = authToken;
            originalRequest = originalRequest.clone({
              setHeaders: {
                'Authorization': `Bearer ${this.accessToken}`,
              },
            });
            observer.next(originalRequest);
          },
          (error) => {
            observer.error(error);
          });
    });
  }
}
