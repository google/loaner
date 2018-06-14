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

import {Component, Injectable, OnInit} from '@angular/core';
import {MatDialog, MatDialogRef} from '@angular/material';
import * as moment from 'moment';
import {Subject} from 'rxjs';

import {LoaderView} from '../loader';

/** Creates the actual dialog for the extend flow. */
@Injectable()
export class Extend {
  private component!: ExtendDialogComponent;
  private dialogRef!: MatDialogRef<ExtendDialogComponent>;

  constructor(private readonly dialog: MatDialog) {}

  get onExtended() {
    return this.component.onExtended;
  }

  openDialog(dueDate: Date, maxExtendDate: Date) {
    this.dialogRef = this.dialog.open(ExtendDialogComponent);
    this.component = this.dialogRef.componentInstance;
    this.component.dueDate = dueDate;
    this.component.maxExtendDate = maxExtendDate;
  }

  finished(newDueDate: Date) {
    if (this.component) {
      this.component.dueDate = newDueDate;
      this.component.toBeSubmitted = false;
      this.component.loading = false;
    }
  }

  close() {
    this.dialogRef.close();
  }
}
/**
 * References the content to go into the extend dialog.
 * Also handles the dialog closing.
 */
@Component({
  host: {
    'class': 'mat-typography',
  },
  selector: 'extend',
  styleUrls: ['./extend.scss'],
  templateUrl: './extend.ng.html',
})
export class ExtendDialogComponent extends LoaderView implements OnInit {
  dueDate?: Date;
  maxExtendDate?: Date;
  newReturnDate?: Date;
  onExtended = new Subject<string>();
  toBeSubmitted = true;
  validDate = true;

  constructor(public dialogRef: MatDialogRef<ExtendDialogComponent>) {
    super(false);
  }

  ngOnInit() {
    this.setInitialExtendDate();
  }

  /** Gets the minimum return date. */
  getMinimumReturnDate(): Date {
    const today = moment().set({
      hour: 0,
      minute: 0,
      second: 0,
    });

    return moment(today).add(1, 'd').toDate();
  }

  /**
   * Set's the initial extend date by adding one additional date to the current
   * due date using MomentJS.
   */
  setInitialExtendDate() {
    if (this.dueDate == null) {
      console.error('The due date was never defined.');
    }
    if (this.maxExtendDate == null) {
      console.error('The max extend date was never defined.');
    }
    this.newReturnDate = moment(this.dueDate!).add(1, 'days').toDate();
  }

  /**
   * Checks the dates to see if the loan can be extended.
   * @param date The formatted new extension date.
   */
  validateDate(date: string): boolean {
    if (moment(date).isSame(this.dueDate!)) {
      return false;
    } else {
      return moment(date).diff(this.getMinimumReturnDate(), 'days') >= 0 &&
          moment(date).diff(this.maxExtendDate!, 'days') <= 0;
    }
  }

  /**
   * Prevents non 0-9 and / characters from being used in the date field.
   * @param event The DOM event to be tracked on key presses.
   */
  validateField(event: KeyboardEvent): boolean {
    const pattern = /[0-9\/]/;
    const inputCharacters = String.fromCharCode(event.charCode);

    if (!pattern.test(inputCharacters)) {
      return false;
    } else {
      return pattern.test(inputCharacters);
    }
  }

  /** Emits an new value on the onExtend if date is valid. */
  extendDate() {
    /** Updates the new return date to the proper API format. */
    const formattedNewDueDate =
        moment(this.newReturnDate!).format(`YYYY-MM-DD[T][00]:[00]:[00]`);

    if (this.validateDate(formattedNewDueDate)) {
      this.loading = true;
      this.newReturnDate = moment(formattedNewDueDate).toDate();
      this.onExtended.next(formattedNewDueDate);
    } else {
      this.validDate = false;
    }
  }

  closeDialog() {
    this.dialogRef.close();
  }
}
