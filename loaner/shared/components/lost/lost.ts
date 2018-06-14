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

/** Return message for lost devices. */
const LOST_RETURN_MESSAGE =
   `Thank you for reporting the device as lost. If you need
please grab another one from the device.
Take care and have a great day!`;

/** Creates the actual dialog for the lost flow. */
@Injectable()
export class Lost {
  private dialogRef!: MatDialogRef<LostDialogComponent>;
  private lostComponent!: LostDialogComponent;

  constructor(private readonly dialog: MatDialog) {}

  get onLost() {
    return this.lostComponent.onLost;
  }

  openDialog() {
    this.dialogRef = this.dialog.open(LostDialogComponent);
    this.lostComponent = this.dialogRef.componentInstance;
  }

  finished() {
    if (this.lostComponent) {
      this.lostComponent.toBeSubmitted = false;
      this.lostComponent.loading = false;
    }
  }

  close() {
    this.dialogRef.close();
  }
}

/**
 * References the content to go into the lost dialog.
 * Also handles the dialog closing.
 */
@Component({
  host: {
    'class': 'mat-typography',
  },
  selector: 'lost',
  styleUrls: ['./lost.scss'],
  templateUrl: './lost.ng.html',
})
export class LostDialogComponent extends LoaderView {
  toBeSubmitted = true;
  lostReturnMessage = LOST_RETURN_MESSAGE;
  onLost = new Subject<boolean>();


  constructor(public dialogRef: MatDialogRef<LostDialogComponent>) {
    super(false);
  }

  closeDialog() {
    this.dialogRef.close();
  }

  /** Feeds the onLost Subject. */
  reportLost() {
    this.loading = true;
    this.onLost.next(true);
  }
}
