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

import {Damaged} from '../../damaged';

@Component({
  selector: 'loan-button[damagedButton]',
  styleUrls: ['./loan_actions_card.scss'],
  template: `<button mat-raised-button class="action-button" color="warn"
             (click)="openDialog()"
             aria-label="Click to report this device as damaged.">
               Damaged Device?
             </button>`,
})
export class DamagedButton {
  @Output() done = new Subject<string>();

  constructor(private readonly damagedService: Damaged) {}

  /** Opens the loan damaged dialog. */
  openDialog() {
    this.damagedService.openDialog();
    this.damagedService.onDamaged.subscribe(damagedReason => {
      this.done.next(damagedReason);
    });
  }
}
