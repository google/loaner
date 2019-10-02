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

import {Extend} from '../../extend';

@Component({
  selector: 'loan-button[extendButton]',
  styleUrls: ['./loan_actions_card.scss'],
  template: `
  <button *ngIf="canExtend"
          mat-raised-button class="action-button"
          (click)="openDialog()"
          color="primary"
          aria-label="Click to extend the duration of this loan.">
    Extend
  </button>
  <span *ngIf="!canExtend"
        matTooltip="This loaner can not be extended any further.">
    <button mat-raised-button
            disabled
            class="action-button"
            color="primary"
            aria-disabled="This loaner can not be extended any further.">
      Extend
    </button>
  </span>`,
})
export class ExtendButton {
  @Input() canExtend = false;
  @Input() dueDate!: Date;
  @Input() maxExtendDate!: Date;
  @Output() done = new Subject<string>();

  constructor(private readonly extendService: Extend) {}

  /** Opens the loan extension dialog. */
  openDialog() {
    this.extendService.openDialog(this.dueDate, this.maxExtendDate);
    this.extendService.onExtended.subscribe(newDate => {
      this.done.next(newDate);
    });
  }
}
