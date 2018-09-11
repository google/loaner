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

import {Component, EventEmitter, Input, Output} from '@angular/core';
import {switchMap} from 'rxjs/operators';

import {Damaged} from '../../../../../shared/components/damaged';
import {Extend} from '../../../../../shared/components/extend';
import {GuestMode} from '../../../../../shared/components/guest';
import {Lost} from '../../../../../shared/components/lost';
import {Undamaged} from '../../../../../shared/components/undamaged';
import {Unenroll} from '../../../../../shared/components/unenroll';
import {Unlock} from '../../../../../shared/components/unlock';
import {Device} from '../../models/device';
import {DeviceService} from '../../services/device';

/**
 * Component that renders a menu with device actions in it.
 */
@Component({
  preserveWhitespaces: true,
  selector: 'loaner-device-actions-menu',
  styleUrls: ['device_actions_menu.scss'],
  templateUrl: 'device_actions_menu.ng.html',
})
export class DeviceActionsMenu {
  @Input() device!: Device;
  @Output() refreshDevice = new EventEmitter<string>();
  @Output() unenrolled = new EventEmitter<void>();

  constructor(
      private readonly damagedService: Damaged,
      private readonly deviceService: DeviceService,
      private readonly extendService: Extend,
      private readonly guestModeService: GuestMode,
      private readonly lostService: Lost,
      private readonly undamagedService: Undamaged,
      private readonly unenrollService: Unenroll,
      private readonly unlockService: Unlock,
  ) {}

  /** Dialog for removing a device. */
  openRemoveDeviceDialog() {
    this.unenrollService.openDialog(this.device.identifier);
    this.unenrollService.onUnenroll
        .pipe(switchMap(() => this.deviceService.unenroll(this.device)))
        .subscribe(() => {
          this.unenrollService.finished();
          this.unenrolled.emit();
          this.refreshDevice.emit();
        });
  }

  /**
   * Toggle guest mode for the device
   * @param device The device we are enabling guest on.
   */
  enableGuestMode(device: Device) {
    this.guestModeService.openDialog();
    this.guestModeService.onGuestModeEnabled
        .pipe(switchMap(() => this.deviceService.enableGuestMode(device)))
        .subscribe(() => {
          this.guestModeService.finished();
          this.refreshDevice.emit(device.identifier);
        });
  }

  /**
   * Unlock a lost or locked device.
   * @param device The device we are enabling guest on.
   */
  unlock(device: Device) {
    this.unlockService.openDialog(device.identifier);
    this.unlockService.onUnlock
        .pipe(switchMap(() => this.deviceService.unlock(device)))
        .subscribe(() => {
          this.unlockService.finished();
          this.refreshDevice.emit(device.identifier);
        });
  }

  /**
   * Calls deviceService API for extending a device and defines new due date.
   * @param device The device we're extending.
   */
  extendDevice(device: Device) {
    let temporaryNewDate: string;
    this.extendService.openDialog(device.dueDate, device.maxExtendDate);
    this.extendService.onExtended
        .pipe(switchMap(newDate => {
          temporaryNewDate = newDate;
          return this.deviceService.extend(newDate, device);
        }))
        .subscribe(
            () => {
              this.extendService.finished(new Date(temporaryNewDate));
              temporaryNewDate = '';
              this.refreshDevice.emit(device.identifier);
            },
            () => {
              this.extendService.close();
            });
  }

  /**
   * Calls the deviceService to return a device.
   * @param device The device to take action on.
   */
  onReturned(device: Device) {
    this.deviceService.returnDevice(device).subscribe(() => {
      device.pendingReturn = true;
    });
    this.refreshDevice.emit(device.identifier);
  }

  /**
   * Calls the deviceService to mark a device as damaged.
   * @param device The device to take action on.
   */
  onDamaged(device: Device) {
    this.damagedService.openDialog();
    this.damagedService.onDamaged
        .pipe(switchMap(
            damagedReason =>
                this.deviceService.markAsDamaged(device, damagedReason)))
        .subscribe(
            () => {
              this.damagedService.finished();
              this.refreshDevice.emit(device.identifier);
            },
            () => {
              this.damagedService.close();
            });
  }

  /**
   * Calls the deviceService to clear a device's as damaged state.
   * @param device The device to take action on.
   */
  onUndamaged(device: Device) {
    this.undamagedService.openDialog(device.identifier);
    this.undamagedService.onUndamaged
        .pipe(switchMap(
            damagedReason => this.deviceService.markAsUndamaged(device)))
        .subscribe(
            () => {
              this.undamagedService.finished();
              this.refreshDevice.emit(device.identifier);
            },
            () => {
              this.undamagedService.close();
            });
  }

  /**
   * Calls the deviceService to mark a device as lost.
   * @param device The device to take action on.
   */
  onLost(device: Device) {
    this.lostService.openDialog();
    this.lostService.onLost
        .pipe(switchMap(() => this.deviceService.markAsLost(device)))
        .subscribe(
            () => {
              this.lostService.finished();
              this.refreshDevice.emit(device.identifier);
            },
            () => {
              this.lostService.close();
            });
  }
}
