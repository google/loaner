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

import {Component, Input} from '@angular/core';

/**
 * Main component to building a loan maintenance card.
 *
 * It has the <loaner-loan-actions-card> and the underneath buttons:
 *  <loan-button extendButton>
 *  <loan-button guestButton>
 *  <loan-button returnButton>
 *  <loan-button damagedButton>
 *  <loan-button lostButton>
 *
 * Only the buttons that you define within loaner-loan-actions-card component
 * will be rendered on the card. All buttons has a (done) event emmiter for a
 * callback to be assigned to it. Eg:
 *
 * <loaner-loan-actions-card>
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
  @Input() pendingReturn = false;
  @Input() dueDate: Date;
  @Input() assetTag = '';
  @Input() serialNumber = '';
  @Input() oneOfMany = false;
}
