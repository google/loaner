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

import {ChangeDetectorRef, Component, ElementRef, Input, OnDestroy, OnInit, ViewChild} from '@angular/core';
import {MatSort} from '@angular/material';
import {fromEvent, interval, NEVER, Observable, Subject} from 'rxjs';
import {debounceTime, distinctUntilChanged, startWith, switchMap, takeUntil} from 'rxjs/operators';

import {LoaderView} from '../../../../../shared/components/loader';

import {ShelfData} from './shelf_data';
import {ShelfDataSource} from './shelf_data_source';

/**
 * Implements the mat-table component. Implementation details:
 * https://material.angular.io/components/table/overview
 */
@Component({
  preserveWhitespaces: true,
  selector: 'loaner-shelf-list-table',
  styleUrls: ['shelf_list_table.scss'],
  templateUrl: 'shelf_list_table.html',
})
export class ShelfListTable extends LoaderView implements OnInit, OnDestroy {
  /** Title of the table to be displayed. */
  @Input() cardTitle = 'Shelf List';

  /** Observable that iterates once the component is about to be destroyed. */
  private onDestroy = new Subject<void>();
  /** Columns that should be rendered on the frontend table */
  displayedColumns = [
    'name',
    'capacity',
    'lastAuditTime',
    'lastAuditBy',
    'icons',
  ];
  /** Type of data source that will be used on this implementation. */
  dataSource: ShelfDataSource|null;

  @ViewChild(MatSort) sort: MatSort;
  @ViewChild('filter') filter: ElementRef;

  loading = true;
  pauseLoading = false;

  constructor(
      private shelfData: ShelfData,
      private changeDetectorReference: ChangeDetectorRef) {
    super(true);
  }

  ngOnInit() {
    interval(5000)
        .pipe(startWith(0), takeUntil(this.onDestroy), switchMap(() => {
                if (this.pauseLoading) return NEVER;
                this.loading = true;
                return this.shelfData.refresh();
              }))
        .subscribe(() => {
          this.loading = false;
        });

    this.dataSource = new ShelfDataSource(this.shelfData, this.sort);

    fromEvent(this.filter.nativeElement, 'keyup')
        .pipe(debounceTime(150), distinctUntilChanged())
        .subscribe(() => {
          if (!this.dataSource) return;
          this.dataSource.filter = this.filter.nativeElement.value;
        });
  }

  ngOnDestroy() {
    this.onDestroy.next();
  }

  /**
   * This is needed due to a bug on the mat-table component that does not
   * auto-detect the change cycle after the data source is rendered.
   */
  ngAfterViewChecked() {
    this.changeDetectorReference.detectChanges();
  }
}
