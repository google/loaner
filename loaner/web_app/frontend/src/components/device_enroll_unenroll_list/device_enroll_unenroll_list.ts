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

import {HttpErrorResponse} from '@angular/common/http';
import {Component, Input} from '@angular/core';
import {Observable, of} from 'rxjs';
import {map, tap} from 'rxjs/operators';

import {Actions, Device, DeviceOnAction, Status} from '../../models/device';
import {DeviceService} from '../../services/device';
import {Dialog} from '../../services/dialog';

@Component({
  selector: 'loaner-device-enroll-unenroll-list',
  styleUrls: ['device_enroll_unenroll_list.scss'],
  templateUrl: 'device_enroll_unenroll_list.ng.html',
})
export class DeviceEnrollUnenrollList {
  actions = Actions;
  /** Status of enroll/unenroll to be and displayed on the template. */
  status = Status;
  /** Devices that are being enrolled/unenrolled */
  devices: DeviceOnAction[] = [];
  /** Current action depending on app route, enroll or unenroll. */
  @Input() currentAction = '';

  constructor(
      private readonly deviceService: DeviceService,
      private readonly dialogBox: Dialog,
  ) {}

  /**
   * Property to check if the list of devices enrolled or unenrolled is empty.
   */
  get isEmpty() {
    return this.devices.length === 0;
  }

  /**
   * Adds a device to the pool of devices that are being enrolled or unenrolled.
   * @param device The object that holds the device identifier to be enrolled
   * or unenrolled
   */
  deviceAction(device: Device) {
    const deviceId =
        device.assetTag || device.serialNumber || device.identifier;
    let deviceOnAction: DeviceOnAction;
    if (deviceId) {
      deviceOnAction = {
        deviceId,
        status: Status.IN_PROGRESS,
      };

      this.devices.push(deviceOnAction);

      const handleSuccess = () => {
        deviceOnAction.status = Status.READY;
        deviceOnAction.message = `Successfully ${this.currentAction}ed`;
      };
      const handleError = (error: HttpErrorResponse) => {
        deviceOnAction.status = Status.ERROR;
        deviceOnAction.message = error.error.error.message;
      };

      if (this.currentAction === Actions.ENROLL) {
        this.deviceService.enroll(device).subscribe(handleSuccess, handleError);
      } else {
        this.deviceService.unenroll(device).subscribe(
            handleSuccess, handleError);
      }
    }
  }

  /** Can deactivate route checking. */
  canDeactivate(): Observable<boolean> {
    /** Check if any error occurred to confirm if user is aware */
    if (this.devices.find(device => device.status === Status.ERROR)) {
      return this.dialogBox
          .confirm(
              'Do you want to leave this page?',
              `One or more devices failed to be ${this.currentAction}ed`)
          .pipe(
              tap(result => {
                if (result) {
                  /** Clean everything before changing route. */
                  this.devices = [];
                }
              }),
              map(result => Boolean(result)));
    }
    /** Clean everything before changing route. */
    this.devices = [];
    return of(true);
  }
}
