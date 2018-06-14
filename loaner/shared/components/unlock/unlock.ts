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

/** Creates the actual dialog for the unlock flow. */
@Injectable()
export class Unlock {
  private dialogRef!: MatDialogRef<UnlockDialogComponent>;
  private unlockComponent!: UnlockDialogComponent;

  constructor(private readonly dialog: MatDialog) {}

  get onUnlock() {
    return this.unlockComponent.onUnlock;
  }

  openDialog(deviceId: string) {
    this.dialogRef = this.dialog.open(UnlockDialogComponent);
    this.unlockComponent = this.dialogRef.componentInstance;
    this.unlockComponent.deviceId = deviceId;
  }

  finished() {
    if (this.unlockComponent) {
      this.unlockComponent.toBeSubmitted = false;
      this.unlockComponent.loading = false;
    }
  }

  close() {
    this.dialogRef.close();
  }
}

/**
 * References the content to go into the unlock dialog.
 * Also handles the dialog closing.
 */
@Component({
  host: {
    'class': 'mat-typography',
  },
  selector: 'unlock',
  styleUrls: ['./unlock.scss'],
  templateUrl: './unlock.ng.html',
})
export class UnlockDialogComponent extends LoaderView {
  toBeSubmitted = true;
  deviceId!: string;
  onUnlock = new Subject<boolean>();


  constructor(public dialogRef: MatDialogRef<UnlockDialogComponent>) {
    super(false);
  }

  closeDialog() {
    this.dialogRef.close();
  }

  /** Feeds the onUnlock Subject. */
  unlock() {
    this.loading = true;
    this.onUnlock.next(true);
  }
}
