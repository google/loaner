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

import * as config from './config';

describe('APIService', () => {
  let api: config.APIService;

  beforeEach(() => {
    api = new config.APIService();
  });

  it('should provide the correct link for chrome endpoint', () => {
    expect(api.chrome()).toBe('http://localhost:8082/_ah/api');
  });

  it('should provide the correct link for standard endpoint', () => {
    expect(api.endpoints()).toBe('http://localhost:8081/_ah/api');
  });
});
