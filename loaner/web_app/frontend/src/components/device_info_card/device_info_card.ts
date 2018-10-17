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
import {ActivatedRoute, Router} from '@angular/router';
import * as moment from 'moment';
import {map, switchMap, tap} from 'rxjs/operators';

import {Damaged} from '../../../../../shared/components/damaged';
import {Extend} from '../../../../../shared/components/extend';
import {GuestMode} from '../../../../../shared/components/guest';
import {Lost} from '../../../../../shared/components/lost';
import {ResumeLoan} from '../../../../../shared/components/resume_loan';
import {CONFIG} from '../../app.config';
import {Device} from '../../models/device';
import {User} from '../../models/user';
import {DeviceService} from '../../services/device';
import {UserService} from '../../services/user';

/**
 * Component that renders the device info card template.
 */
@Component({
  preserveWhitespaces: true,
  selector: 'loaner-device-info-card',
  styleUrls: ['device_info_card.scss'],
  templateUrl: 'device_info_card.ng.html',
})
export class DeviceInfoCard implements OnInit {
  // Component's core variables.
  user = new User();
  /* List of devices assigned to the user. */
  loanedDevices!: Device[];
  /* Index of the tab to focus on landing when coming from route with id. */
  selectedTab = 0;
  /* String defining what user is being requested for imitation. */
  imitatedUser: string|undefined;

  /** Boolean property if the current user has any devices assigned to them. */
  get hasDevices() {
    return this.loanedDevices && Boolean(this.loanedDevices.length);
  }

  /* Boolean stating whether a user is being imitated. */
  get isImitatingUser(): boolean {
    return Boolean(this.imitatedUser);
  }

  /* Handles the logic for what user/name to display in the greeting card */
  get userToDisplay(): string {
    if (this.isImitatingUser) {
      return this.hasDevices ? this.loanedDevices[0].assignedUser :
                               this.imitatedUser!;
    }
    return this.user ? this.user.givenName : 'there';
  }

  constructor(
      private readonly damagedService: Damaged,
      private readonly deviceService: DeviceService,
      private readonly extendService: Extend,
      private readonly guestModeService: GuestMode,
      private readonly lostService: Lost,
      private readonly resumeService: ResumeLoan,
      private readonly route: ActivatedRoute,
      private readonly router: Router,
      private readonly userService: UserService,
  ) {}

  ngOnInit() {
    this.getDevices();
  }

  /**
   * Load current user or perform the impersonating to get the list of devices
   * for user.
   */
  private getDevices() {
    this.userService.whenUserLoaded()
        .pipe(
            tap(user => this.user = user),
            switchMap(() => this.route.queryParams),
            map(params => params.user),
            switchMap(
                (userToImitate: string|undefined) =>
                    this.getDevicesForUser(userToImitate)),
            )
        .subscribe(userDevices => {
          if (this.imitatedUser && !userDevices.length) {
            this.backToSearch();
            return;
          }
          this.loanedDevices = userDevices.sort((a, b) => {
            if (!a.identifier || !b.identifier) return 0;
            return Number(b.identifier) - Number(a.identifier);
          });

          // Represents the device ID to be highlighted if given.
          this.route.params.subscribe((params) => {
            if (params.id) {
              this.selectedTab = this.loanedDevices.findIndex(
                  device => device.identifier === params.id);
            }
          });
        });
  }

  /**
   * Handles deciding whether to imitate a user or display the viewing users
   * loans.
   * @param userToImitate represents the user to imitate if provided.
   */
  private getDevicesForUser(userToImitate?: string) {
    if (userToImitate &&
        this.user.hasPermission(CONFIG.appPermissions.ADMINISTRATE_LOAN)) {
      const request = {
        'assigned_user': userToImitate,
      };
      this.imitatedUser = userToImitate;
      return this.deviceService.list(request).pipe(map(r => r.devices));
    }
    return this.deviceService.listUserDevices();
  }

  /**
   * Calls the deviceService to enable guest mode.
   *
   * @param device The device to take action on.
   */
  onGuestModeEnabled(device: Device) {
    this.deviceService.enableGuestMode(device).subscribe(() => {
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
    this.deviceService.extend(formattedNewDueDate, device)
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
    this.deviceService.returnDevice(device).subscribe(() => {
      device.pendingReturn = true;
      this.loanedDevices =
          this.loanedDevices.filter(device => !device.pendingReturn);
    });
  }

  /**
   * Calls the deviceService to mark a device as damaged.
   *
   * @param device The device to take action on.
   * @param damagedReason The reason why this device is being marked as damaged.
   */
  onDamaged(device: Device, damagedReason: string) {
    this.deviceService.markAsDamaged(device, damagedReason)
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
    this.deviceService.markAsLost(device).subscribe(
        () => {
          this.lostService.finished();
          this.getDevices();
        },
        () => {
          this.lostService.close();
        });
  }

  /** Calls the deviceService to resume the loan. */
  onLoanResumed(device: Device) {
    this.deviceService.resumeLoan(device).subscribe(() => {
      this.resumeService.finished();
      device.pendingReturn = false;
    });
  }

  /** Takes the user back to the default user view if imitating a user. */
  stopImitatingUser() {
    this.router.navigate(['user']);
    this.imitatedUser = undefined;
  }

  /**
   * This takes the user back to the search results if the user they searched
   * for has no devices.
   */
  backToSearch() {
    this.router.navigate([`/search/user/`, this.imitatedUser]);
  }
}
