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
import {MatDialog, MatDialogRef} from '@angular/material';
import {Observable} from 'rxjs';
import {ConfirmDialog} from './confirm_dialog';

@Injectable()
export class Dialog {

  constructor(private dialog: MatDialog) {}

  /**
   * Class to create dialogs using matDialog from angular material
   * @param title Dialog title
   * @param message Dialog message
   */
  confirm(title: string, message: string): Observable<boolean> {
    let dialogRef: MatDialogRef<ConfirmDialog>;
    dialogRef = this.dialog.open(ConfirmDialog);
    dialogRef.componentInstance.title = title;
    dialogRef.componentInstance.message = message;
    return dialogRef.afterClosed();
  }
}
