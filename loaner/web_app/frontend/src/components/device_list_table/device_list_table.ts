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

import {ChangeDetectorRef, Component, ElementRef, Input, OnInit, ViewChild} from '@angular/core';
import {MatSort} from '@angular/material';
import {ActivatedRoute} from '@angular/router';
import {fromEvent, interval, NEVER, Observable, Subject} from 'rxjs';
import {debounceTime, distinctUntilChanged, finalize, startWith, switchMap, takeUntil} from 'rxjs/operators';

import {Damaged} from '../../../../../shared/components/damaged';
import {Extend} from '../../../../../shared/components/extend';
import {GuestMode} from '../../../../../shared/components/guest';
import {LoaderView} from '../../../../../shared/components/loader';
import {Lost} from '../../../../../shared/components/lost';
import {Device} from '../../models/device';
import {Shelf} from '../../models/shelf';
import {DeviceService} from '../../services/device';
import {Actions} from '../device_action_box';

import {DeviceData} from './device_data';
import {DeviceDataSource} from './device_data_source';

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
export class DeviceListTable extends LoaderView implements OnInit {
  /** Title of the table to be displayed. */
  @Input() cardTitle = 'Default Text';
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
  dataSource: DeviceDataSource|null;

  /** Current action that will be used in the device-action-box if rendered. */
  currentAction: string;

  /* When true, pauseLoading will prevent auto refresh on the table. */
  pauseLoading = false;

  @ViewChild(MatSort) sort: MatSort;
  @ViewChild('filter') filter: ElementRef;

  constructor(
      private readonly damagedService: Damaged,
      private readonly lostService: Lost,
      private readonly extendService: Extend,
      private readonly deviceData: DeviceData,
      private readonly deviceService: DeviceService,
      private readonly changeDetectorReference: ChangeDetectorRef,
      private readonly route: ActivatedRoute,
      private readonly guestModeService: GuestMode,
  ) {
    super(false);
  }

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
    interval(5000)
        .pipe(startWith(0), takeUntil(this.onDestroy), switchMap(() => {
                if (this.pauseLoading) return NEVER;
                this.loading = true;
                if (this.shelf) {
                  return this.deviceData.refresh(
                      {shelf: {location: this.shelf.location}});
                } else {
                  return this.deviceData.refresh();
                }
              }))
        .subscribe(() => {
          this.loading = false;
        });

    this.route.params.subscribe((params) => {
      this.currentAction = '';
      for (const key in Actions) {
        if (params.action === Actions[key]) {
          this.currentAction = Actions[key];
        }
      }
    });

    this.dataSource = new DeviceDataSource(this.deviceData, this.sort);

    fromEvent(this.filter.nativeElement, 'keyup')
        .pipe(debounceTime(150), distinctUntilChanged())
        .subscribe(() => {
          if (!this.dataSource) return;
          this.dataSource.filter = this.filter.nativeElement.value;
        });
  }

  ngOnDestroy() {
    this.deviceData.clearData();
    this.onDestroy.next();
  }

  /**
   * This is needed due to a bug on the mat-table component that does not
   * auto-detect the change cycle after the data source is rendered.
   */
  ngAfterViewChecked() {
    this.changeDetectorReference.detectChanges();
  }

  /** Callback that's called once the device-action-box emits a device event. */
  takeActionOnDevice(device: Device) {
    this.waiting();
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
    action
        .pipe(
            switchMap(() => this.deviceData.refresh()),
            finalize(() => {
              this.ready();
            }),
            )
        .subscribe();
  }

  /**
   * Toggle guest mode for the device
   * @param device The device we are enabling guest on.
   */
  enableGuestMode(device: Device) {
    this.guestModeService.openDialog();
    this.guestModeService.onGuestModeEnabled
        .pipe(switchMap(
            () => this.deviceService.enableGuestMode(device.serialNumber)))
        .subscribe(
            () => {
              this.guestModeService.finished();
            },
            () => {
              this.guestModeService.close();
            });
  }

  /**
   * Calls deviceService API for extending a device and defines new due date.
   *
   * @param device The device we're extending.
   */
  extendDevice(device: Device) {
    let temporaryNewDate: string;
    this.extendService.openDialog(device.dueDate, device.maxExtendDate);
    this.extendService.onExtended
        .pipe(switchMap(newDate => {
          temporaryNewDate = newDate;
          return this.deviceService.extend(newDate, device.serialNumber);
        }))
        .subscribe(
            () => {
              this.extendService.finished(new Date(temporaryNewDate));
            },
            () => {
              this.extendService.close();
            });
  }

  /**
   * Calls the deviceService to return a device.
   *
   * @param device The device to take action on.
   */
  onReturned(device: Device) {
    this.deviceService.returnDevice(device.serialNumber).subscribe(() => {
      device.pendingReturn = true;
    });
  }

  /**
   * Calls the deviceService to mark a device as damaged.
   *
   * @param device The device to take action on.
   */
  onDamaged(device: Device) {
    this.damagedService.openDialog();
    this.damagedService.onDamaged
        .pipe(switchMap(
            damagedReason => this.deviceService.markAsDamaged(
                device.serialNumber, damagedReason)))
        .subscribe(
            () => {
              this.damagedService.finished();
            },
            () => {
              this.damagedService.close();
            });
  }

  /**
   * Calls the deviceService to mark a device as lost.
   *
   * @param device The device to take action on.
   */
  onLost(device: Device) {
    this.lostService.openDialog();
    this.lostService.onLost
        .pipe(
            switchMap(() => this.deviceService.markAsLost(device.serialNumber)))
        .subscribe(
            () => {
              this.lostService.finished();
            },
            () => {
              this.lostService.close();
            });
  }
}
