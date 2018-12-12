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

import {Injectable} from '@angular/core';
import {MatSort} from '@angular/material';
import {BehaviorSubject, Observable} from 'rxjs';
import {map, tap} from 'rxjs/operators';

import {SearchExpression, SortDirection, translateSortDirectionToApi} from '../../../../shared/models/search';
import {Device, DeviceApiParams, DeviceRequestApiParams, ExtendDeviceRequestApiParams, ListDevicesResponse, ListDevicesResponseApiParams, MarkAsDamagedRequestApiParams} from '../models/device';

import {ApiService} from './api';

function setupQueryFilters(
    filters: DeviceApiParams,
    activeSortField: string,
    sortDirection: SortDirection,
) {
  const expressions: SearchExpression = {
    expression: activeSortField,
    direction: translateSortDirectionToApi(sortDirection),
  };

  if (filters.query && filters.query.query_string) {
    filters.query = {query_string: filters.query.query_string, expressions};
  } else {
    filters.query = {expressions};
  }
  return filters;
}

/** Class to connect to the backend's Device Service API methods. */
@Injectable()
export class DeviceService extends ApiService {
  /** Implements ApiService's apiEndpoint requirement. */
  apiEndpoint = 'device';

  /** Checks if whether a particular device is ready to be checked in. */
  checkReadyForAudit(id: string): Observable<string> {
    return new Observable(observer => {
      const request: DeviceRequestApiParams = {'identifier': id};
      this.post('auditable', request, false /* showSnackbarOnFailure */)
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
    const request: DeviceRequestApiParams = {'identifier': id};
    return this.post('user/get', request)
        .pipe(map(
            (retrievedDevice: DeviceApiParams) => new Device(retrievedDevice)));
  }

  /**
   * Returns all the device data as a list of devices.
   */
  list(
      filters: DeviceApiParams = {},
      activeSortField = 'id',
      sortDirection: SortDirection = 'asc',
      ): Observable<ListDevicesResponse> {
    filters = setupQueryFilters(filters, activeSortField, sortDirection);

    return this.post<ListDevicesResponseApiParams>('list', filters)
        .pipe(map(res => {
          const devices =
              res.devices && res.devices.map(d => new Device(d)) || [];
          const retrievedDevices: ListDevicesResponse = {
            devices,
            totalResults: res.total_results,
            totalPages: res.total_pages
          };
          return retrievedDevices;
        }));
  }

  /**
   * Returns assigned devices based on the current user.
   */
  listUserDevices(): Observable<Device[]> {
    return this.post<ListDevicesResponseApiParams>('user/devices')
        .pipe(map(res => {
          const retrievedDevices = res;
          return (retrievedDevices['devices'] || [])
              .map(
                  (retrievedDevice: DeviceApiParams) =>
                      new Device(retrievedDevice));
        }));
  }

  /**
   * Request to extend the loan return date.
   * @param newDate Date in Python DateTime formatting, sent as a string.
   * @param device Device to have its due date extended.
   */
  extend(newDate: string, device: Device): Observable<boolean> {
    return new Observable(observer => {
      const request: ExtendDeviceRequestApiParams = {
        'device': device.toApiMessage(),
        'extend_date': newDate,
      };
      this.post('user/extend_loan', request).subscribe(() => {
        observer.next(true);
      });
    });
  }

  /**
   * Returns a particular device from a user loan.
   * @param device Device to be returned.
   */
  returnDevice(device: Device) {
    return this.post('user/mark_pending_return', device.toApiMessage())
        .pipe(tap(() => {
          this.snackBar.open(`Device ${device.identifier} returned.`);
        }));
  }

  /**
   * Marks a particular device as lost.
   * @param device Device to be marked as lost.
   */
  markAsLost(device: Device) {
    return this.post('user/mark_lost', device.toApiMessage()).pipe(tap(() => {
      this.snackBar.open(`Device ${device.identifier} marked as lost.`);
    }));
  }

  /**
   * Unlocks a particular device.
   * @param device Device to be unlocked.
   */
  unlock(device: Device) {
    return this.post<void>('unlock', device.toApiMessage()).pipe(tap(() => {
      this.snackBar.open(`Device ${device.identifier} has been unlocked.`);
    }));
  }

  /**
   * Enables Guest mode in a particular device.
   * @param device Device to have Guest mode enabled.
   */
  enableGuestMode(device: Device): Observable<void> {
    return this.post('user/enable_guest_mode', device.toApiMessage());
  }

  /**
   * Resumes the loan for a particular device.
   * @param device Device to resume the loan for.
   */
  resumeLoan(device: Device) {
    return this.post('user/resume_loan', device.toApiMessage()).pipe(tap(() => {
      this.snackBar.open(`Loan resumed for device ${device.identifier}.`);
    }));
  }

  /**
   * Marks a particular device as damaged.
   * @param device Device to be marked as damaged.
   * @param reason The reason why the device is being marked as damaged.
   */
  markAsDamaged(device: Device, reason: string): Observable<void> {
    const request: MarkAsDamagedRequestApiParams = {
      'device': device.toApiMessage(),
      'damaged_reason': reason,
    };
    const httpObservable = this.post<void>('user/mark_damaged', request);
    httpObservable.subscribe(() => {
      this.snackBar.open(`Device ${device.identifier} marked as damaged.`);
    });
    return httpObservable;
  }

  /**
   * Clears a device's damaged state.
   * @param device Device to be marked as undamaged.
   */
  markAsUndamaged(device: Device) {
    return this.post('undamaged', device.toApiMessage()).pipe(tap(() => {
      this.snackBar.open(
          `Device ${device.identifier} is no longer marked as damaged.`);
    }));
  }

  /**
   * Enrolls a particular device into the Grab n Go Loaners program.
   * @param newDevice Device that will be enrolled in the program.
   */
  enroll(newDevice: Device) {
    return this.post<void>('enroll', newDevice.toApiMessage()).pipe(tap(() => {
      this.snackBar.open(`Device ${newDevice.identifier} enrolled.`);
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
              `Device ${deviceToBeUnenrolled.identifier} removed.`);
        }));
  }
}
