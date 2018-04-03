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



import {Component, OnInit} from '@angular/core';
import {ActivatedRoute} from '@angular/router';
import * as moment from 'moment';
import {switchMap} from 'rxjs/operators';

import {Damaged} from '../../../../../shared/components/damaged';
import {Extend} from '../../../../../shared/components/extend';
import {GuestMode} from '../../../../../shared/components/guest';
import {Lost} from '../../../../../shared/components/lost';
import {ResumeLoan} from '../../../../../shared/components/resume_loan';
import {Device} from '../../models/device';
import {User} from '../../models/user';
import {DeviceService} from '../../services/device';
import {UserService} from '../../services/user';

/**
 * Component that renders the device info card template.
 */
@Component({
  preserveWhitespaces: true,
  host: {
    'class': 'mat-typography',
  },
  selector: 'loaner-device-info-card',
  styleUrls: ['device_info_card.scss'],
  templateUrl: 'device_info_card.html',
})
export class DeviceInfoCard implements OnInit {
  // Component's core variables.
  user = new User();
  /* List of devices assigned to the user. */
  loanedDevices: Device[];
  /* Index of the tab to focus on landing when coming from route with id. */
  selectedTab = 0;

  constructor(
      private readonly damagedService: Damaged,
      private readonly deviceService: DeviceService,
      private readonly extendService: Extend,
      private readonly guestModeService: GuestMode,
      private readonly lostService: Lost,
      private readonly resumeService: ResumeLoan,
      private readonly route: ActivatedRoute,
      private readonly userService: UserService) {}

  ngOnInit() {
    this.userService.whenUserLoaded()
        .pipe(switchMap((user) => {
          this.user = user;
          return this.deviceService.listUserDevices();
        }))
        .subscribe(userDevices => {
          this.loanedDevices = userDevices.sort((a, b) => {
            if (!a.lastHeartbeat || !b.lastHeartbeat) return 0;
            return b.lastHeartbeat.getTime() - a.lastHeartbeat.getTime();
          });

          this.route.params.subscribe((params) => {
            if (params.id) {
              this.selectedTab = this.loanedDevices.findIndex(
                  device => device.serialNumber === params.id);
            }
          });
        });
  }
  /**
   * Calls the deviceService to enable guest mode.
   *
   * @param device The device to take action on.
   */
  onGuestModeEnabled(device: Device) {
    this.deviceService.enableGuestMode(device.serialNumber).subscribe(() => {
      this.guestModeService.finished();
      device.guestEnabled = true;
    });
  }

  /**
   * Calls deviceService API for extending a device and defines new due date.
   *
   * @param device The device to take action on.
   * @param formattedNewDueDate New date as string in the following format:
   *    YYYY-MM-DD[T][00]:[00]:[00]
   */
  onExtended(device: Device, formattedNewDueDate: string) {
    const newReturnDate = moment(formattedNewDueDate).toDate();
    this.deviceService.extend(formattedNewDueDate, device.serialNumber)
        .subscribe(
            () => {
              this.extendService.finished(newReturnDate);
              device.dueDate = newReturnDate;
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
   * @param damagedReason The reason why this device is being marked as damaged.
   */
  onDamaged(device: Device, damagedReason: string) {
    this.deviceService.markAsDamaged(device.serialNumber, damagedReason)
        .subscribe(
            () => {
              this.damagedService.finished();
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
    this.deviceService.markAsLost(device.serialNumber)
        .subscribe(
            () => {
              this.lostService.finished();
            },
            () => {
              this.lostService.close();
            });
  }

  /** Calls the deviceService to resume the loan. */
  onLoanResumed(device: Device) {
    this.deviceService.resumeLoan(device.serialNumber).subscribe(() => {
      this.resumeService.finished();
      device.pendingReturn = false;
    });
  }
}
