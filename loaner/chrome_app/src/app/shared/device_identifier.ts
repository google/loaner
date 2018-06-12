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


import {Observable, of} from 'rxjs';

import {CHROME_MODE, ConfigService} from '../../../../shared/config';

const CONFIG = new ConfigService();
export function id(): Observable<string> {
  try {
    const deviceAttributes = chrome.enterprise.deviceAttributes;
    return new Observable(observer => {
      deviceAttributes.getDirectoryDeviceId(deviceId => {
        observer.next(deviceId);
      });
    });
  } catch (error) {
    if (CONFIG.chromeMode === CHROME_MODE.DEV) {
      console.warn(`The Chrome App is currently running in developer/testing
mode and using a device id of ${CONFIG.DEV_DEVICE_ID}.`);
      return of(CONFIG.DEV_DEVICE_ID);
    } else {
      console.error(`This application was not force installed by an OU.
Please contact your administrator. ${error}`);
      return of('NO_DEVICE_ID');
    }
  }
}
