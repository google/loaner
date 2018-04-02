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

import {Component, Output} from '@angular/core';
import {Subject} from 'rxjs';

import {Lost} from '../../lost';

@Component({
  selector: 'loan-button[lostButton]',
  styleUrls: ['./loan_actions_card.scss'],
  template: `
  <button mat-raised-button class="action-button" color="warn"
          (click)="openDialog()"
          aria-label="Click to report this device as lost.">
    Device Lost?
  </button>`,
})
export class LostButton {
  @Output() done = new Subject<void>();

  constructor(private readonly lostService: Lost) {}

  /** Opens the loan lost dialog. */
  openDialog() {
    this.lostService.openDialog();
    this.lostService.onLost.subscribe(() => {
      this.done.next();
    });
  }
}
