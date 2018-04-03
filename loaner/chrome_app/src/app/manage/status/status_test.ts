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

import {HttpClient} from '@angular/common/http';
import {HttpClientTestingModule} from '@angular/common/http/testing';
import {ComponentFixture, TestBed} from '@angular/core/testing';
import {MatDialogRef} from '@angular/material';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {RouterTestingModule} from '@angular/router/testing';
import {of} from 'rxjs';
import * as moment from 'moment';

import {Damaged} from '../../../../../shared/components/damaged';
import {Extend} from '../../../../../shared/components/extend';
import {GuestMode} from '../../../../../shared/components/guest';
import {LoaderModule} from '../../../../../shared/components/loader';
import {GreetingsCardModule} from '../../../../../shared/components/loan_management/greetings_card';
import {LoanActionsCardModule} from '../../../../../shared/components/loan_management/loan_actions_card';
import {ResumeLoan} from '../../../../../shared/components/resume_loan';
import {FocusModule} from '../../../../../shared/directives/focus/index';
import {APIService} from '../../config';
import {Background} from '../../shared/background_service';
import {FailureModule} from '../../shared/failure';
import {Loan} from '../../shared/loan';
import {Storage} from '../../shared/storage/storage';

import {StatusComponent} from './index';
import {MaterialModule} from './material_module';
import {StatusService, StatusServiceMock} from './status_service';

/** Mock material DialogRef. */
class MatDialogRefMock {}

describe('StatusComponent', () => {
  let app: StatusComponent;
  let fixture: ComponentFixture<StatusComponent>;
  let loan: Loan;

  // Mock response of loan info
  const testLoanInfo: LoanResponse = {
    due_date: moment().toDate(),
    max_extend_date: moment().add(1, 'w').toDate(),
    given_name: 'John',
    guest_enabled: false,
    guest_permitted: true,
  };

  // Mock response of device info
  const testDeviceInfo: DeviceInfoResponse = {
    due_date: moment().toDate(),
    max_extend_date: moment().add(1, 'w').toDate(),
    guest_enabled: false,
    guest_permitted: true,
  };

  beforeEach(() => {
    TestBed
        .configureTestingModule({
          declarations: [StatusComponent],
          imports: [
            BrowserAnimationsModule,
            FailureModule,
            FocusModule,
            GreetingsCardModule,
            HttpClientTestingModule,
            LoaderModule,
            MaterialModule,
            RouterTestingModule,
            LoanActionsCardModule,
          ],
          providers: [
            APIService,
            Damaged,
            HttpClient,
            Extend,
            GuestMode,
            Loan,
            ResumeLoan,
            Storage,
            {
              provide: MatDialogRef,
              useClass: MatDialogRefMock,
            },
            {
              provide: StatusService,
              useClass: StatusServiceMock,
            },
          ],
        })
        .compileComponents();
  });

  beforeEach(() => {
    loan = TestBed.get(Loan);
    fixture = TestBed.createComponent(StatusComponent);
    app = fixture.debugElement.componentInstance;
    app.ready();
    fixture.detectChanges();
  });

  it('renders the page as loading', () => {
    app.waiting();
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelector('loaner-loader')).toBeTruthy();
  });

  it('loads the loan information initially', () => {
    spyOn(loan, 'getLoan').and.returnValue(of(testLoanInfo));
    spyOn(loan, 'getDevice').and.returnValue(of(testDeviceInfo));
    app.setLoanInfo(false);
    fixture.detectChanges();
    expect(app.dueDate).toEqual(testDeviceInfo.due_date);
    expect(app.maxExtendDate).toEqual(testDeviceInfo.max_extend_date);
    expect(app.guestAllowed).toEqual(testDeviceInfo.guest_permitted);
    expect(app.guestEnabled).toEqual(testDeviceInfo.guest_enabled);
  });

  it('renders content on the page', () => {
    app.dueDate = new Date(2018, 1, 1);
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent)
        .toContain('Please return your loaner by:');
  });

  it('allows the loan to be extended', () => {
    app.dueDate = new Date(2017, 2, 27, 0, 0, 0, 0);
    app.maxExtendDate = new Date(2017, 3, 1, 0, 0, 0);
    expect(app.canExtend()).toBeTruthy();
  });

  it('doesn\'t allow the loan to be extended', () => {
    app.dueDate = new Date(2017, 3, 3, 0, 0, 0, 0);
    app.maxExtendDate = new Date(2017, 3, 1, 0, 0, 0);
    expect(app.canExtend()).toBeFalsy();
  });
});
