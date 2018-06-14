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

/** Return message for damaged devices. */
const DAMAGED_RETURN_MESSAGE =
   `Thank you for reporting the device as damaged. If you need to
get a new loaner device, you can return this one and grab another
device from the shelf. Otherwise, you can keep using this device
and when you are finished with it, please return it. Take care and
have a great day!`;

/** Creates the actual dialog for the damaged flow. */
@Injectable()
export class Damaged {
  private dialogRef!: MatDialogRef<DamagedDialogComponent>;
  private damagedComponent!: DamagedDialogComponent;

  constructor(private readonly dialog: MatDialog) {}

  get onDamaged() {
    return this.damagedComponent.onDamaged;
  }

  openDialog() {
    this.dialogRef = this.dialog.open(DamagedDialogComponent);
    this.damagedComponent = this.dialogRef.componentInstance;
  }

  finished() {
    if (this.damagedComponent) {
      this.damagedComponent.toBeSubmitted = false;
      this.damagedComponent.loading = false;
    }
  }

  close() {
    this.dialogRef.close();
  }
}

/**
 * References the content to go into the damaged dialog.
 * Also handles the dialog closing.
 */
@Component({
  host: {
    'class': 'mat-typography',
  },
  selector: 'damaged',
  styleUrls: ['./damaged.scss'],
  templateUrl: './damaged.ng.html',
})
export class DamagedDialogComponent extends LoaderView {
  toBeSubmitted = true;
  damagedReason!: string;
  damagedReturnMessage = DAMAGED_RETURN_MESSAGE;
  onDamaged = new Subject<string>();


  constructor(public dialogRef: MatDialogRef<DamagedDialogComponent>) {
    super(false);
  }

  closeDialog() {
    this.dialogRef.close();
  }

  /** Reports the device as damaged to the API with a reason if given. */
  reportDamaged() {
    this.loading = true;
    this.onDamaged.next(this.damagedReason);
  }
}
