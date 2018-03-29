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
import {BehaviorSubject} from 'rxjs/BehaviorSubject';
import {Observable} from 'rxjs/Observable';
import {merge} from 'rxjs/observable/merge';
import {map} from 'rxjs/operators/map';

import {Shelf} from '../../models/shelf';

import {ShelfData} from './shelf_data';

/**
 * Shelf data source to provide what data should be rendered in the Angular
 * Material's mat-table.
 * https://material.angular.io/components/table/overview
 */
export class ShelfDataSource extends DataSource<{}> {
  private filterChange = new BehaviorSubject('');

  constructor(
      private readonly shelfData: ShelfData, private readonly sort: MatSort) {
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
  connect(): Observable<Shelf[]> {
    const displayDataChanges = [
      this.shelfData.dataChange,
      this.sort.sortChange,
      this.filterChange,
    ];

    return merge(...displayDataChanges)
        .pipe(map(() => this.getSortedData().filter((shelf: Shelf) => {
          const searchStr = shelf.name.toLowerCase();
          return searchStr.indexOf(this.filter.toLowerCase()) !== -1;
        })));
  }

  disconnect() {
    // No-op. Must be implemented by cdk's DataSource.
  }

  /** Returns a sorted copy of the database data. */
  getSortedData(): Shelf[] {
    const data = this.shelfData.data.slice();
    if (!this.sort.active || this.sort.direction === '') {
      return data;
    }

    return data.sort((a, b) => {
      let propertyA: Date|string|number = '';
      let propertyB: Date|string|number = '';

      switch (this.sort.active) {
        case 'name':
          [propertyA, propertyB] = [a.name, b.name];
          break;
        case 'capacity':
          [propertyA, propertyB] = [a.capacity, b.capacity];
          break;
        case 'lastAuditBy':
          [propertyA, propertyB] = [a.lastAuditBy, b.lastAuditBy];
          break;
        case 'lastAuditTime':
          [propertyA, propertyB] = [a.lastAuditTime, b.lastAuditTime];
          break;
        default:
          break;
      }

      const valueA = isNaN(+propertyA) ? propertyA : +propertyA;
      const valueB = isNaN(+propertyB) ? propertyB : +propertyB;

      return (
          (valueA < valueB ? -1 : 1) *
          (this.sort.direction === 'asc' ? 1 : -1));
    });
  }
}
