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

import {DataSource} from '@angular/cdk/table';
import {Injectable} from '@angular/core';
import {Response} from '@angular/http';
import {MatSort} from '@angular/material';
import {BehaviorSubject, Observable} from 'rxjs';
import {map, tap} from 'rxjs/operators';

import {Device, DeviceRequestApiParams, ExtendDeviceRequestApiParams, MarkAsDamagedRequestApiParams} from '../models/device';
import {DeviceApiParams, ListDeviceResponse} from '../models/device';

import {ApiService} from './api';

/** Class to connect to the backend's Device Service API methods. */
@Injectable()
export class DeviceService extends ApiService {
  /** Implements ApiService's apiEndpoint requirement. */
  apiEndpoint = 'device';

  /** Checks if whether a particular device is ready to be checked in. */
  checkReadyForAudit(id: string): Observable<string> {
    return new Observable(observer => {
      this.post(
              'auditable', {'unknown_identifier': id},
              false /* showSnackbarOnFailure */)
          .subscribe(
              () => {
                observer.next(`Device ready for audit.`);
              },
              error => {
                observer.error(error.error.error.message);
              });
    });
  }

  /**
   * Gets a particular device from the backend.
   * @param id Device identifier to be gotten from the backend.
   */
  getDevice(id: string) {
    return this.post('get', {'unknown_identifier': id})
        .pipe(map(res => new Device(res)));
  }

  /**
   * Returns all the device data as a list of devices.
   */
  list(filters: DeviceApiParams = {}): Observable<Device[]> {
    return this.post<ListDeviceResponse>('list', filters).pipe(map(res => {
      const retrievedDevices = res;
      return (retrievedDevices['devices'] || [])
          .map(
              (retrievedDevice: DeviceApiParams) =>
                  new Device(retrievedDevice));
    }));
  }

  /**
   * Returns assigned devices based on the current user.
   */
  listUserDevices(): Observable<Device[]> {
    return this.post<ListDeviceResponse>('user_devices').pipe(map(res => {
      const retrievedDevices = res;
      return (retrievedDevices['devices'] || [])
          .map(
              (retrievedDevices: DeviceApiParams) =>
                  new Device(retrievedDevices));
    }));
  }

  /**
   * Request to extend the loan return date.
   * @param newDate Date in Python DateTime formatting, sent as a string.
   * @param id Device identifier to be extended.
   */
  extend(newDate: string, id: string): Observable<boolean> {
    return new Observable((observer) => {
      const device: DeviceRequestApiParams = {
        'unknown_identifier': id,
      };
      const request: ExtendDeviceRequestApiParams = {
        'device': device,
        'extend_date': newDate,
      };
      this.post('extend_loan', request).subscribe(() => {
        observer.next(true);
      });
    });
  }

  /**
   * Returns a particular device from a user loan.
   * @param id Device identifier to be returned.
   */
  returnDevice(id: string) {
    const request: DeviceRequestApiParams = {
      'unknown_identifier': id,
    };
    return this.post('mark_pending_return', request).pipe(tap(() => {
      this.snackBar.open(`Device ${id} returned.`);
    }));
  }

  /**
   * Marks a particular device as lost.
   * @param id Device identifier to be marked as lost.
   */
  markAsLost(id: string) {
    const request: DeviceRequestApiParams = {
      'unknown_identifier': id,
    };
    return this.post('mark_lost', request).pipe(tap(() => {
      this.snackBar.open(`Device ${id} marked as lost.`);
    }));
  }

  /**
   * Enables Guest mode in a particular device.
   * @param id Device identifier to have Guest mode enabled.
   */
  enableGuestMode(id: string) {
    const request: DeviceRequestApiParams = {
      'unknown_identifier': id,
    };
    return this.post('enable_guest_mode', request).pipe(tap(() => {
      this.snackBar.open(`Enabled guest mode for device ${id}.`);
    }));
  }

  /**
   * Marks a particular device as damaged.
   * @param id Device identifier to have device marked as damaged.
   * @param reason The reason why the device is being marked as damaged.
   */
  markAsDamaged(id: string, reason: string): Observable<void> {
    const device: DeviceRequestApiParams = {
      'unknown_identifier': id,
    };
    const request: MarkAsDamagedRequestApiParams = {
      'device': device,
      'damaged_reason': reason,
    };
    const httpObservable = this.post<void>('mark_damaged', request);
    httpObservable.subscribe(() => {
      this.snackBar.open(`Device ${id} marked as damaged.`);
    });
    return httpObservable;
  }

  /**
   * Enrolls a particular device into the Grab n Go Loaners program.
   * @param newDevice Device that will be enrolled in the program.
   */
  enroll(newDevice: Device) {
    return this.post<void>('enroll', newDevice.toApiMessage()).pipe(tap(() => {
      this.snackBar.open(`Device ${newDevice.serialNumber} enrolled.`);
    }));
  }

  /**
   * Unenrolls a particular device from the Grab n Go Loaners program.
   * @param deviceToBeUnenrolled Device that will be unenrolled from the
   * program.
   */
  unenroll(deviceToBeUnenrolled: Device): Observable<void> {
    return this.post<void>('unenroll', deviceToBeUnenrolled.toApiMessage())
        .pipe(tap(() => {
          this.snackBar.open(
              `Device ${deviceToBeUnenrolled.serialNumber} removed.`);
        }));
  }
}
