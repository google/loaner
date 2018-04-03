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
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';

import {DamagedModule} from '../../damaged';
import {ExtendModule} from '../../extend';
import {GuestModeModule} from '../../guest';
import {LostModule} from '../../lost';

import {DamagedButton} from './damaged_button';
import {ExtendButton} from './extend_button';
import {GuestButton} from './guest_button';
import {LoanActionsCardComponent} from './loan_actions_card';
import {LostButton} from './lost_button';
import {MaterialModule} from './material_module';
import {ResumeButton} from './resume_button';
import {ReturnButton} from './return_button';

const DECLARATIONS_AND_EXPORTS = [
  DamagedButton,
  ExtendButton,
  GuestButton,
  LoanActionsCardComponent,
  LostButton,
  ReturnButton,
  ResumeButton,
];

@NgModule({
  declarations: DECLARATIONS_AND_EXPORTS,
  entryComponents: [LoanActionsCardComponent],
  imports: [
    BrowserAnimationsModule,
    CommonModule,
    DamagedModule,
    ExtendModule,
    GuestModeModule,
    MaterialModule,
    LostModule,
  ],
  exports: DECLARATIONS_AND_EXPORTS,
})
export class LoanActionsCardModule {
}

export * from './loan_actions_card';
