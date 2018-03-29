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

import {ApiConfig, apiConfigFactory} from './api_config';

describe('ApiConfig', () => {
  it('should generate a class with the correct properties', () => {
    const config =
        new ApiConfig('http://example.com', 'http://chrome-example.com');
    expect(config.baseUrl).toBe('http://example.com');
    expect(config.baseChromeUrl).toBe('http://chrome-example.com');
  });
});

describe('apiConfigFactory', () => {
  it('should generate a new ApiConfig class with the correct properties',
     () => {
       const config =
           apiConfigFactory('http://example.com', 'http://chrome-example.com');
       expect(config.baseUrl).toBe('http://example.com');
       expect(config.baseChromeUrl).toBe('http://chrome-example.com');
     });
});
