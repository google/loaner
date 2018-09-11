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

import {Component, OnInit, ViewChild} from '@angular/core';
import {Title} from '@angular/platform-browser';
import {ActivatedRoute} from '@angular/router';
import {Observable} from 'rxjs';

import {CONFIG} from '../../app.config';
import {DeviceEnrollUnenrollList} from '../../components/device_enroll_unenroll_list';
import {Actions, Device} from '../../models/device';

@Component({
  selector: 'loaner-device-actions-view',
  styleUrls: ['device_actions_view.scss'],
  templateUrl: 'device_actions_view.ng.html',

})
export class DeviceActionsView implements OnInit {
  /** Title for the component. */
  private readonly title = `Devices - ${CONFIG.appName}`;
  /** Current action that will be used in the device-action-box if rendered. */
  currentAction = '';

  /**
   * Device being (un)enrolled which will be inputed on
   * device_enroll_unenroll_list component.
   */
  device = new Device();
  @ViewChild('deviceEnrollUnenroll')
  deviceEnrollUnenroll!: DeviceEnrollUnenrollList;

  constructor(
      private titleService: Title, private readonly route: ActivatedRoute) {}

  ngOnInit() {
    this.titleService.setTitle(this.title);
    this.route.params.subscribe(params => {
      this.currentAction = '';
      for (const key in Actions) {
        if (params.action === Actions[key]) {
          this.currentAction = Actions[key];
        }
      }
    });
  }

  /** Can deactivate route checking. */
  canDeactivate(): Observable<boolean> {
    return this.deviceEnrollUnenroll.canDeactivate();
  }
}
