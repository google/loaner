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

import {Location} from '@angular/common';
import {Component, OnInit} from '@angular/core';
import {ActivatedRoute, Router} from '@angular/router';
import {NEVER} from 'rxjs';
import {finalize, switchMap} from 'rxjs/operators';

import {Damaged} from '../../../../../shared/components/damaged';
import {Extend} from '../../../../../shared/components/extend';
import {GuestMode} from '../../../../../shared/components/guest';
import {LoaderView} from '../../../../../shared/components/loader';

import {Device} from '../../models/device';
import {DeviceService} from '../../services/device';

/**
 * Component that renders the device details template.
 */
@Component({
  preserveWhitespaces: true,
  selector: 'loaner-device-details',
  styleUrls: ['device_details.scss'],
  templateUrl: 'device_details.html',
})
export class DeviceDetails extends LoaderView implements OnInit {
  device = new Device();

  constructor(
      private readonly deviceService: DeviceService,
      private readonly location: Location,
      private readonly route: ActivatedRoute) {
    super(true);
  }

  ngOnInit() {
    this.route.params.subscribe((params) => {
      this.refreshDevice(params.id);
    });
  }

  /**
   * Refreshes a device using the deviceService.
   * @param deviceID the device identifier used to get the device.
   */
  refreshDevice(deviceId: string) {
    this.waiting();
    this.deviceService.getDevice(deviceId).subscribe((device: Device) => {
      this.device = device;
      this.ready();
    });
  }

  /** Navigates to the previous expected page. */
  back() {
    this.location.back();
  }
}
