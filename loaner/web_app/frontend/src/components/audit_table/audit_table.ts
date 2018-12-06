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

import {DeviceOnAction, Status} from '../../models/device';
import {Shelf} from '../../models/shelf';
import {DeviceService} from '../../services/device';
import {Dialog} from '../../services/dialog';
import {ShelfService} from '../../services/shelf';

@Component({
  preserveWhitespaces: true,
  selector: 'loaner-audit-table',
  styleUrls: ['audit_table.scss'],
  templateUrl: 'audit_table.ng.html',

})
export class AuditTable implements OnInit {
  /** Status to be checked and displayed on the template */
  status = Status;
  /** List of devices that are in the pool to be checked in. */
  devicesToBeCheckedIn: DeviceOnAction[] = [];
  /** Current shelf that the devices are being checked into. */
  shelf = new Shelf();

  constructor(
      private readonly deviceService: DeviceService,
      private readonly dialog: Dialog,
      private readonly location: Location,
      private readonly route: ActivatedRoute,
      private readonly router: Router,
      private readonly shelfService: ShelfService,
  ) {}

  ngOnInit() {
    this.route.params.subscribe(params => {
      this.shelfService.getShelf(params.id).subscribe(shelf => {
        this.shelf = shelf;
      });
    });
  }

  /** Property that defines if there's any device ready to be checked in. */
  get isEmpty() {
    return this.devicesToBeCheckedIn.length === 0;
  }

  /** Navigates to the previous expected page. */
  backToShelves() {
    this.router.navigate(['/shelves']);
  }

  /** Navigates to the previous visited page. */
  backToLast() {
    this.location.back();
  }

  /**
   * Adds a device to the pool of devices to be checked in and check it's state
   * for the audit.
   *
   * @param input Input element with the device identifier that will be checked
   *              in.
   */
  addDevice(input: HTMLInputElement) {
    const deviceId = input.value.trim();
    let deviceToBeCheckedIn: DeviceOnAction;
    if (deviceId) {
      deviceToBeCheckedIn = {
        deviceId,
        status: Status.IN_PROGRESS,
      };

      this.updateDeviceInList(deviceToBeCheckedIn);
      input.value = '';
      input.focus();

      const devicesWithReadyState = this.devicesToBeCheckedIn.filter(
          device => device.status === Status.READY);

      if (this.shelf.capacity >= devicesWithReadyState.length) {
        this.deviceService.checkReadyForAudit(deviceId).subscribe(
            success => {
              deviceToBeCheckedIn.status = Status.READY;
              deviceToBeCheckedIn.message = success;
            },
            error => {
              deviceToBeCheckedIn.status = Status.ERROR;
              deviceToBeCheckedIn.message = error;
            },
        );
      } else {
        deviceToBeCheckedIn.status = Status.ERROR;
        deviceToBeCheckedIn.message =
            `Device can't be checked in because shelf has exceed its capacity.`;
      }
    }
  }

  /**
   * Updates the device inside the devicesToBeCheckedIn list, appending if
   * they're non-existant or replaced with the new status if they're already in
   * the list.
   * @param deviceToBeCheckedIn Device that will be checked in or replaced in
   *     the list.
   */
  private updateDeviceInList(deviceToBeCheckedIn: DeviceOnAction) {
    const deviceToBeRemoved = this.devicesToBeCheckedIn.find(
        device => device.deviceId === deviceToBeCheckedIn.deviceId);
    // Early return since if it's not found in devicesToBeCheckedIn then an
    // index value cannot be obtained later on.
    if (deviceToBeRemoved === undefined) {
      this.devicesToBeCheckedIn.push(deviceToBeCheckedIn);
      return;
    }
    const index = this.devicesToBeCheckedIn.indexOf(deviceToBeRemoved);
    if (index !== -1) {
      this.devicesToBeCheckedIn[index] = deviceToBeCheckedIn;
    } else {
      this.devicesToBeCheckedIn.push(deviceToBeCheckedIn);
    }
  }

  /**
   * Removes a device to the pool of devices to be checked in.
   *
   * @param device Device element to be removed from the pool.
   */
  removeDevice(device: DeviceOnAction) {
    const index = this.devicesToBeCheckedIn.indexOf(device);
    if (index > -1) {
      this.devicesToBeCheckedIn.splice(index, 1);
    }
  }

  /**
   * Property that defines if the pool of devices is healthy to be checked
   *  in.
   */
  get isReadyForAudit() {
    return this.isEmpty || this.allDevicesReady;
  }

  /** Checks all devices states and makes sure all of the are on Status.READY */
  get allDevicesReady() {
    return this.devicesToBeCheckedIn
               .filter(
                   deviceToBeCheckedIn =>
                       deviceToBeCheckedIn.status === Status.READY)
               .length === this.devicesToBeCheckedIn.length;
  }

  /** Performs the shelf audit with all devices that are in the current pool. */
  audit() {
    const deviceIdList =
        this.devicesToBeCheckedIn.map(device => device.deviceId);
    this.shelfService.audit(this.shelf, deviceIdList).subscribe(() => {
      this.devicesToBeCheckedIn = [];
      this.backToShelves();
    });
  }

  /** Performs an audit as empty on a shelf. */
  auditAsEmpty() {
    const dialogTitle = 'Audit shelf as empty';
    const dialogContent = `Are you sure you want to audit the shelf: ${
        this.shelf.location} as empty ? `;
    this.dialog.confirm(dialogTitle, dialogContent).subscribe(result => {
      if (result) {
        this.shelfService.audit(this.shelf).subscribe(() => {
          this.backToShelves();
        });
      }
    });
  }
}
