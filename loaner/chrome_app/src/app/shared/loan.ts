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

import {HttpClient} from '@angular/common/http';
import {Injectable} from '@angular/core';
import {Observable, of} from 'rxjs';
import {map, switchMap} from 'rxjs/operators';

import {ConfigService} from '../../../../shared/config';
import {Device, DeviceRequestApiParams, ExtendDeviceRequestApiParams, MarkAsDamagedRequestApiParams} from '../../../../shared/models/device';

import * as DeviceIdentifier from './device_identifier';

@Injectable()
export class Loan {
  constructor(
      private readonly config: ConfigService,
      private readonly http: HttpClient) {}

  chromeUrl = `${this.config.chromeApiUrl}/loaner/v1/chrome`;
  endpointsDeviceUrl = `${this.config.endpointsApiUrl}/loaner/v1/device`;

  /**
   * Request to extend the loan return date.
   * @param newDate Date in Python DateTime formatting, sent as a string.
   */
  extend(newDate: string): Observable<boolean> {
    let request: ExtendDeviceRequestApiParams;
    return DeviceIdentifier.id().pipe(switchMap(deviceId => {
      request = {
        device: {
          chrome_device_id: deviceId,
        },
        extend_date: newDate,
      };
      const apiUrl = `${this.endpointsDeviceUrl}/user/extend_loan`;
      return this.http.post<boolean>(apiUrl, request);
    }));
  }

  /** Mark device as returned on the backend. */
  return(): Observable<boolean> {
    let request: DeviceRequestApiParams;
    return DeviceIdentifier.id().pipe(switchMap(deviceId => {
      request = {
        chrome_device_id: deviceId,
      };
      const apiUrl = `${this.endpointsDeviceUrl}/user/mark_pending_return`;
      return this.http.post<boolean>(apiUrl, request);
    }));
  }

  /**
   * Mark device as damaged on the backend.
   * @param damagedReason Optional reason for what's damaged on the device.
   */
  damaged(damagedReason?: string): Observable<boolean> {
    let request: MarkAsDamagedRequestApiParams;
    return DeviceIdentifier.id().pipe(switchMap(deviceId => {
      request = {
        damaged_reason: damagedReason,
        device: {
          chrome_device_id: deviceId,
        },
      };
      const apiUrl = `${this.endpointsDeviceUrl}/user/mark_damaged`;
      return this.http.post<boolean>(apiUrl, request);
    }));
  }

  /** Enable guest mode for the loan. */
  enableGuestMode(): Observable<boolean> {
    let request: DeviceRequestApiParams;
    return DeviceIdentifier.id().pipe(switchMap(deviceId => {
      request = {
        chrome_device_id: deviceId,
      };
      const apiUrl = `${this.endpointsDeviceUrl}/user/enable_guest_mode`;
      return this.http.post<boolean>(apiUrl, request);
    }));
  }

  /** Resumes the loan and removes the pending return status. */
  resumeLoan(): Observable<boolean> {
    let request: DeviceRequestApiParams;
    return DeviceIdentifier.id().pipe(switchMap(deviceId => {
      request = {
        chrome_device_id: deviceId,
      };
      const apiUrl = `${this.endpointsDeviceUrl}/user/resume_loan`;
      return this.http.post<boolean>(apiUrl, request);
    }));
  }

  /**
   * Gets the device info and some additional loan info.
   */
  getDevice(): Observable<Device> {
    let request: DeviceRequestApiParams;
    return DeviceIdentifier.id().pipe(switchMap(deviceId => {
      request = {
        chrome_device_id: deviceId,
      };
      const apiUrl = `${this.endpointsDeviceUrl}/user/get`;
      return this.http.post<Device>(apiUrl, request)
          .pipe(map(deviceApiParams => new Device(deviceApiParams)));
    }));
  }
}

/** Loan service mock that don't call any HTTP. */
@Injectable()
export class LoanMock {
  chromeUrl = `chrome`;
  endpointsDeviceUrl = `device`;

  extend(newDate: string): Observable<boolean> {
    return of(true);
  }

  return(): Observable<boolean> {
    return of(true);
  }

  damaged(damagedReason?: string): Observable<boolean> {
    return of(true);
  }

  enableGuestMode(): Observable<boolean> {
    return of(true);
  }

  resumeLoan(): Observable<boolean> {
    return of(true);
  }

  getDevice(): Observable<Device> {
    return of(new Device());
  }
}
