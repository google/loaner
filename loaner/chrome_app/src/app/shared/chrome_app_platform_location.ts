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

import {LocationChangeListener, PlatformLocation} from '@angular/common';

/**
 * A platform location implementation for a Chrome OS app to prevent calls
 * to history.
 */
export class ChromeAppPlatformLocation extends PlatformLocation {
  private appLocation: Location;

  constructor() {
    super();
    this.appLocation = window.location;
  }

  get location() {
    return this.appLocation;
  }
  get search(): string {
    return this.appLocation.search;
  }
  get hash(): string {
    return this.appLocation.hash;
  }
  get pathname(): string {
    return this.appLocation.pathname;
  }
  set pathname(newPath: string) {
    this.appLocation.pathname = newPath;
  }

  getBaseHrefFromDOM() {
    return '/';
  }

  onPopState(fn: LocationChangeListener): void {}

  onHashChange(fn: LocationChangeListener): void {}

  pushState(state: {}, title: string, url: string) {
    return;
  }

  replaceState(state: {}, title: string, url: string) {
    return;
  }

  forward(): void {
    return;
  }

  back(): void {
    return;
  }
}
