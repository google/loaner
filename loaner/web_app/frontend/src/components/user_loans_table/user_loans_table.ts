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

import {ChangeDetectorRef, Component, OnInit, ViewChild} from '@angular/core';

import {UserLoansData} from './user_loans_data';
import {UserLoansDataSource} from './user_loans_data_source';

/**
 * Implements the mat-table component. Implementation details:
 * https://material.angular.io/components/table/overview
 */
@Component({
  preserveWhitespaces: true,
  selector: 'loaner-user-loans-table',
  styleUrls: ['user_loans_table.scss'],
  templateUrl: 'user_loans_table.html',
})
export class UserLoansTable implements OnInit {
  /** Columns that should be rendered on the frontend table */
  displayedColumns = ['identifier', 'assignedOnDate', 'lastUpdate'];
  /** Type of data source that will be used on this implementation. */
  dataSource: UserLoansDataSource|null;

  constructor(
      private userLoansData: UserLoansData,
      private changeDetectorReference: ChangeDetectorRef) {}

  ngOnInit() {
    this.dataSource = new UserLoansDataSource(this.userLoansData);
  }

  /**
   * This is needed due to a bug on the mat-table component that does not
   * auto-detect the change cycle after the data source is rendered.
   */
  ngAfterViewChecked() {
    this.changeDetectorReference.detectChanges();
  }
}
