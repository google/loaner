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

import {Component} from '@angular/core';
import {ComponentFixture, TestBed} from '@angular/core/testing';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {RouterTestingModule} from '@angular/router/testing';

import {DEVICE, ResumeLoanMock} from '../../../testing/mocks';
import {ResumeLoan} from '../../resume_loan';

import {LoanActionsCardModule} from './index';

const PENDING_DEVICE = {...DEVICE};
PENDING_DEVICE.pendingReturn = true;

@Component({
  template: `
  <loaner-loan-actions-card [device]="device">
    <loan-button resumeButton
                 (done)="onLoanResumed()"></loan-button>
  </loaner-loan-actions-card>`,
})
class ResumeButtonComponent {
  device = PENDING_DEVICE;
  onLoanResumed() {}
}

describe('LoanActionsCardComponent ResumeLoanButton', () => {
  let app: ResumeButtonComponent;
  let fixture: ComponentFixture<ResumeButtonComponent>;
  let compiled: HTMLElement;

  beforeEach(() => {
    TestBed
        .configureTestingModule({
          declarations: [
            ResumeButtonComponent,
          ],
          imports: [
            BrowserAnimationsModule,
            LoanActionsCardModule,
            RouterTestingModule,
          ],
          providers: [
            {provide: ResumeLoan, useClass: ResumeLoanMock},
          ],
        })
        .compileComponents();

    fixture = TestBed.createComponent(ResumeButtonComponent);
    app = fixture.debugElement.componentInstance;
    fixture.detectChanges();
    compiled = fixture.debugElement.nativeElement;
  });

  it('renders resume loan button.', () => {
    const buttons = compiled.querySelectorAll('button');
    expect(buttons).toBeDefined();
    expect(buttons.length).toBe(1);
    expect(buttons[0].textContent).toContain('Resume Loan');
  });

  it('calls onLoanResumed function after is clicked.', () => {
    spyOn(app, 'onLoanResumed');
    const button = compiled.querySelector('button');

    button!.dispatchEvent(new Event('click'));
    expect(app.onLoanResumed).toHaveBeenCalled();
  });
});
