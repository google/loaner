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

import {ComponentFixture, TestBed} from '@angular/core/testing';
import {MatDialogModule, MatDialogRef} from '@angular/material/dialog';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';

import {ReturnDialog, ReturnDialogModule} from './index';

/** Mock material DialogRef. */
class MatDialogRefMock {}

describe('ReturnDialog', () => {
  let component: ReturnDialog;
  let fixture: ComponentFixture<ReturnDialog>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [
        ReturnDialogModule,
      ],
      providers: [{
        provide: MatDialogRef,
        useClass: MatDialogRefMock,
      }],
    });

    fixture = TestBed.createComponent(ReturnDialog);
    component = fixture.debugElement.componentInstance;
    fixture.detectChanges();
  });

  it('should create dialog component', () => {
    expect(component).toBeTruthy();
  });

  it('should show the correct title', () => {
    const compiled = fixture.debugElement.nativeElement;
    fixture.detectChanges();
    expect(compiled.querySelector('#title').textContent)
        .toContain('Are you sure you want to return this loaner?');
  });

  it('should show the correct body', () => {
    const compiled = fixture.debugElement.nativeElement;
    fixture.detectChanges();
    expect(compiled.querySelector('#content').textContent)
        .toContain(
            'Clicking the return button below will mark this loaner as returned.');
  });

  it('should render the Return button', () => {
    const compiled = fixture.debugElement.nativeElement;
    fixture.detectChanges();
    expect(compiled.querySelectorAll('.action-button')[0].textContent)
        .toContain('Return');
  });

  it('should render the Close button', () => {
    const compiled = fixture.debugElement.nativeElement;
    fixture.detectChanges();
    expect(compiled.querySelectorAll('.action-button')[1].textContent)
        .toContain('Close');
  });
});
