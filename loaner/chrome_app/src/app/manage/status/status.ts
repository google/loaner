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

import {Component, Injectable, OnInit} from '@angular/core';
import {MatDialog} from '@angular/material';
import * as moment from 'moment';
import {switchMap} from 'rxjs/operators';

import {Damaged} from '../../../../../shared/components/damaged';
import {Extend} from '../../../../../shared/components/extend';
import {GuestMode} from '../../../../../shared/components/guest';
import {LoaderView} from '../../../../../shared/components/loader';
import {ResumeLoan} from '../../../../../shared/components/resume_loan';
import {CHROME_DEV_MODE, LOGGING} from '../../../../../shared/config';
import {Background} from '../../shared/background_service';
import {FailAction, FailType, Failure} from '../../shared/failure';
import {Loan} from '../../shared/loan';

import {StatusService} from './status_service';

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
  dueDate: Date;
  guestAllowed: boolean;
  guestEnabled: boolean;
  maxExtendDate: Date;
  newReturnDate: Date;
  pendingReturn: boolean;
  userDisplayName: string;

  constructor(
      private readonly bg: Background,
      private readonly damaged: Damaged,
      private readonly extend: Extend,
      private readonly failure: Failure,
      private readonly guestMode: GuestMode,
      private readonly loan: Loan,
      private readonly resumeService: ResumeLoan,
      private readonly status: StatusService,
      readonly dialog: MatDialog,
  ) {
    super(true);
  }

  ngOnInit() {
    this.refreshContent();
  }

  /**
   * Grabs necessary content on the page and updates it.
   */
  refreshContent() {
    this.getGivenName();
  }

  /** Set loan information for manage view. */
  setLoanInfo(grabGivenName?: boolean) {
    let retrievedLoanInfo: LoanResponse;
    this.loan.getLoan(grabGivenName)
        .pipe(switchMap(loanInfo => {
          retrievedLoanInfo = loanInfo;
          return this.loan.getDevice();
        }))
        .subscribe(
            deviceInfo => {
              if (grabGivenName) {
                if (retrievedLoanInfo.given_name) {
                  this.status.setGivenNameInChromeStorage(
                      retrievedLoanInfo.given_name);
                  this.userDisplayName = retrievedLoanInfo.given_name;
                } else {
                  this.status.setGivenNameInChromeStorage('there');
                  this.userDisplayName = retrievedLoanInfo.given_name;
                }
              }
              this.setLocalValues(deviceInfo);
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
   * Sets the local values to the populated info from the API.
   * @param deviceInfo represents the various info for a given device.
   */
  private setLocalValues(deviceInfo: DeviceInfoResponse) {
    this.dueDate = moment(deviceInfo.due_date!).toDate();
    this.maxExtendDate = moment(deviceInfo.max_extend_date!).toDate();
    this.guestEnabled = deviceInfo.guest_enabled!;
    this.guestAllowed = deviceInfo.guest_permitted!;
    this.pendingReturn = !!deviceInfo.mark_pending_return_date;
    this.canExtend();
  }

  /** Gets the given name of a user and calls for setting initial loan info. */
  getGivenName() {
    this.status.getGivenNameFromChromeStorage().subscribe(
        name => {
          if (name) {
            this.userDisplayName = name;
            this.setLoanInfo(false);
          } else {
            this.setLoanInfo(true);
          }
        },
        error => {
          // Error only occurs when givenName can't be found in local storage.
          this.setLoanInfo(true);
        });
  }

  /** Checks the dates to see if the loan can be extended. */
  canExtend() {
    if (this.dueDate == null) {
      console.error('The due date date was never defined.');
    }
    if (this.maxExtendDate == null) {
      console.error('The max extend date date was never defined.');
    }
    return moment(this.dueDate!).diff(this.maxExtendDate!, 'days') <= -1;
  }

  /**
   * Toggle guest mode for the device
   */
  onGuestModeEnabled() {
    this.loan.enableGuestMode().subscribe(
        response => {
          this.guestMode.finished();
          if (CHROME_DEV_MODE && LOGGING) {
            console.info(response);
          }
          this.guestEnabled = true;
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
              this.dueDate = this.newReturnDate;
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
    if (LOGGING) {
      console.info('Returning Device');
    }
    this.bg.openView('offboarding');
  }

  /** Calls the loan API to resume the loan. */
  onLoanResumed() {
    this.loan.resumeLoan().subscribe(
        response => {
          this.resumeService.finished();
          if (CHROME_DEV_MODE && LOGGING) {
            console.info(response);
          }
          this.pendingReturn = false;
        },
        error => {
          const message = 'An error occurred when resuming this loan.';
          this.failure.register(
              message, FailType.Other, FailAction.Quit, error);
        });
  }
}
