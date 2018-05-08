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

import {DamagedModule} from '../../../../../shared/components/damaged';
import {ExtendModule} from '../../../../../shared/components/extend';
import {GuestModeModule} from '../../../../../shared/components/guest';
import {LostModule} from '../../../../../shared/components/lost';
import {MaterialModule} from '../../core/material_module';
import {DeviceActionBoxModule} from '../device_action_box';
import {DeviceActionsMenuModule} from '../device_actions_menu';
import {DeviceButtonsModule} from '../device_buttons';

import {DeviceListTable} from './device_list_table';

export * from './device_list_table';

@NgModule({
  declarations: [
    DeviceListTable,
  ],
  exports: [
    DeviceListTable,
  ],
  imports: [
    BrowserModule,
    DamagedModule,
    DeviceActionBoxModule,
    DeviceActionsMenuModule,
    DeviceButtonsModule,
    GuestModeModule,
    ExtendModule,
    LostModule,
    MaterialModule,
    RouterModule,
  ],
})
export class DeviceListTableModule {
}
