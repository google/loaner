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

import {AfterViewInit, Component, ContentChildren, Directive, HostBinding, Input, OnInit, Output, QueryList, ViewEncapsulation} from '@angular/core';
import {Subject} from 'rxjs';
import {takeUntil} from 'rxjs/operators';

import {LoanerFlowSequenceButtons} from './flow_sequence_buttons';
import {FlowState, FlowStateOptional, Step} from './index';

/**
 * Selector to be placed on components which are to be flowChildren.
 */
@Directive({selector: '[loaner-flow-child], [loanerFlowChild]'})
export class LoanerFlowSequenceChild {
  @HostBinding('hidden') hidden = false;
}

/**
 * LoanerFlowSequence creates a wrapper around a set of components in the
 * ng-content and cycles through these in an ordered route-like fashion.
 * Injected components are hidden or shown depending on their step number.
 * Steps can be changed programatically through this component or can be hooked
 * up via the <loaner-flow-sequence-buttons> component.
 */
@Component({
  encapsulation: ViewEncapsulation.None,
  host: {'class': 'mat-typography'},
  selector: 'loaner-flow-sequence',
  styleUrls: ['./flow_sequence.scss'],
  template: '<ng-content></ng-content>',
})
export class LoanerFlowSequence implements OnInit, AfterViewInit {
  /** Steps in order of when they are to appear. */
  @Input() steps!: Step[];
  /** Emits the current step the flow is on. */
  @Output() activeStep = new Subject<Step>();
  /** Emits the previous step from the flow. */
  @Output() previousStep = new Subject<Step>();
  /** The current step number in a flow sequence. */
  @Output() currentStepNumber = 0;
  /** The maximum amount of steps or final step number in a flow sequence. */
  @Output()
  get maxStepNumber(): number {
    return this.steps.length - 1;
  }
  /** Emits the current state of the flow when it has changed. */
  @Output() flowState = new Subject<FlowState>();
  flowFinished$ = new Subject<void>();
  flowFinished = false;

  /**
   * Query list of all children elements to be used in the flow sequence.
   */
  @ContentChildren(LoanerFlowSequenceChild)
  flowChildren!: QueryList<LoanerFlowSequenceChild>;

  /** Optional input for flowSequence buttons. */
  @Input() flowSequenceButtons?: LoanerFlowSequenceButtons;

  ngOnInit() {
    this.flowFinished$.subscribe(() => {
      this.flowFinished = true;
    });
  }

  ngAfterViewInit() {
    // Timeout used to fix ExpressionChangedAfterItHasBeenCheckedError
    setTimeout(() => {
      this.updateVisibleChildren();
    });
  }

  /**
   * Toggle hidden for elements based on which flow step the app is on.
   */
  updateVisibleChildren() {
    for (let i = 0; i < this.flowChildren.toArray().length; i++) {
      if (this.currentStepNumber === i) {
        this.flowChildren.toArray()[i].hidden = false;
      } else {
        this.flowChildren.toArray()[i].hidden = true;
      }
    }
  }

  /**
   * Send necessary information to go forward in a flow sequence.
   */
  goForward() {
    this.currentStepNumber < this.maxStepNumber ?
        this.currentStepNumber += 1 :
        this.currentStepNumber = this.maxStepNumber;
    const step = this.steps[this.currentStepNumber];
    const previousStep = this.steps[this.currentStepNumber - 1];
    this.handleFlowState(step, previousStep, {
      activeStepNumber: this.currentStepNumber,
      maxStepNumber: this.maxStepNumber,
    });
  }

  /**
   * Send necessary information to go back in a flow sequence.
   */
  goBack() {
    this.currentStepNumber > 0 ? this.currentStepNumber -= 1 :
                                 this.currentStepNumber = 0;
    const step = this.steps[this.currentStepNumber];
    const previousStep = this.steps[this.currentStepNumber + 1];
    this.handleFlowState(step, previousStep, {
      activeStepNumber: this.currentStepNumber,
      maxStepNumber: this.maxStepNumber,
    });
  }

  /**
   * Navigate to a specific step in the flow sequence.
   * @param id Step id to navigate to.
   */
  goToStep(id: string, optional?: FlowStateOptional) {
    const index = this.findStep(id);
    if (index) {
      const newStep = this.steps[index];
      const previousStep = this.steps[this.currentStepNumber];
      this.handleFlowState(newStep, previousStep, optional);
    }
  }

  /**
   * Find a given step array index for a given step.id.
   * @param id Of the Step to find
   */
  findStep(id: string): number {
    for (let i = 0; i < this.steps.length; i++) {
      const step = this.steps[i];
      if (step.id === id) {
        return i;
      }
    }
    return -1;
  }
  /**
   * Send necessary information to finish a flow sequence.
   */
  finishFlow() {
    const step = this.steps[this.currentStepNumber];
    const previousStep = this.steps[this.currentStepNumber - 1];
    this.handleFlowState(step, previousStep, {
      flowFinished: true,
    });
    this.flowFinished$.next();
  }

  /**
   * Listen to actions on flow sequence buttons and take appropriate action.
   * @param buttons LoanerFlowSequenceButtons component to listen to.
   */
  setupFlowButtonsListener() {
    if (this.flowSequenceButtons) {
      this.flowSequenceButtons.forward.subscribe(val => {
        if (val) this.goForward();
      });

      this.flowSequenceButtons.back.subscribe(val => {
        if (val) this.goBack();
      });

      this.flowSequenceButtons.finished.pipe(takeUntil(this.flowFinished$))
          .subscribe(val => {
            if (val) this.finishFlow();
          });
    }
  }

  /**
   * Construct the flow State and push to the flowState Subject.
   * @param activeStep Current Step the flow sequence is on.
   * @param previousStep Previous Step the flow sequence was on.
   * @param optional Set of optional paramsters that can be passed in the flow.
   */
  private handleFlowState(
      activeStep: Step, previousStep: Step, optional?: FlowStateOptional) {
    this.activeStep.next(activeStep);
    this.previousStep.next(previousStep);
    if (!this.flowFinished) {
      this.flowState.next({
        activeStep,
        previousStep,
        optional,
      });
      this.updateVisibleChildren();
    }
  }
}
