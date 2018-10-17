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
import * as moment from 'moment';
import {of} from 'rxjs';

import {Damaged} from '../../../../../shared/components/damaged';
import {Extend} from '../../../../../shared/components/extend';
import {GuestMode} from '../../../../../shared/components/guest';
import {LoaderModule} from '../../../../../shared/components/loader';
import {GreetingsCardModule} from '../../../../../shared/components/loan_management/greetings_card';
import {LoanActionsCardModule} from '../../../../../shared/components/loan_management/loan_actions_card';
import {ResumeLoan} from '../../../../../shared/components/resume_loan';
import {ConfigService} from '../../../../../shared/config';
import {FocusModule} from '../../../../../shared/directives/focus/index';
import {Device, DeviceApiParams} from '../../../../../shared/models/device';
import {FailureModule} from '../../shared/failure';
import {Loan} from '../../shared/loan';
import {Storage} from '../../shared/storage/storage';

import {StatusComponent} from './index';
import {MaterialModule} from './material_module';

/** Mock material DialogRef. */
class MatDialogRefMock {}

describe('StatusComponent', () => {
  let app: StatusComponent;
  let fixture: ComponentFixture<StatusComponent>;
  let loan: Loan;

  // Mock response of device info
  const testDeviceInfo: DeviceApiParams = {
    due_date: moment().toDate(),
    max_extend_date: moment().add(1, 'w').toDate(),
    given_name: 'John',
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
            ConfigService,
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
    spyOn(loan, 'getDevice').and.returnValue(of(new Device(testDeviceInfo)));
    app.setLoanInfo();
    fixture.detectChanges();
    expect(app.device.dueDate).toEqual(testDeviceInfo.due_date);
    expect(app.device.maxExtendDate).toEqual(testDeviceInfo.max_extend_date);
    expect(app.device.givenName).toEqual(testDeviceInfo.given_name);
    expect(app.device.guestAllowed).toEqual(testDeviceInfo.guest_permitted);
    expect(app.device.guestEnabled).toEqual(testDeviceInfo.guest_enabled);
  });

  it('renders content on the page', () => {
    app.device.dueDate = new Date(2018, 1, 1);
    app.device.assetTag = 'asset tag';
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent)
        .toContain('Please return this device by:');
  });
});
