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


import {Observable, of, throwError} from 'rxjs';

import {ConfigService} from '../../../../shared/config';

const CONFIG = new ConfigService();
export function id(): Observable<string> {
  if (CONFIG.CHROME_DEV_MODE || CONFIG.TESTING) {
    return of(CONFIG.DEV_DEVICE_ID);
  }

  const deviceAttributes = chrome.enterprise.deviceAttributes;

  if (!deviceAttributes) {
    return throwError(`This application was not force installed by an OU. Please
contact your administrator`);
  }

  return new Observable(observer => {
    deviceAttributes.getDirectoryDeviceId(deviceId => {
      observer.next(deviceId);
    });
  });
}
