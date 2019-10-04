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

import {TestBed} from '@angular/core/testing';

import {CHROME_MODE, ConfigService} from './config';

describe('ConfigService', () => {
  let config: ConfigService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [ConfigService],
    });
    config = TestBed.get(ConfigService);
  });

  it('provides the correct link for chrome/endpoints apis if on prod', () => {
    config.ON_LOCAL = false;
    config.ON_DEV = false;
    config.ON_QA = false;
    config.ON_PROD = true;
    config.IS_FRONTEND = true;
    config.calculateApiUrls();
    expect(config.chromeApiUrl)
        .toBe('https://chrome-dot-prod-app-engine-project.appspot.com/_ah/api');
    expect(config.endpointsApiUrl)
        .toBe('https://endpoints-dot-prod-app-engine-project.appspot.com/_ah/api');
  });

  it('provides the correct link for chrome/endpoints apis if on QA', () => {
    config.ON_LOCAL = false;
    config.ON_DEV = false;
    config.ON_QA = true;
    config.ON_PROD = false;
    config.IS_FRONTEND = true;
    config.calculateApiUrls();
    expect(config.chromeApiUrl)
        .toBe('https://chrome-dot-qa-app-engine-project.appspot.com/_ah/api');
    expect(config.endpointsApiUrl)
        .toBe(
            'https://endpoints-dot-qa-app-engine-project.appspot.com/_ah/api');
  });

  it('provides the correct link for chrome/endpoints apis if on dev', () => {
    config.ON_LOCAL = false;
    config.ON_DEV = true;
    config.ON_QA = false;
    config.ON_PROD = false;
    config.IS_FRONTEND = true;
    config.calculateApiUrls();
    expect(config.chromeApiUrl)
        .toBe('https://chrome-dot-dev-app-engine-project.appspot.com/_ah/api');
    expect(config.endpointsApiUrl)
        .toBe('https://endpoints-dot-dev-app-engine-project.appspot.com/_ah/api');
  });

  it('provides the correct link for chrome/endpoints apis if on localhost',
     () => {
       config.ON_LOCAL = true;
       config.ON_DEV = false;
       config.ON_QA = false;
       config.ON_PROD = false;
       config.IS_FRONTEND = true;
       config.calculateApiUrls();
       expect(config.chromeApiUrl).toBe('http://localhost:8082/_ah/api');
       expect(config.endpointsApiUrl).toBe('http://localhost:8081/_ah/api');
     });

  it('provides the correct link for chrome/endpoints apis if the chrome app and on prod',
     () => {
       config.ON_LOCAL = false;
       config.ON_DEV = false;
       config.ON_QA = false;
       config.ON_PROD = false;
       config.IS_FRONTEND = false;
       spyOnProperty(config, 'chromeMode', 'get')
           .and.returnValue(CHROME_MODE.PROD);
       config.calculateApiUrls();
       expect(config.chromeApiUrl)
           .toBe('https://chrome-dot-prod-app-engine-project.appspot.com/_ah/api');
       expect(config.endpointsApiUrl)
           .toBe('https://endpoints-dot-prod-app-engine-project.appspot.com/_ah/api');
     });

  it('provides the correct link for chrome/endpoints apis if the chrome app and on dev',
     () => {
       config.ON_LOCAL = false;
       config.ON_DEV = false;
       config.ON_QA = false;
       config.ON_PROD = false;
       config.IS_FRONTEND = false;
       spyOnProperty(config, 'chromeMode', 'get')
           .and.returnValue(CHROME_MODE.DEV);
       config.calculateApiUrls();
       expect(config.chromeApiUrl)
           .toBe('https://chrome-dot-dev-app-engine-project.appspot.com/_ah/api');
       expect(config.endpointsApiUrl)
           .toBe('https://endpoints-dot-dev-app-engine-project.appspot.com/_ah/api');
     });

  it('provides the correct link for chrome/endpoints apis if the chrome app and on QA',
     () => {
       config.ON_LOCAL = false;
       config.ON_DEV = false;
       config.ON_QA = false;
       config.ON_PROD = false;
       config.IS_FRONTEND = false;
       spyOnProperty(config, 'chromeMode', 'get')
           .and.returnValue(CHROME_MODE.QA);
       config.calculateApiUrls();
       expect(config.chromeApiUrl)
           .toBe(
               'https://chrome-dot-qa-app-engine-project.appspot.com/_ah/api');
       expect(config.endpointsApiUrl)
           .toBe(
               'https://endpoints-dot-qa-app-engine-project.appspot.com/_ah/api');
     });
});
