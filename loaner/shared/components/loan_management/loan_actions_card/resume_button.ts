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

import {ResumeLoan} from '../../resume_loan';

@Component({
  selector: 'loan-button[resumeButton]',
  styleUrls: ['./loan_actions_card.scss'],
  template: `
    <button mat-raised-button class="action-button"
            color="primary"
            (click)="openDialog()"
            aria-label="Click to resume your loan."
            i18n-aria-label="Click to resume your loan.">
      Resume Loan
    </button>`,
})
export class ResumeButton {
  @Output() done = new Subject<boolean>();

  constructor(private readonly resumeService: ResumeLoan) {}

  /** Opens the resume progress/success dialog. */
  openDialog() {
    this.resumeService.openDialog();
    this.resumeService.onLoanResumed.subscribe(loanResumed => {
      this.done.next(loanResumed);
    });
  }
}
