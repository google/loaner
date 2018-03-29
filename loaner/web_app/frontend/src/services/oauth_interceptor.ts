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
import {Injectable} from '@angular/core';
import {Observable} from 'rxjs/Observable';
import {mergeMap} from 'rxjs/operators';

import {CONFIG} from '../app.config';

import {AuthService, Token} from './auth';

/**
 * Urls that will have the Authorization header added.
 */
const INTERCEPT_URLS = [
  `${CONFIG.endpointsHostname}/_ah/api/${CONFIG.apiName}/${CONFIG.apiVersion}/`,
];

/**
 * Urls that will NOT have the Authorization header added.
 * Primarily used for URLs that have the same base as an INTERCEPT_URL but are
 * more specific.
 */
const EXCLUDED_INTERCEPT_URLS: string[] = [
  // Left blank intentionally for the moment.
];

/**
 * Intercept the HttpRequest and apply the authorization header for the
 * frontend application.
 */
@Injectable()
export class LoanerOAuthInterceptor implements HttpInterceptor {
  private authToken: string;
  private authExpirationTime: number;
  private urlsToIntercept: string[];
  private excludedUrlsToIntercept: string[];

  constructor(private readonly authService: AuthService) {
    this.urlsToIntercept = INTERCEPT_URLS;
    this.excludedUrlsToIntercept = EXCLUDED_INTERCEPT_URLS;

    this.authService.tokenSubject.subscribe((newToken: Token) => {
      this.authToken = newToken.id;
      this.authExpirationTime = newToken.expirationTime;
    });
  }

  /**
   * Intercept the HttpRequest and modify it's headers.
   * @param originalRequest The original Http request.
   * @param next HttpHandler of the next action/request.
   */
  intercept(originalRequest: HttpRequest<{}>, next: HttpHandler):
      Observable<HttpEvent<{}>> {
    if (this.isInterceptableUrl(originalRequest.url)) {
      let request: HttpRequest<{}>;
      return this.prepareRequest(originalRequest)
          .pipe(mergeMap((req: HttpRequest<{}>) => {
            request = req;
            return next.handle(request);
          }));
    } else {
      return next.handle(originalRequest);
    }
  }

  /**
   * Append the auth token to the headers of the original request.
   * @param originalRequest The original Http request.
   */
  private prepareRequest(originalRequest: HttpRequest<{}>):
      Observable<HttpRequest<{}>> {
    return new Observable(observer => {
      if (this.authExpirationTime < Date.now()) {
        this.authService.reloadAuth();
      }

      if (this.authToken) {
        originalRequest = originalRequest.clone({
          setHeaders: {
            'Authorization': `Bearer ${this.authToken}`,
          }
        });
      }
      observer.next(originalRequest);
    });
  }

  /**
   * Checks if the requestURL can be intercepted.
   * @param url String value of the URL to be checked.
   */
  private isInterceptableUrl(url: string): boolean {
    let isOnExcludeList = false;
    // Check first if it's an excluded URL.
    for (const disallowed of this.excludedUrlsToIntercept) {
      if (disallowed.search(url) || disallowed === url) {
        isOnExcludeList = true;
      }
    }
    // If it is not an excluded URL then proceed checking for interceptable URLs
    if (!isOnExcludeList) {
      for (const allowed of this.urlsToIntercept) {
        if (allowed.search(url) || allowed === url) {
          return true;
        }
      }
    }
    return false;
  }
}
