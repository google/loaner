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

import {Injectable} from '@angular/core';
import {Observable} from 'rxjs';
import {tap} from 'rxjs/operators';

import * as bootstrap from '../models/bootstrap';

import {ApiService} from './api';

@Injectable()
/** Class to connect to the backend's Bootstrap Service API methods. */
export class BootstrapService extends ApiService {
  /** Implements ApiService's apiEndpoint requirement. */
  apiEndpoint = 'bootstrap';

  run(tasks?: bootstrap.Task[]): Observable<bootstrap.Status> {
    return this.post<bootstrap.Status>('run', tasks).pipe(tap(() => {
      this.snackBar.open(`Setup requested.`);
    }));
  }

  /**
   * Retrieves current Bootstrap status from the backend.
   */
  getStatus(): Observable<bootstrap.Status> {
    return this.get<bootstrap.Status>('get_status')
        .pipe(tap((status: bootstrap.Status) => {
          if (status.completed) {
            this.snackBar.open(`Bootstrap completed successfully.`);
          } else if (
              status.tasks && status.tasks.every((task) => !!task.timestamp) &&
              status.tasks.some((task) => !task.success)) {
            this.snackBar.open(`One or more tasks failed.`);
          }
        }));
  }
}
