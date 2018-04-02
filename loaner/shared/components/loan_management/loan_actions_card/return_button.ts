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

@Component({
  selector: 'loan-button[returnButton]',
  styleUrls: ['./loan_actions_card.scss'],
  template: `
    <button mat-raised-button class="action-button"
            color="primary"
            (click)="returnDevice()"
            [disabled]="disabled"
            aria-label="Click to start the return process for this device.
            This will close the current window and open the return window.">
      Return
    </button>`,
})
export class ReturnButton {
  @Output() done = new Subject<void>();
  @Input() disabled = false;

  /** Opens the return dialog. */
  returnDevice() {
    this.done.next();
  }
}
