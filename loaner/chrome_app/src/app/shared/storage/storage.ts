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

/// <reference types="chrome-apps" />

import {Injectable} from '@angular/core';
import {Observable} from 'rxjs';

export declare interface Data {
  [key: string]: string;
}

export declare interface DataLoanerStorage {
  [key: string]: LoanerStorage;
}

/**
 * Read and write to a number of local storage devices.
 */
@Injectable()
export class Storage {
  private readonly chromeLocalStorage: ChromeLocalStorage;

  get local() {
    return this.chromeLocalStorage;
  }

  constructor() {
    this.chromeLocalStorage = new ChromeLocalStorage();
  }
}

export class ChromeLocalStorage {
  constructor() {
    this.checkForLocalStorage();
  }

  /**
   * Retrieve a given value from chrome.storage.local.
   * @param key Key for values to retrieve from storage.
   */
  get(key: string): Observable<string> {
    return new Observable(observer => {
      // Fetch initial value from local storage.
      chrome.storage.local.get([key], (result: Data) => {
        observer.next(result[key]);
      });
      // Listen for new changes and push next in observable.
      chrome.storage.onChanged.addListener((changes, namespace) => {
        if (namespace === 'local' && changes[key] !== undefined) {
          observer.next(changes[key].newValue as string);
        }
      });
    });
  }

  /**
   * Retrieve a given value from chrome.storage.local of type LoanerStorage.
   * @param key Key for values to retrieve from storage.
   */
  getLoanerStorage(key: string): Observable<LoanerStorage> {
    return new Observable(observer => {
      // Fetch initial value from local storage.
      chrome.storage.local.get([key], (result: DataLoanerStorage) => {
        observer.next(result[key]);
      });
      // Listen for new changes and push next in observable.
      chrome.storage.onChanged.addListener((changes, namespace) => {
        if (namespace === 'local' && changes[key] !== undefined) {
          observer.next(changes[key].newValue as LoanerStorage);
        }
      });
    });
  }

  /**
   * Set a value at a given key location in chrome.storage.local.
   * @param key Key for value to set in storage.
   * @param value Value to place at key location.
   */
  set(key: string, value: {}) {
    chrome.storage.local.set({[key]: value});
  }

  /**
   * Check if chrome.storage.local exists and can be used.
   */
  private checkForLocalStorage() {
    try {
      return typeof chrome.storage['local'] !== 'undefined' &&
          chrome.storage['local'] !== null;
    } catch (e) {
      return e instanceof DOMException;
    }
  }
}
