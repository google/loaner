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
import {FormsModule} from '@angular/forms';
import {DateAdapter} from '@angular/material/core';

import {LoaderModule} from '../../../../../shared/components/loader';
import {LoanerDateAdapter} from '../../../../../shared/components/loaner_date_adapter/LoanerDateAdapter';
import {FocusModule} from '../../../../../shared/directives/focus';
import {FailureModule} from '../../shared/failure';
import {Loan} from '../../shared/loan';
import {ReturnDateService} from '../../shared/return_date_service';

import {MaterialModule} from './material_module';
import {ReturnComponent} from './return';

@NgModule({
  declarations: [ReturnComponent],
  exports: [ReturnComponent],
  imports: [
    CommonModule,
    FailureModule,
    FocusModule,
    FormsModule,
    LoaderModule,
    MaterialModule,
  ],
  providers: [
    Loan,
    ReturnDateService,
    {provide: DateAdapter, useClass: LoanerDateAdapter},
  ],
})
export class ReturnModule {
}

export * from './return';
