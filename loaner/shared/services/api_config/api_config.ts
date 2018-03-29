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


/**
 * ApiConfig is used so that either application can specify their desired API
 * endpoint on build. This is used in conjunction with the apiConfigFactory so
 * that it can be Injected in to the apps module providers with configured
 * values.
 */
export class ApiConfig {
  constructor(readonly baseUrl: string, readonly baseChromeUrl?: string) {}
}

export function apiConfigFactory(endpoint: string, chromeEndpoint?: string) {
  return new ApiConfig(endpoint, chromeEndpoint);
}
