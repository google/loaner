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

import {AfterViewInit, ChangeDetectorRef, Component, Input, OnDestroy, OnInit, ViewChild} from '@angular/core';
import {MatSort} from '@angular/material/sort';
import {MatTableDataSource} from '@angular/material/table';
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
export class DeviceListTable implements AfterViewInit, OnDestroy, OnInit {
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

  @ViewChild(MatSort, {static: true}) sort!: MatSort;
  /** Token needed on backend in order to return more results. */
  pageToken?: string;
  /** Backend response if there is more results to be retrieved. */
  hasMoreResults = false;
  /** Controls the state if is a refresh or request for more results. */
  gettingMoreData = false;
  /** Controls how many results it will get from backend. */
  pageSize = 25;
  /** Query filter to send to backend to get more results. */
  filters: DeviceApiParams = {};


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

    merge(intervalObservable, this.sort.sortChange)
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

  getMoreResults() {
    this.gettingMoreData = true;
    this.getDeviceList();
    this.pageSize += 25;
  }

  private getDeviceList() {
    if (this.gettingMoreData) {
      this.filters = this.setupShelfFilters({page_token: this.pageToken});
    } else {
      this.filters = this.setupShelfFilters({page_size: this.pageSize});
    }

    const sort = this.sort.active;
    const sortDirection = this.sort.direction || 'asc';

    this.deviceService.list(this.filters, sort, sortDirection)
        .subscribe(listResponse => {
          if (this.gettingMoreData) {
            this.dataSource.data =
                this.dataSource.data.concat(listResponse.devices);
          } else {
            this.dataSource.data = listResponse.devices;
          }
          this.gettingMoreData = false;
          this.hasMoreResults = listResponse.has_additional_results;
          this.pageToken = listResponse.page_token;
          // We need to manually call change detection here because of
          // https://github.com/angular/angular/issues/14748
          this.changeDetector.detectChanges();
        });
  }
}
