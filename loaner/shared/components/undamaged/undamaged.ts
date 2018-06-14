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

import {Component, Injectable} from '@angular/core';
import {MatDialog, MatDialogRef} from '@angular/material';
import {Subject} from 'rxjs';

import {LoaderView} from '../loader';

/** Creates the actual dialog for the undamaged flow. */
@Injectable()
export class Undamaged {
  private dialogRef!: MatDialogRef<UndamagedDialogComponent>;
  private undamagedComponent!: UndamagedDialogComponent;

  constructor(private readonly dialog: MatDialog) {}

  get onUndamaged() {
    return this.undamagedComponent.onUndamaged;
  }

  openDialog(deviceId: string) {
    this.dialogRef = this.dialog.open(UndamagedDialogComponent);
    this.undamagedComponent = this.dialogRef.componentInstance;
    this.undamagedComponent.deviceId = deviceId;
  }

  finished() {
    if (this.undamagedComponent) {
      this.undamagedComponent.toBeSubmitted = false;
      this.undamagedComponent.loading = false;
    }
  }

  close() {
    this.dialogRef.close();
  }
}

/**
 * References the content to go into the undamaged dialog.
 * Also handles the dialog closing.
 */
@Component({
  host: {
    'class': 'mat-typography',
  },
  selector: 'undamaged',
  styleUrls: ['./undamaged.scss'],
  templateUrl: './undamaged.ng.html',
})
export class UndamagedDialogComponent extends LoaderView {
  toBeSubmitted = true;
  deviceId!: string;
  onUndamaged = new Subject<boolean>();


  constructor(public dialogRef: MatDialogRef<UndamagedDialogComponent>) {
    super(false);
  }

  closeDialog() {
    this.dialogRef.close();
  }

  /** Feeds the onUndamaged Subject. */
  undamaged() {
    this.loading = true;
    this.onUndamaged.next(true);
  }
}
