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

import {ChromeAppPlatformLocation} from './chrome_app_platform_location';

describe('Chrome App Platform Location', () => {
  let platform: ChromeAppPlatformLocation;

  beforeEach(() => {
    platform = new ChromeAppPlatformLocation();
  });

  it('should get the window location', () => {
    expect(platform.location).toBe(window.location);
  });

  it('should get the location search paramater', () => {
    expect(platform.search).toBe(window.location.search);
  });

  it('should get the location hash', () => {
    expect(platform.hash).toBe(window.location.hash);
  });

  it('should get the location path name', () => {
    expect(platform.pathname).toBe(window.location.pathname);
  });

  it('should return the correct baseRef', () => {
    expect(platform.getBaseHrefFromDOM()).toBe('/');
  });

  it('should run pushState/replaceState and return nothing', () => {
    const params = {state: {}, title: 'test', url: '/some-url'};
    expect(platform.pushState(params.state, params.title, params.url))
        .toBe(undefined);
    expect(platform.replaceState(params.state, params.title, params.url))
        .toBe(undefined);
  });

  it('should return undefined for forward(), back()', () => {
    expect(platform.forward()).toBe(undefined);
    expect(platform.back()).toBe(undefined);
  });
});
