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

import {CommonModule} from '@angular/common';
import {NgModule} from '@angular/core';
import {FlexLayoutModule} from '@angular/flex-layout';

import {LoanerFlowSequence, LoanerFlowSequenceChild} from './flow_sequence';
import {LoanerFlowSequenceButtons} from './flow_sequence_buttons';
import {MaterialModule} from './material_module';

@NgModule({
  declarations: [
    LoanerFlowSequence,
    LoanerFlowSequenceButtons,
    LoanerFlowSequenceChild,
  ],
  imports: [
    CommonModule,
    FlexLayoutModule,
    MaterialModule,
  ],
  exports: [
    LoanerFlowSequence,
    LoanerFlowSequenceButtons,
    LoanerFlowSequenceChild,
  ],
})
export class LoanerFlowSequenceModule {
}

export interface FlowState {
  activeStep: Step;
  previousStep: Step;
  optional?: FlowStateOptional;
}

export interface FlowStateOptional {
  activeStepNumber?: number;
  maxStepNumber?: number;
  flowFinished?: boolean;
}

export interface Step {
  id: string;
  title: string;
}

export interface NavigationLabels {
  done: {aria: string; toolTip: string;};
  next: {aria: string; toolTip: string;};
  previous: {aria: string; toolTip: string;};
}

export * from './flow_sequence';
export * from './flow_sequence_buttons';
