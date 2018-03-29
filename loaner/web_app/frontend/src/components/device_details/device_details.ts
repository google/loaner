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

import {Location} from '@angular/common';
import {Component, OnInit} from '@angular/core';
import {ActivatedRoute, Router} from '@angular/router';
import {never} from 'rxjs/observable/never';
import {finalize, switchMap} from 'rxjs/operators';

import {Damaged} from '../../../../../shared/components/damaged';
import {Extend} from '../../../../../shared/components/extend';
import {GuestMode} from '../../../../../shared/components/guest';
import {LoaderView} from '../../../../../shared/components/loader';
import {Lost} from '../../../../../shared/components/lost';
import {Device} from '../../models/device';
import {DeviceService} from '../../services/device';
import {Dialog} from '../../services/dialog';

/**
 * Component that renders the device details template.
 */
@Component({
  preserveWhitespaces: true,
  selector: 'loaner-device-details',
  styleUrls: ['device_details.scss'],
  templateUrl: 'device_details.html',
})
export class DeviceDetails extends LoaderView implements OnInit {
  device = new Device();
  dialogResult: boolean;

  identifier = 'Serial No.';
  constructor(
      private readonly damagedService: Damaged,
      private readonly lostService: Lost,
      private readonly extendService: Extend,
      private readonly deviceService: DeviceService,
      private readonly guestModeService: GuestMode,
      private readonly route: ActivatedRoute, private readonly router: Router,
      private readonly dialog: Dialog, private readonly location: Location) {
    super(true);
  }

  ngOnInit() {
    this.route.params.subscribe((params) => {
      this.refreshDevice(params.id);
    });
  }

  /** Dialog for removing a device. */
  openRemoveDeviceDialog() {
    const dialogTitle = 'Remove device';
    const dialogContent = 'Are you sure you want to remove this device?';
    this.dialog.confirm(dialogTitle, dialogContent).subscribe(result => {
      if (result) {
        this.waiting();
        this.deviceService.unenroll(this.device)
            .pipe(finalize(() => {
              this.ready();
            }))
            .subscribe(() => {
              this.back();
            });
      }
    });
  }

  /**
   * Refreshes a device using the deviceService.
   * @param deviceID the device identifier used to get the device.
   */
  private refreshDevice(deviceId: string) {
    this.waiting();
    this.deviceService.getDevice(deviceId).subscribe((device: Device) => {
      this.device = device;
      this.ready();
    });
  }

  /**
   * Toggle guest mode for the device
   * @param device The device we are enabling guest on.
   */
  enableGuestMode(device: Device) {
    this.guestModeService.openDialog();
    this.guestModeService.onGuestModeEnabled
        .pipe(switchMap(
            () => this.deviceService.enableGuestMode(device.serialNumber)))
        .subscribe(() => {
          this.guestModeService.finished();
          this.refreshDevice(device.serialNumber);
        });
  }

  /**
   * Calls deviceService API for extending a device and defines new due date.
   *
   * @param device The device we're extending.
   */
  extendDevice(device: Device) {
    let temporaryNewDate: string;
    this.extendService.openDialog(device.dueDate, device.maxExtendDate);
    this.extendService.onExtended
        .pipe(switchMap(newDate => {
          temporaryNewDate = newDate;
          return this.deviceService.extend(newDate, device.serialNumber);
        }))
        .subscribe(
            () => {
              this.extendService.finished(new Date(temporaryNewDate));
              temporaryNewDate = '';
              this.refreshDevice(device.serialNumber);
            },
            () => {
              this.extendService.close();
            });
  }

  /**
   * Calls the deviceService to return a device.
   *
   * @param device The device to take action on.
   */
  onReturned(device: Device) {
    this.deviceService.returnDevice(device.serialNumber).subscribe(() => {
      device.pendingReturn = true;
    });
  }

  /**
   * Calls the deviceService to mark a device as damaged.
   *
   * @param device The device to take action on.
   */
  onDamaged(device: Device) {
    this.damagedService.openDialog();
    this.damagedService.onDamaged
        .pipe(switchMap(
            damagedReason => this.deviceService.markAsDamaged(
                device.serialNumber, damagedReason)))
        .subscribe(
            () => {
              this.damagedService.finished();
              this.refreshDevice(device.serialNumber);
            },
            () => {
              this.damagedService.close();
            });
  }

  /**
   * Calls the deviceService to mark a device as lost.
   *
   * @param device The device to take action on.
   */
  onLost(device: Device) {
    this.lostService.openDialog();
    this.lostService.onLost
        .pipe(
            switchMap(() => this.deviceService.markAsLost(device.serialNumber)))
        .subscribe(
            () => {
              this.lostService.finished();
              this.refreshDevice(device.serialNumber);
            },
            () => {
              this.lostService.close();
            });
  }

  /** Navigates to the previous expected page. */
  back() {
    this.location.back();
  }
}
