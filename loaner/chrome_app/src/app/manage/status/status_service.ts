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
import {Observable, of, throwError} from 'rxjs';
import {catchError, take} from 'rxjs/operators';

import {Storage} from '../../shared/storage/storage';

/**
 * Service to communicate with the status component.
 */
@Injectable()
export class StatusService {
  constructor(private readonly storage: Storage) {}

  /**
   * Sets the given name to be displayed for a user on a loaner.
   * @param name string represents the name to store in Chrome Storage.
   */
  setGivenNameInChromeStorage(name: string) {
    this.storage.local.set('givenName', name);
  }

  /**
   * Gets the given name to be displayed for a user on a loaner.
   */
  getGivenNameFromChromeStorage(): Observable<string> {
    return this.storage.local.get('givenName')
        .pipe(
            take(1),
            catchError(() => throwError('Unable to obtain a given name')));
  }
}

/**
 * Mock of StatusService since we use Chrome API's.
 */
@Injectable()
export class StatusServiceMock extends StatusService {
  name: string;
  /**
   * Sets the given name to be displayed for a user on a loaner.
   * @param name string represents the name to store in Chrome Storage.
   */
  setGivenNameInChromeStorage(name: string) {
    this.name = name;
    console.info(`Setting givenName to ${name}`);
  }

  /**
   * Gets the given name to be displayed for a user on a loaner.
   */
  getGivenNameFromChromeStorage(): Observable<string> {
    return of(this.name);
  }
}
