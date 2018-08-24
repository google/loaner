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
import {MatDialog} from '@angular/material';
import * as moment from 'moment';

import {Damaged} from '../../../../../shared/components/damaged';
import {Extend} from '../../../../../shared/components/extend';
import {GuestMode} from '../../../../../shared/components/guest';
import {LoaderView} from '../../../../../shared/components/loader';
import {ResumeLoan} from '../../../../../shared/components/resume_loan';
import {ConfigService} from '../../../../../shared/config';
import {Device} from '../../../../../shared/models/device';
import {Background} from '../../shared/background_service';
import {FailAction, FailType, Failure} from '../../shared/failure';
import {Loan} from '../../shared/loan';

const ADDITIONAL_MANAGEMENT_TEXT = `If you need guidance or have a question,
be sure to check out our Troubleshoot and FAQ buttons below.`;

@Component({
  host: {
    'class': 'mat-typography',
  },
  selector: 'status',
  styleUrls: ['./status.scss'],
  templateUrl: './status.ng.html',
})
export class StatusComponent extends LoaderView implements OnInit {
  additionalText = ADDITIONAL_MANAGEMENT_TEXT;
  device = new Device();
  newReturnDate!: Date;

  /** If the device model data is populated. */
  get hasDevices() {
    return Boolean(this.device.identifier);
  }

  constructor(
      private readonly bg: Background,
      private readonly config: ConfigService,
      private readonly damaged: Damaged,
      private readonly extend: Extend,
      private readonly failure: Failure,
      private readonly guestMode: GuestMode,
      private readonly loan: Loan,
      private readonly resumeService: ResumeLoan,
      readonly dialog: MatDialog,
  ) {
    super(true);
  }

  ngOnInit() {
    this.setLoanInfo();
  }

  /** Set loan information for manage view. */
  setLoanInfo() {
    this.loan.getDevice().subscribe(
        device => {
          this.device = device;
          this.ready();
        },
        error => {
          const message =
              `We had some trouble getting some initial information.`;
          this.failure.register(
              message, FailType.Network, FailAction.Quit, error);
        });
  }

  /**
   * Toggle guest mode for the device
   */
  onGuestModeEnabled() {
    this.loan.enableGuestMode().subscribe(
        response => {
          this.guestMode.finished();
          this.device.guestEnabled = true;
        },
        error => {
          const message = 'Something happened with enabling guest mode.';
          this.failure.register(
              message, FailType.Other, FailAction.Quit, error);
        });
  }

  /** Calls the loan API to extend the device. */
  onExtended(formattedNewDueDate: string) {
    this.newReturnDate = moment(formattedNewDueDate).toDate();
    this.loan.extend(formattedNewDueDate)
        .subscribe(
            () => {
              this.extend.finished(this.newReturnDate);
              this.device.dueDate = this.newReturnDate;
            },
            error => {
              this.loading = false;
              const message = 'Something happened with extending this device.';
              this.failure.register(
                  message, FailType.Other, FailAction.Quit, error);
            });
  }

  /** Calls the loan API to mark the device as damaged. */
  onDamaged(damagedReason: string) {
    this.loan.damaged(damagedReason)
        .subscribe(
            () => {
              this.damaged.finished();
            },
            error => {
              this.damaged.close();
              const message =
                  'Something happened with marking this device as damaged.';
              this.failure.register(
                  message, FailType.Other, FailAction.Quit, error);
            });
  }

  /** Trigger the return flow. */
  onReturned() {
    if (this.config.LOGGING) {
      console.info('Returning Device');
    }
    this.bg.openView('offboarding');
  }

  /** Calls the loan API to resume the loan. */
  onLoanResumed() {
    this.loan.resumeLoan().subscribe(
        response => {
          this.resumeService.finished();
          this.device.pendingReturn = false;
        },
        error => {
          const message = 'An error occurred when resuming this loan.';
          this.failure.register(
              message, FailType.Other, FailAction.Quit, error);
        });
  }
}
