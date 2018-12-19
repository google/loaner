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

import {ChangeDetectorRef, Component, Input, OnInit, ViewChild} from '@angular/core';
import {MatPaginator, MatSort, MatTableDataSource} from '@angular/material';
import {interval, merge, NEVER, Subject} from 'rxjs';
import {startWith, takeUntil, tap} from 'rxjs/operators';

import {Device, DeviceApiParams} from '../../models/device';
import {Shelf} from '../../models/shelf';
import {DeviceService} from '../../services/device';

/**
 * Implements the mat-table component. Implementation details:
 * https://material.angular.io/components/table/overview
 */
@Component({
  preserveWhitespaces: true,
  selector: 'loaner-device-list-table',
  styleUrls: ['device_list_table.scss'],
  templateUrl: 'device_list_table.ng.html',

})
export class DeviceListTable implements OnInit {
  /** Title of the table to be displayed. */
  @Input() cardTitle = 'Device List';
  /** If whether the action buttons taken on each row should be displayed. */
  @Input() showButtons = true;
  /** If the status column should be displayed on the data table. */
  @Input() showStatus = true;
  /** The shelf that is being used to filter devices. */
  @Input() shelf!: Shelf;
  /** Columns that should be rendered on the frontend table. */
  @Input()
  displayedColumns = [
    'id',
    'assigned_user',
    'due_date',
    'device_model',
  ];
  /** Observable that iterates once the component is about to be destroyed. */
  private onDestroy = new Subject<void>();
  /** Type of data source that will be used on this implementation. */
  dataSource = new MatTableDataSource<Device>();
  /** Total number of shelves returned from the backend. */
  totalResults = 0;
  /* When true, pauseLoading will prevent auto refresh on the table. */
  pauseLoading = false;

  @ViewChild(MatSort) sort!: MatSort;
  @ViewChild(MatPaginator) paginator!: MatPaginator;

  constructor(
      private readonly changeDetector: ChangeDetectorRef,
      private readonly deviceService: DeviceService,
  ) {}

  setDisplayColumns() {
    if (this.showStatus) {
      this.displayedColumns = [...this.displayedColumns, 'status'];
    }

    if (this.showButtons) {
      this.displayedColumns = [...this.displayedColumns, 'icons'];
    }
  }

  ngOnInit() {
    this.setDisplayColumns();
  }

  ngAfterViewInit() {
    const intervalObservable = interval(60000).pipe(startWith(0));

    merge(intervalObservable, this.sort.sortChange, this.paginator.page)
        .pipe(takeUntil(this.onDestroy), tap(() => {
                if (!this.pauseLoading) {
                  this.getDeviceList();
                }
              }))
        .subscribe();
  }

  ngOnDestroy() {
    this.dataSource.data = [];
    this.onDestroy.next();
  }

  private setupShelfFilters(filters: DeviceApiParams) {
    if (this.shelf) {
      filters.shelf = {
        shelf_request: {
          location: this.shelf.shelfRequest.location,
          urlsafe_key: this.shelf.shelfRequest.urlsafe_key
        }
      };
    }
    return filters;
  }

  private getDeviceList() {
    let filters: DeviceApiParams = {
      page_number: this.paginator.pageIndex + 1,
      page_size: this.paginator.pageSize,
    };
    const sort = this.sort.active;
    const sortDirection = this.sort.direction || 'asc';

    filters = this.setupShelfFilters(filters);

    this.deviceService.list(filters, sort, sortDirection)
        .subscribe(response => {
          this.totalResults = response.totalResults;
          this.dataSource.data = response.devices;
          // We need to manually call change detection here because of
          // https://github.com/angular/angular/issues/14748
          this.changeDetector.detectChanges();
        });
  }
}
