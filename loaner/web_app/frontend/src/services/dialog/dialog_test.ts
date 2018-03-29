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

import {fakeAsync, flushMicrotasks, TestBed} from '@angular/core/testing';
import {MatDialog} from '@angular/material';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {RouterTestingModule} from '@angular/router/testing';

import {Dialog, DialogsModule} from '.';

class MatDialogMock {
  open() {
    return;
  }
}

describe('DialogComponent', () => {
  let dialog: Dialog;
  let matDialogMock: MatDialog;

  beforeEach(fakeAsync(() => {
    TestBed
        .configureTestingModule({
          imports: [
            RouterTestingModule,
            DialogsModule,
            BrowserAnimationsModule,
          ],
          providers: [
            {provide: MatDialog, useClass: MatDialogMock},
          ],
        })
        .compileComponents();

    flushMicrotasks();

    dialog = TestBed.get(Dialog);
    matDialogMock = TestBed.get(MatDialog);
  }));

  it('should inject the Dialog', () => {
    expect(dialog).toBeDefined();
  });

});
