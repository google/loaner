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


import {DEV_DEVICE_ID, DEV_MODE, TESTING} from '../config';

/** Get the unique enterprise ID from the chrome device. */
export function id(): Promise<string|undefined> {
  return new Promise((resolve, reject) => {
    try {
      const deviceAttributes = chrome.enterprise.deviceAttributes;
      if (deviceAttributes) {
        deviceAttributes.getDirectoryDeviceId((deviceId: string) => {
          resolve(deviceId);
        });
      } else {
        resolve(undefined);
      }
    } catch (error) {
      if (DEV_MODE || TESTING) {
        resolve(DEV_DEVICE_ID);
      } else {
        reject(error);
      }
    }
  });
}
