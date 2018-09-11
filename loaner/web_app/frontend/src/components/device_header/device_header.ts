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

import {Component, Input} from '@angular/core';

/**
 * Implements the Device Header component.
 */
@Component({
  selector: 'loaner-device-header',
  styleUrls: ['device_header.scss'],
  templateUrl: 'device_header.ng.html',

})
export class DeviceHeader {
  /** Title of the device header to be displayed. */
  @Input() cardTitle = 'Default Title';
  /** If whether the action buttons taken on each row should be displayed. */
  @Input() showButtons = true;
}
