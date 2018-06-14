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

/** Creates the actual dialog for the guest flow. */
@Injectable()
export class GuestMode {
  private component!: GuestComponentDialog;
  private dialogRef!: MatDialogRef<GuestComponentDialog>;

  constructor(private readonly dialog: MatDialog) {}

  get onGuestModeEnabled() {
    return this.component.onGuestModeEnabled;
  }

  openDialog() {
    this.dialogRef = this.dialog.open(GuestComponentDialog);
    this.component = this.dialogRef.componentInstance;
  }

  finished() {
    if (this.component) {
      this.component.loading = false;
    }
  }

  close() {
    this.dialogRef.close();
  }
}
/**
 * Dialog that appears when enable guest mode.
 */
@Component({
  host: {
    'class': 'mat-typography',
  },
  selector: 'guest',
  styleUrls: ['./guest.scss'],
  templateUrl: './guest.ng.html',
})
export class GuestComponentDialog extends LoaderView {
  onGuestModeEnabled = new Subject<boolean>();

  constructor(public dialogRef: MatDialogRef<GuestComponentDialog>) {
    super(true);
  }

  ngOnInit() {
    this.enableGuestMode();
  }

  enableGuestMode() {
    this.loading = true;
    this.onGuestModeEnabled.next(true);
    this.onGuestModeEnabled.complete();
  }

  closeDialog() {
    this.dialogRef.close();
  }
}
