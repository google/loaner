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

import {ConfigService} from '../../../../../shared/config';
import {Background} from '../background_service';

import {Failure, FailureComponentDialog} from './failure';
import {MaterialModule} from './material_module';

@NgModule({
  declarations: [FailureComponentDialog],
  entryComponents: [FailureComponentDialog],
  imports: [
    BrowserAnimationsModule,
    CommonModule,
    MaterialModule,
  ],
  providers: [
    Background,
    ConfigService,
    Failure,
  ],
})
export class FailureModule {
}

export * from './failure';
