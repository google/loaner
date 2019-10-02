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
import * as moment from 'moment';

import {LoaderView} from '../../../../../shared/components/loader';
import {ConfigService} from '../../../../../shared/config';
import {Device} from '../../../../../shared/models/device';
import {FailAction, FailType, Failure} from '../../shared/failure';
import {Loan} from '../../shared/loan';
import {ReturnDateService} from '../../shared/return_date_service';

@Component({
  host: {'class': 'mat-typography'},
  selector: 'return',
  styleUrls: ['./return.scss'],
  templateUrl: './return.ng.html',
})
export class ReturnComponent extends LoaderView implements OnInit {
  device = new Device();
  newReturnDate?: Date;
  toBeSubmitted = true;
  validDate = true;
  webAppUrl: string;

  constructor(
      private readonly config: ConfigService, private failure: Failure,
      private loan: Loan, private returnService: ReturnDateService) {
    super(true);
    this.webAppUrl = this.config.webAppUrl;
  }

  ngOnInit() {
    this.loan.getDevice().subscribe(
        device => {
          this.device = device;
          this.newReturnDate = this.getMinimumReturnDate();
          this.initializeDateServiceVariables(device);
          this.ready();
        },
        error => {
          this.ready();
          const message = `We had some trouble getting your loan information.`;
          this.failure.register(
              message, FailType.Network, FailAction.Quit, error);
        });

    this.returnService.validDate.subscribe(validDate => {
      this.validDate = validDate;
    });
  }

  private initializeDateServiceVariables(device: Device) {
    this.returnService.updateDueDate(device.dueDate);
    this.returnService.updateNewReturnDate(device.dueDate)
        .subscribe(newReturnDate => {
          if (this.newReturnDate instanceof Date) {
            this.newReturnDate = newReturnDate!;
          }
        });
    this.returnService.updateMaxReturnDate(device.maxExtendDate);

    // Do validation checks on changes.
    this.returnService.validationChecks().subscribe(val => {
      this.validDate = val;
      this.returnService.updateValidDate(val);
    });
  }

  /** Gets the minimum return date. */
  getMinimumReturnDate(): Date {
    const today = moment().set({
      hour: 0,
      minute: 0,
      second: 0,
    });

    return moment(today).add(1, 'd').toDate();
  }

  /**
   * Prevents non 0-9 and / characters from being used in the date field.
   * @param event The DOM event to be tracked on key presses.
   */
  validateField(event: KeyboardEvent): boolean {
    const pattern = /[0-9\/]/;
    const inputCharacters = String.fromCharCode(event.charCode);

    return pattern.test(inputCharacters);
  }
}
