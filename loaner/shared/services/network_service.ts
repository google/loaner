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
import {MatSnackBar, MatSnackBarConfig} from '@angular/material';
import {BehaviorSubject, fromEvent} from 'rxjs';

@Injectable()
export class NetworkService {
  internetStatus = new BehaviorSubject<boolean>(true);

  constructor(private readonly snackBar: MatSnackBar) {
    fromEvent(window, 'online')
        .subscribe(() => this.internetStatusUpdater(true));
    fromEvent(window, 'offline')
        .subscribe(() => this.internetStatusUpdater(false));
  }

  /**
   * Updates the internetStatus variable and also creates a snackbar on services
   * when the connection is lost.
   * @param status Represents the current status of the internet connection.
   */
  internetStatusUpdater(status: boolean) {
    if (!status) {
      const message = 'No internet connection.';
      const action = '';
      const config: MatSnackBarConfig = {
        horizontalPosition: 'center',
      };
      this.snackBar.open(message, action, config);
    } else {
      this.snackBar.dismiss();
    }
    this.internetStatus.next(status);
  }
}
