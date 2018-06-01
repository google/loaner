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

import {Component, ElementRef, Input, OnInit, ViewChild} from '@angular/core';
import {MatSort, MatTableDataSource} from '@angular/material';
import {ActivatedRoute} from '@angular/router';
import {fromEvent, interval, NEVER, Observable, Subject} from 'rxjs';
import {debounceTime, distinctUntilChanged, startWith, takeUntil, tap} from 'rxjs/operators';

import {Damaged} from '../../../../../shared/components/damaged';
import {Extend} from '../../../../../shared/components/extend';
import {GuestMode} from '../../../../../shared/components/guest';
import {Lost} from '../../../../../shared/components/lost';
import {Device, DeviceApiParams} from '../../models/device';
import {Shelf} from '../../models/shelf';
import {DeviceService} from '../../services/device';
import {Actions} from '../device_action_box';

/**
 * Implements the mat-table component. Implementation details:
 * https://material.angular.io/components/table/overview
 */
@Component({
  preserveWhitespaces: true,
  selector: 'loaner-device-list-table',
  styleUrls: ['device_list_table.scss'],
  templateUrl: 'device_list_table.html',

})
export class DeviceListTable implements OnInit {
  /** Title of the table to be displayed. */
  @Input() cardTitle = 'Device List';
  /** If whether the action buttons taken on each row should be displayed. */
  @Input() showButtons = true;
  /** If the status column should be displayed on the data table. */
  @Input() showStatus = true;
  /** The shelf that is being used to filter devices. */
  @Input() shelf: Shelf;

  /** Observable that iterates once the component is about to be destroyed. */
  private onDestroy = new Subject<void>();

  /** Columns that should be rendered on the frontend table */
  displayedColumns: string[];

  /** Type of data source that will be used on this implementation. */
  dataSource = new MatTableDataSource<Device>();

  /** Current action that will be used in the device-action-box if rendered. */
  currentAction: string;

  /* When true, pauseLoading will prevent auto refresh on the table. */
  pauseLoading = false;

  @ViewChild(MatSort) sort: MatSort;

  constructor(
      private readonly damagedService: Damaged,
      private readonly lostService: Lost,
      private readonly extendService: Extend,
      private readonly deviceService: DeviceService,
      private readonly route: ActivatedRoute,
      private readonly guestModeService: GuestMode,
  ) {}

  setDisplayColumns() {
    this.displayedColumns = [
      'identifier',
      'assignedUser',
      'dueDate',
      'deviceModel',
    ];

    if (this.showStatus) {
      this.displayedColumns = [...this.displayedColumns, 'status'];
    }

    if (this.showButtons) {
      this.displayedColumns = [...this.displayedColumns, 'icons'];
    }
  }

  ngOnInit() {
    this.setDisplayColumns();
    this.dataSource.sort = this.sort;

    interval(60000)  // 1 minute.
        .pipe(
            startWith(0),
            takeUntil(this.onDestroy),
            tap(() => {
              if (this.pauseLoading) return NEVER;

              let filters: DeviceApiParams = {};
              if (this.shelf) {
                filters = {
                  shelf: {
                    shelf_request: {
                      location: this.shelf.shelfRequest.location,
                      urlsafe_key: this.shelf.shelfRequest.urlsafe_key
                    }
                  }
                };
              }

              return this.refresh(filters);
            }),
            )
        .subscribe();

    this.route.params.subscribe((params) => {
      this.currentAction = '';
      for (const key in Actions) {
        if (params.action === Actions[key]) {
          this.currentAction = Actions[key];
        }
      }
    });
  }

  ngOnDestroy() {
    this.dataSource.data = [];
    this.onDestroy.next();
  }

  /** Callback that's called once the device-action-box emits a device event. */
  takeActionOnDevice(device: Device) {
    let action: Observable<void>;
    switch (this.currentAction) {
      case Actions.ENROLL:
        action = this.deviceService.enroll(device);
        break;
      case Actions.UNENROLL:
        action = this.deviceService.unenroll(device);
        break;
      default:
        throw new Error('Device action not recognized.');
    }
    action.pipe(tap(() => this.refresh())).subscribe();
  }

  private refresh(filters: DeviceApiParams = {}) {
    return this.deviceService.list(filters).subscribe(response => {
      this.dataSource.data = response.devices;
    });
  }
}
