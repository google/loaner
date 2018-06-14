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

/** Service that communicates with the resume loan dialog. */
@Injectable()
export class ResumeLoan {
  private component!: ResumeLoanDialog;
  private dialogRef!: MatDialogRef<ResumeLoanDialog>;

  constructor(private readonly dialog: MatDialog) {}

  get onLoanResumed() {
    return this.component.onLoanResumed;
  }

  openDialog() {
    this.dialogRef = this.dialog.open(ResumeLoanDialog);
    this.component = this.dialogRef.componentInstance;
  }

  finished() {
    if (this.component) {
      this.component.loading = false;
    }
  }
}

/**
 * Resume loan dialog for the successful resuming of a loan.
 */
@Component({
  host: {
    'class': 'mat-typography',
  },
  selector: 'resume-loan',
  styleUrls: ['./resume_loan.scss'],
  templateUrl: './resume_loan.ng.html',
})
export class ResumeLoanDialog extends LoaderView {
  onLoanResumed = new Subject<boolean>();

  constructor(public dialogRef: MatDialogRef<ResumeLoanDialog>) {
    super(true);
  }

  ngOnInit() {
    this.resumeLoan();
  }

  resumeLoan() {
    this.loading = true;
    this.onLoanResumed.next(true);
  }

  closeDialog() {
    this.dialogRef.close();
  }
}
