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

import {Injectable} from '@angular/core';
import {BehaviorSubject} from 'rxjs/BehaviorSubject';
import {Observable} from 'rxjs/Observable';
import {tap} from 'rxjs/operators';

import {Device} from '../../models/device';
import {DeviceApiParams} from '../../models/device';
import {DeviceService} from '../../services/device';

/** Device data class to be displayed in a mat-table for device_list_table. */
@Injectable()
export class DeviceData {
  /** Data that the backend streams to the frontend. */
  dataChange = new BehaviorSubject<Device[]>([]);

  constructor(private readonly deviceService: DeviceService) {
    this.refresh();
  }

  /** Property to return a list of shelves based on streamed data. */
  get data(): Device[] {
    return this.dataChange.value;
  }

  /**
   * Updates the device data from the DeviceService.
   * @param filters The device api filters.
   */
  refresh(filters: DeviceApiParams = {}): Observable<Device[]> {
    return this.deviceService.list(filters).pipe(tap(devices => {
      this.dataChange.next(devices);
    }));
  }

  /**
   * Clears the device data.
   */
  clearData() {
    this.dataChange.next([]);
  }
}
