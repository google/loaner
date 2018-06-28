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

import {HttpClient, HttpHeaders} from '@angular/common/http';
import {Injectable} from '@angular/core';
import {Observable, of} from 'rxjs';
import {skipWhile, switchMap, tap} from 'rxjs/operators';

import {ConfigService} from '../../../../../shared/config';

import {Storage} from '../storage/storage';

@Injectable()
export class AnalyticsService {
  constructor(
      private readonly config: ConfigService,
      private readonly http: HttpClient,
      private readonly storage: Storage,
  ) {}

  /**
   * Generates a UUID for Google Analytics to use.
   *
   * Much of this is adapted from:
   * https://github.com/googlearchive/chrome-platform-analytics/blob/master/src/internal/identifier.js
   * @returns UUID for usage with Google Analytics.
   */
  generateUuid() {
    const format = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx';
    const chars = format.split('');

    for (let i = 0, length = chars.length; i < length; i++) {
      switch (chars[i]) {
        case 'x':
          chars[i] = Math.floor(Math.random() * 16).toString(16);
          break;
        case 'y':
          chars[i] = (Math.floor(Math.random() * 4) + 8).toString(16);
          break;
        default:
          break;
      }
    }

    return chars.join('');
  }

  retrieveUuid(): Observable<string> {
    return this.storage.local.get('analyticsID').pipe(tap(analyticsID => {
      if (!analyticsID) {
        const generatedId = this.generateUuid();
        this.storage.local.set('analyticsID', generatedId);
        return generatedId;
      } else {
        return analyticsID;
      }
    }));
  }

  /**
   * Updates the view and reports it to Google Analytics.
   * @param flow represents the current flow that the app is on.
   * @param pageView represents the page/view that the app is on.
   * @returns Blob of Google Analytics image to attach to the embedded image.
   */
  sendView(flow: string, pageView: string): Observable<Blob> {
    const httpOptions = {
      headers: new HttpHeaders({
        'Content-Type': 'application/json',
      }),
      responseType: 'blob' as 'json',
    };
    const structuredView = `chrome_app/${flow}${pageView}`;
    if (this.config.analyticsEnabled) {
      // Confirm that cid is defined, otherwise skip it until it is defined.
      return this.retrieveUuid().pipe(
          skipWhile(cid => cid === undefined),
          switchMap(
              cid => this.http.get<Blob>(
                  `https://www.google-analytics.com/collect?payload_data&cid=${
                      cid}&dp=${structuredView}&t=pageview&tid=${
                      this.config.analyticsId}&v=1`,
                  httpOptions)));
    }
    return new Observable<Blob>();
  }
}

@Injectable()
export class AnalyticsServiceMock extends AnalyticsService {
  // Fake image that we would usually receive from Google Analytics.
  fakeBlob = new Blob([''], {'type': 'image/gif'});

  sendView(pageView: string): Observable<Blob> {
    return of(this.fakeBlob);
  }
}
