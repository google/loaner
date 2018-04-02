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
import {BehaviorSubject, Observable} from 'rxjs';

import {Device} from '../../models/device';
import {DeviceService} from '../../services/device';

/** UserLoan data class to be displayed in a mat-table for device_list_table. */
@Injectable()
export class UserLoansData {
  /** Data that the backend streams to the frontend. */
  dataChange = new BehaviorSubject<Device[]>([]);

  constructor(private readonly deviceService: DeviceService) {
    this.refresh();
  }

  /** Property to return a list of shelves based on streamed data. */
  get data(): Device[] {
    return this.dataChange.value;
  }

  /** Updates the shelf data from the ShelfService. */
  refresh() {
    this.deviceService.list().subscribe(devices => {
      this.dataChange.next(devices);
    });
  }
}
