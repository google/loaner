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

import {NgModule} from '@angular/core';
import {FormsModule, ReactiveFormsModule} from '@angular/forms';
import {BrowserModule} from '@angular/platform-browser';
import {RouterModule} from '@angular/router';

import {MinValidatorModule} from '../../../../../shared/directives/min_validator';
import {MaterialModule} from '../../core/material_module';
import {DialogsModule} from '../../services/dialog';

import {ShelfActionsCard} from './shelf_actions';

export * from './shelf_actions';

@NgModule({
  declarations: [
    ShelfActionsCard,
  ],
  exports: [
    ShelfActionsCard,
  ],
  imports: [
    BrowserModule,
    DialogsModule,
    FormsModule,
    ReactiveFormsModule,
    MaterialModule,
    MinValidatorModule,
    RouterModule,
  ],
})
export class ShelfActionsModule {
}
