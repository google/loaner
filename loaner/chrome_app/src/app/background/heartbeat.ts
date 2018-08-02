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
 * heartbeat.ts hold methods surround setting interval and sending of
 * the device heartbeat.
 */

import {from, Observable, of, throwError} from 'rxjs';
import {catchError, switchMap} from 'rxjs/operators';

import {ConfigService, HEARTBEAT} from '../../../../shared/config';
import * as DeviceIdentifier from '../shared/device_identifier';
import * as Http from '../shared/http';

const CONFIG = new ConfigService();

/**
 * Set the interval for the heartbeat
 */
export function setHeartbeatInterval(period: number = HEARTBEAT.duration) {
  chrome.alarms.create(HEARTBEAT.name, {
    'periodInMinutes': period,
  });
}

/**
 * Disable the heartbeat chrome alarm.
 */
export function disableHeartbeat() {
  chrome.alarms.clear(HEARTBEAT.name);
  removeHeartbeatListener();
}

/**
 * Send the heartbeat request to the API endpoint.
 */
export function sendHeartbeat(): Observable<HeartbeatResponse> {
  const heartbeatUrl = `${CONFIG.chromeApiUrl}${HEARTBEAT.url}`;
  return DeviceIdentifier.id().pipe(
      switchMap(
          deviceId =>
              from(Http.get<HeartbeatResponse>(`${heartbeatUrl}${deviceId}`))),
      switchMap(res => {
        if (CONFIG.LOGGING) {
          console.info(`Heartbeat response: ${res}`);
        }
        return of(res);
      }),
      catchError(error => throwError(`The heartbeat failed: ${error}`)));
}

/**
 * Create the chrome alarms for the heartbeat.
 */
export function setHeartbeatAlarmListener() {
  chrome.alarms.onAlarm.addListener(createHeartbeatListener);
}

/**
 * Creates the function for the heartbeat listener to use and listen to.
 * @param alarm Name of the alarm we are checking for.
 */
function createHeartbeatListener(alarm: chrome.alarms.Alarm) {
  if (alarm.name === HEARTBEAT.name && navigator.onLine) {
    sendHeartbeat().subscribe();
    if (CONFIG.LOGGING) {
      console.info(`Heartbeat sent`);
    }
  }
}

/** Destroys the heartbeat listener. */
export function removeHeartbeatListener() {
  chrome.alarms.onAlarm.removeListener(createHeartbeatListener);
}
