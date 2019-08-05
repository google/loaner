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

import {AfterViewInit, ChangeDetectorRef, Component, Input, OnDestroy, ViewChild} from '@angular/core';
import {MatSort} from '@angular/material/sort';
import {MatTableDataSource} from '@angular/material/table';
import {interval, merge, NEVER, Subject} from 'rxjs';
import {startWith, switchMap, takeUntil} from 'rxjs/operators';

import {Shelf, ShelfApiParams} from '../../models/shelf';
import {ShelfService} from '../../services/shelf';

/**
 * Implements the mat-table component. Implementation details:
 * https://material.angular.io/components/table/overview
 */
@Component({
  preserveWhitespaces: true,
  selector: 'loaner-shelf-list-table',
  styleUrls: ['shelf_list_table.scss'],
  templateUrl: 'shelf_list_table.ng.html',
})
export class ShelfListTable implements AfterViewInit, OnDestroy {
  /** Title of the table to be displayed. */
  @Input() cardTitle = 'Shelf List';

  /** Observable that iterates once the component is about to be destroyed. */
  private onDestroy = new Subject<void>();
  /** Columns that should be rendered on the frontend table */
  displayedColumns = [
    'id',
    'capacity',
    'last_audit_time',
    'last_audit_by',
    'icons',
  ];
  /** Type of data source that will be used on this implementation. */
  dataSource = new MatTableDataSource<Shelf>();
  /** Total number of shelves returned from the back end */
  totalResults = 0;
  /** Sort object */
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
  filters: ShelfApiParams = {};
  /* When true, pauseLoading will prevent auto refresh on the table. */
  pauseLoading = false;

  constructor(
      private readonly changeDetector: ChangeDetectorRef,
      private readonly shelfService: ShelfService) {}

  ngAfterViewInit() {
    this.getShelves();
  }

  getMoreResults() {
    this.gettingMoreData = true;
    this.getShelves();
    this.pageSize += 25;
  }

  ngOnDestroy() {
    this.dataSource.data = [];
    this.onDestroy.next();
  }

  private getShelves() {
    const intervalObservable = interval(60000).pipe(startWith(0));
    merge(intervalObservable, this.sort.sortChange)
        .pipe(
            takeUntil(this.onDestroy),
            switchMap(() => {
              if (this.pauseLoading) return NEVER;

              if (this.gettingMoreData) {
                this.filters = {
                  page_token: this.pageToken,
                };
              } else {
                this.filters = {page_size: this.pageSize};
              }

              const sort = this.sort.active || 'id';
              const sortDirection = this.sort.direction || 'asc';
              return this.shelfService.list(this.filters, sort, sortDirection);
            }),
            )
        .subscribe(listReponse => {
          if (this.gettingMoreData) {
            this.dataSource.data =
                this.dataSource.data.concat(listReponse.shelves);
          } else {
            this.dataSource.data = listReponse.shelves;
          }
          this.gettingMoreData = false;
          this.hasMoreResults = listReponse.has_additional_results;
          this.pageToken = listReponse.page_token;
          // We need to manually call change detection here because of
          // https://github.com/angular/angular/issues/14748
          this.changeDetector.detectChanges();
        });
  }
}
