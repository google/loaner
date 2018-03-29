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

import {Device} from '../../models/device';

import {UserLoansData} from './user_loans_data';


/**
 * UserLoan data source to provide what data should be rendered in the Angular
 * Material's mat-table.
 * https://material.angular.io/components/table/overview
 */
export class UserLoansDataSource extends DataSource<{}> {
  constructor(private readonly userLoansData: UserLoansData) {
    super();
  }

  /**
   * Connect function called by the table to retrieve one stream containing the
   * data to render.
   */
  connect(): Observable<Device[]> {
    const displayDataChanges = [
      this.userLoansData.dataChange,
    ];

    return merge(...displayDataChanges);
  }

  disconnect() {
    // No-op. Must be implemented by cdk's DataSource.
  }
}
