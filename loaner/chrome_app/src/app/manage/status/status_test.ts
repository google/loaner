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

import {Damaged} from '../../../../../shared/components/damaged';
import {Extend} from '../../../../../shared/components/extend';
import {GuestMode} from '../../../../../shared/components/guest';
import {LoaderModule} from '../../../../../shared/components/loader';
import {GreetingsCardModule} from '../../../../../shared/components/loan_management/greetings_card';
import {LoanActionsCardModule} from '../../../../../shared/components/loan_management/loan_actions_card';
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

  beforeEach(() => {
    TestBed
        .configureTestingModule({
          declarations: [StatusComponent],
          imports: [
            BrowserAnimationsModule,
            FailureModule,
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
