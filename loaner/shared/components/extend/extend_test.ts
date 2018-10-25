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
import {MatDialogRef} from '@angular/material';
import * as moment from 'moment';

import {ExtendDialogComponent, ExtendModule} from './index';

/** Mock material DialogRef. */
class MatDialogRefMock {}

describe('ExtendDialogComponent', () => {
  let component: ExtendDialogComponent;
  let fixture: ComponentFixture<ExtendDialogComponent>;
  let compiled: HTMLElement;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [
        ExtendModule,
      ],
      providers: [{
        provide: MatDialogRef,
        useClass: MatDialogRefMock,
      }],
    });

    fixture = TestBed.createComponent(ExtendDialogComponent);
    component = fixture.debugElement.componentInstance;

    component.dueDate = new Date(2018, 1, 1);
    component.maxExtendDate = new Date(2018, 1, 2);
    component.ready();
    fixture.detectChanges();
    compiled = fixture.debugElement.nativeElement;
  });

  it('should create dialog component', () => {
    expect(component).toBeDefined();
  });

  it('should render the submit button', () => {
    expect(compiled.querySelector('#submit')!.textContent).toContain('Submit');
  });

  it('should render the cancel button', () => {
    expect(compiled.querySelector('#cancel')!.textContent).toContain('Cancel');
  });

  it('should show the correct title', () => {
    expect(compiled.querySelector('.mat-dialog-title')!.textContent)
        .toBe('Extend your loaner');
  });

  it('should successfully validate the date', () => {
    component.dueDate = new Date();
    component.newReturnDate = new Date();
    component.maxExtendDate = new Date();

    component.newReturnDate =
        moment(component.newReturnDate).add(11, 'days').toDate();
    component.maxExtendDate =
        moment(component.maxExtendDate).add(14, 'days').toDate();
    const formattedNewDueDate =
        moment(component.newReturnDate).format(`YYYY-MM-DD[T][00]:[00]:[00]`);

    expect(component.validateDate(formattedNewDueDate)).toBe(true);
  });

  it('should fail to validate the date', () => {
    component.dueDate = new Date();
    component.newReturnDate = new Date();
    component.maxExtendDate = new Date();

    component.newReturnDate =
        moment(component.newReturnDate).add(16, 'days').toDate();
    component.maxExtendDate =
        moment(component.maxExtendDate).add(14, 'days').toDate();
    const formattedNewDueDate =
        moment(component.newReturnDate).format(`YYYY-MM-DD[T][00]:[00]:[00]`);

    expect(component.validateDate(formattedNewDueDate)).toBe(false);
  });

  it('should show and hide the loader', () => {
    component.waiting();
    fixture.detectChanges();
    expect(compiled.querySelector('loader')).toBeDefined();
    component.ready();
    fixture.detectChanges();
    expect(compiled.querySelector('loader')).toBeFalsy();
  });

  it('should render the close button', () => {
    component.toBeSubmitted = false;
    component.ready();
    fixture.detectChanges();
    expect(compiled.querySelector('#close')!.textContent).toContain('Close');
  });

  it('uses loaner date adapter to display the date', () => {
    component.ready();
    fixture.whenStable().then(() => {
      const compiled = fixture.debugElement.nativeElement;
      expect(compiled.querySelector('input').value).toBe('February 2, 2018');
    });
  });
});
