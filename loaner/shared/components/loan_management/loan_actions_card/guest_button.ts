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

import {Component, Input, Output} from '@angular/core';
import {Subject} from 'rxjs';

import {GuestMode} from '../../guest';

@Component({
  selector: 'loan-button[guestButton]',
  styleUrls: ['./loan_actions_card.scss'],
  template: `
  <button *ngIf="guestAllowed && !guestEnabled"
          mat-raised-button class="action-button"
          (click)="openDialog()"
          color="primary"
          aria-label="Click to enabled guest mode on this device.">
    Enable Guest
  </button>
  <span *ngIf="guestAllowed && guestEnabled"
        color="primary"
        matTooltip="Guest mode is already enabled.">
    <button mat-raised-button disabled class="action-button">
      Enable Guest
    </button>
  </span>`,
})
export class GuestButton {
  @Input() guestEnabled = false;
  @Input() guestAllowed = false;
  @Output() done = new Subject<boolean>();

  constructor(private readonly guestModeService: GuestMode) {}

  /** Opens the guest mode dialog. */
  openDialog() {
    this.guestModeService.openDialog();
    this.guestModeService.onGuestModeEnabled.subscribe(guestEnabled => {
      this.done.next(guestEnabled);
    });
  }
}
