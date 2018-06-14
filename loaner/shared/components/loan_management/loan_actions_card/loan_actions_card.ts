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

import {Component, ContentChild, Input} from '@angular/core';

import {Device} from '../../../models/device';

import {ExtendButton} from './extend_button';
import {GuestButton} from './guest_button';

/**
 * Main component to building a loan maintenance card.
 *
 * It has the <loaner-loan-actions-card [device]="$DEVICE"> containing the input
 * [device] and the underneath buttons:
 *  <loan-button extendButton>
 *  <loan-button guestButton>
 *  <loan-button returnButton>
 *  <loan-button damagedButton>
 *  <loan-button lostButton>
 *  <loan-button resumeButton>
 *
 * Only the buttons that you define within loaner-loan-actions-card component
 * will be rendered on the card. All buttons has a (done) event emmiter for a
 * callback to be assigned to it. Eg:
 *
 * <loaner-loan-actions-card [device]="$DEVICE">
 *   <loan-button returnButton (done)="myReturnActionFunction()">
 *   </loan-button>
 *   <loan-button damagedButton (done)="myDamagedActionFunction($event)">
 *   </loan-button>
 * </loaner-loan-actions-card>
 *
 * Individual buttons and event args can be seen in the ./*_button.ts files.
 *
 * There's also an additionalManagementText Input directive that will be
 * rendered at the sub-title of the card in case you need to pass additional
 * instructions to your users.
 */
@Component({
  host: {
    'class': 'mat-typography',
  },
  selector: 'loaner-loan-actions-card',
  styleUrls: ['./loan_actions_card.scss'],
  templateUrl: './loan_actions_card.ng.html',
})
export class LoanActionsCardComponent {
  @Input() additionalManagementText = '';
  @Input() device!: Device;
  @ContentChild(ExtendButton) extendButton!: ExtendButton;
  @ContentChild(GuestButton) guestButton!: GuestButton;

  ngOnInit() {
    if (!this.device) {
      throw new Error('Device must be passed to this component.');
    }
  }

  ngDoCheck() {
    this.setupExtendButtonProperties();
    this.setupGuestModeButtonProperties();
  }

  private setupExtendButtonProperties() {
    if (this.extendButton && this.device) {
      this.extendButton.canExtend = this.device.canExtend;
      this.extendButton.dueDate = this.device.dueDate;
      this.extendButton.maxExtendDate = this.device.maxExtendDate;
    }
  }

  private setupGuestModeButtonProperties() {
    if (this.guestButton && this.device) {
      this.guestButton.guestEnabled = this.device.guestEnabled;
      this.guestButton.guestAllowed = this.device.guestAllowed;
    }
  }
}
