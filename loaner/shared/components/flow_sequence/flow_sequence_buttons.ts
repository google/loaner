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

import {Component, Input, OnInit, Output} from '@angular/core';
import {Subject} from 'rxjs';

import {FlowState, NavigationLabels, Step} from './index';

/**
 * Controller for buttons used in flow sequence.
 * Takes in labels and current step numbers and emits boolean values if certain
 * buttons are pressed.
 */
@Component({
  selector: 'loaner-flow-sequence-buttons',
  styleUrls: ['./flow_sequence.scss'],
  templateUrl: './flow_sequence_buttons.ng.html',
})
export class LoanerFlowSequenceButtons implements OnInit {
  /**
   * The step number of which the flow is on.
   * Used to determine if back button or finished button should be displayed.
   */
  @Input() currentStepNumber = 0;
  /**
   * The maximum amount of steps in a flow.
   * Used to determine if back button or finished button should be displayed.
   */
  @Output()
  get maxStepNumber(): number {
    return this.steps.length - 1;
  }
  /** FlowState provided by the flowSequence. */
  @Input() flowState = new Subject<FlowState>();
  /** Array of steps in the flow sequence. */
  @Input() steps!: Step[];
  /** Emits an event when forward button is pressed. */
  @Output() forward = new Subject<boolean>();
  /** Emits an event when back button is pressed. */
  @Output() back = new Subject<boolean>();
  /** Emits an event when finished button is pressed. */
  @Output() finished = new Subject<boolean>();
  /** Defines the aria and toolTip labels for the butons. */
  @Input() navLabels!: NavigationLabels;
  /** Defines whether the flow can proceed forward. */
  @Input() canProceed = true;
  /** Defines whether the buttons should be available to click. */
  @Input() allowButtonClick = true;

  ngOnInit() {
    this.flowState.subscribe(state => {
      // Handle optional information delivered in a state change.
      if (state.optional) {
        if (state.optional.activeStepNumber === 0 ||
            state.optional.activeStepNumber) {
          this.currentStepNumber = state.optional.activeStepNumber;
        }
      }
    });
  }

  goForward() {
    if (this.canProceed && this.allowButtonClick) {
      this.forward.next(true);
    }
  }

  goBack() {
    if (this.allowButtonClick) {
      this.back.next(true);
    }
  }

  finishFlow() {
    this.finished.next(true);
  }
}
