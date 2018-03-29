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

import {APIService} from './config';

describe('APIService', () => {
  let api: APIService;

  const chromeEndpoint = {
    dev: 'https://chrome-loaner-dev/_ah/api',
    prod: 'https://chrome-loaner-prod/_ah/api',
  };
  const standardEndpoint = {
    dev: 'https://endpoints-loaner-dev/_ah/api',
    prod: 'https://endpoints-loaner-prod/_ah/api'
  };

  beforeEach(() => {
    api = new APIService();
    api.chromeEndpoint = chromeEndpoint;
    api.standardEndpoint = standardEndpoint;
  });

  it('should provide the correct link for chrome endpoint', () => {
    api.devTrack = true;
    expect(api.chrome()).toBe(chromeEndpoint.dev);
    api.devTrack = false;
    expect(api.chrome()).toBe(chromeEndpoint.prod);
  });

  it('should provide the correct link for standard endpoint', () => {
    api.devTrack = true;
    expect(api.endpoints()).toBe(standardEndpoint.dev);
    api.devTrack = false;
    expect(api.endpoints()).toBe(standardEndpoint.prod);
  });
});
