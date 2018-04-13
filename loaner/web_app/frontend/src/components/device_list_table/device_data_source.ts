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

import {DataSource} from '@angular/cdk/table';
import {MatSort} from '@angular/material';
import {BehaviorSubject, merge, Observable} from 'rxjs';
import {map} from 'rxjs/operators';

import {Device, DeviceChipStatus} from '../../models/device';

import {DeviceData} from './device_data';

export interface DeviceFilter {
  token: string;
  filter(device: Device): boolean;
}

/**
 * Device data source to provide what data should be rendered in the Angular
 * Material's mat-table.
 * https://material.angular.io/components/table/overview
 */
export class DeviceDataSource extends DataSource<{}> {
  private filterChange = new BehaviorSubject('');
  private deviceFilters: DeviceFilter[] = [
    {
      token: 'assigned',
      filter: device =>
          device.chips.some(chip => chip.status === DeviceChipStatus.ASSIGNED)
    },
    {
      token: 'unassigned',
      filter: device =>
          device.chips.some(chip => chip.status === DeviceChipStatus.UNASSIGNED)
    },
    {
      token: 'locked',
      filter: device =>
          device.chips.some(chip => chip.status === DeviceChipStatus.LOCKED)
    },
    {
      token: 'lost',
      filter: device =>
          device.chips.some(chip => chip.status === DeviceChipStatus.LOST)
    },
    {
      token: 'pending return',
      filter: device => device.chips.some(
          chip => chip.status === DeviceChipStatus.PENDING_RETURN)
    },
    {
      token: 'damaged',
      filter: device =>
          device.chips.some(chip => chip.status === DeviceChipStatus.DAMAGED)
    }
  ];

  constructor(
      private readonly deviceData: DeviceData, private readonly sort: MatSort) {
    super();
  }

  get filter(): string {
    return this.filterChange.value;
  }

  set filter(filter: string) {
    this.filterChange.next(filter);
  }

  /**
   * Connect function called by the table to retrieve one stream containing the
   * data to render.
   */
  connect(): Observable<Device[]> {
    const displayDataChanges = [
      this.deviceData.dataChange,
      this.sort.sortChange,
      this.filterChange,
    ];

    return merge(...displayDataChanges)
        .pipe(map(() => this.getSortedData().filter((device: Device) => {
          if (this.deviceFilters
                  .filter(
                      deviceFilter => this.filter.split(' ').some(
                          userFilterPart =>
                              deviceFilter.token.startsWith(userFilterPart)))
                  .some(filter => filter.filter(device))) {
            return true;
          }
          return this.filter.split(' ').some(
              userFilterPart =>
                  device.assignedUser.startsWith(userFilterPart) ||
                  device.id.toLowerCase().startsWith(userFilterPart));
        })));
  }

  disconnect() {
    // No-op. Must be implemented by cdk's DataSource.
  }

  /** Returns a sorted copy of the database data. */
  getSortedData(): Device[] {
    const data = this.deviceData.data.slice();
    if (!this.sort.active || this.sort.direction === '') {
      return data;
    }

    return data.sort((a, b) => {
      let propertyA: Date|string = '';
      let propertyB: Date|string = '';

      switch (this.sort.active) {
        case 'id':
          [propertyA, propertyB] = [a.id, b.id];
          break;
        case 'returnDate':
          [propertyA, propertyB] = [a.dueDate, b.dueDate];
          break;
        case 'deviceModel':
          [propertyA, propertyB] = [a.deviceModel, b.deviceModel];
          break;
        case 'lastUpdate':
          [propertyA, propertyB] = [a.lastUpdate, b.lastUpdate];
          break;
        case 'assignedUser':
          [propertyA, propertyB] = [a.assignedUser, b.assignedUser];
          break;
        default:
          break;
      }

      const valueA = Number(propertyA);
      const valueB = Number(propertyB);

      return (
          (valueA < valueB ? -1 : 1) *
          (this.sort.direction === 'asc' ? 1 : -1));
    });
  }
}
