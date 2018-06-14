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

/** Creates the actual dialog for the unenroll flow. */
@Injectable()
export class Unenroll {
  private dialogRef!: MatDialogRef<UnenrollDialogComponent>;
  private unenrollComponent!: UnenrollDialogComponent;

  constructor(private readonly dialog: MatDialog) {}

  get onUnenroll() {
    return this.unenrollComponent.onUnenroll;
  }

  openDialog(deviceId: string) {
    this.dialogRef = this.dialog.open(UnenrollDialogComponent);
    this.unenrollComponent = this.dialogRef.componentInstance;
    this.unenrollComponent.deviceId = deviceId;
  }

  finished() {
    if (this.unenrollComponent) {
      this.unenrollComponent.toBeSubmitted = false;
      this.unenrollComponent.loading = false;
    }
  }

  close() {
    this.dialogRef.close();
  }
}

/**
 * References the content to go into the unenroll dialog.
 * Also handles the dialog closing.
 */
@Component({
  host: {
    'class': 'mat-typography',
  },
  selector: 'unenroll',
  styleUrls: ['./unenroll.scss'],
  templateUrl: './unenroll.ng.html',
})
export class UnenrollDialogComponent extends LoaderView {
  toBeSubmitted = true;
  deviceId!: string;
  onUnenroll = new Subject<boolean>();


  constructor(public dialogRef: MatDialogRef<UnenrollDialogComponent>) {
    super(false);
  }

  closeDialog() {
    this.dialogRef.close();
  }

  /** Feeds the onUnenroll Subject. */
  unenroll() {
    this.loading = true;
    this.onUnenroll.next(true);
  }
}
