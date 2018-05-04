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

import {DamagedModule} from '../../../../../shared/components/damaged';
import {ExtendModule} from '../../../../../shared/components/extend';
import {GuestModeModule} from '../../../../../shared/components/guest';
import {LoaderModule} from '../../../../../shared/components/loader';
import {GreetingsCardModule} from '../../../../../shared/components/loan_management/greetings_card';
import {LoanActionsCardModule} from '../../../../../shared/components/loan_management/loan_actions_card';
import {ResumeLoanModule} from '../../../../../shared/components/resume_loan';
import {FocusModule} from '../../../../../shared/directives/focus/index';
import {Background} from '../../shared/background_service';
import {FailureModule} from '../../shared/failure';
import {Loan} from '../../shared/loan';
import {Storage} from '../../shared/storage/storage';

import {MaterialModule} from './material_module';
import {StatusComponent} from './status';

@NgModule({
  declarations: [StatusComponent],
  entryComponents: [StatusComponent],
  imports: [
    BrowserAnimationsModule,
    CommonModule,
    DamagedModule,
    ExtendModule,
    GreetingsCardModule,
    GuestModeModule,
    FailureModule,
    FocusModule,
    LoaderModule,
    LoanActionsCardModule,
    MaterialModule,
    ResumeLoanModule,
  ],
  providers: [
    Background,
    Loan,
    Storage,
  ],
})
export class StatusModule {
}

export * from './status';
