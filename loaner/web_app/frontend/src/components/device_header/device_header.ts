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

import {Component, Input, OnInit} from '@angular/core';
import {ActivatedRoute} from '@angular/router';
import {Observable} from 'rxjs';

import {Device} from '../../models/device';
import {DeviceService} from '../../services/device';
import {Actions} from '../device_action_box';

/**
 * Implements the Device Header component.
 */
@Component({
  selector: 'loaner-device-header',
  styleUrls: ['device_header.scss'],
  templateUrl: 'device_header.html',

})
export class DeviceHeader implements OnInit {
  /** Title of the device header to be displayed. */
  @Input() cardTitle = 'Default Title';
  /** If whether the action buttons taken on each row should be displayed. */
  @Input() showButtons = true;

  /** Current action that will be used in the device-action-box if rendered. */
  currentAction: string;

  constructor(
      private readonly route: ActivatedRoute,
      private readonly deviceService: DeviceService,
  ) {}

  ngOnInit() {
    this.route.params.subscribe((params) => {
      this.currentAction = '';
      for (const key in Actions) {
        if (params.action === Actions[key]) {
          this.currentAction = Actions[key];
        }
      }
    });
  }

  /** Callback that's called once the device-action-box emits a device event. */
  takeActionOnDevice(device: Device) {
    let action: Observable<void>;
    switch (this.currentAction) {
      case Actions.ENROLL:
        action = this.deviceService.enroll(device);
        break;
      case Actions.UNENROLL:
        action = this.deviceService.unenroll(device);
        break;
      default:
        throw new Error('Device action not recognized.');
    }
    action.subscribe();
  }
}
