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
import {BrowserModule} from '@angular/platform-browser';
import {RouterModule} from '@angular/router';

import {MaterialModule} from '../../core/material_module';
import {ShelfButtons} from './shelf_buttons';

export * from './shelf_buttons';

@NgModule({
  declarations: [
    ShelfButtons,
  ],
  exports: [
    ShelfButtons,
  ],
  imports: [
    BrowserModule,
    MaterialModule,
    RouterModule,
  ],
})
export class ShelfButtonsModule {
}
