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
import {FormsModule} from '@angular/forms';
import {DateAdapter} from '@angular/material/core';
import * as moment from 'moment';
import {of} from 'rxjs';

import {LoaderModule} from '../../../../../shared/components/loader';
import {LoanerDateAdapter} from '../../../../../shared/components/loaner_date_adapter/LoanerDateAdapter';
import {ConfigService} from '../../../../../shared/config';
import {Device, DeviceApiParams} from '../../../../../shared/models/device';
import {FailureModule} from '../../shared/failure';
import {Loan} from '../../shared/loan';
import {ReturnDateService} from '../../shared/return_date_service';

import {ReturnComponent} from './index';
import {MaterialModule} from './material_module';

describe('ReturnComponent', () => {
  let app: ReturnComponent;
  let fixture: ComponentFixture<ReturnComponent>;
  let loan: Loan;
  let returnService: ReturnDateService;

  // Mock response of device info
  const testDeviceInfo: DeviceApiParams = {
    due_date: moment('2018-06-04').toDate(),
    max_extend_date: moment('2018-06-17').toDate(),
    given_name: 'John',
    guest_enabled: false,
    guest_permitted: true,
  };

  beforeEach(() => {
    TestBed
        .configureTestingModule({
          declarations: [ReturnComponent],
          imports: [
            FailureModule,
            FormsModule,
            LoaderModule,
            MaterialModule,
            HttpClientTestingModule,
          ],
          providers: [
            ConfigService,
            HttpClient,
            Loan,
            ReturnDateService,
            {
              provide: DateAdapter,
              useClass: LoanerDateAdapter,
            },
          ],
        })
        .compileComponents();

    loan = TestBed.get(Loan);
    returnService = TestBed.get(ReturnDateService);
    fixture = TestBed.createComponent(ReturnComponent);
    app = fixture.debugElement.componentInstance;

    const today = moment('2018-06-04').toDate();
    jasmine.clock().mockDate(today);
  });

  it('renders the page as loading', () => {
    app.waiting();
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelector('loaner-loader')).toBeTruthy();
  });

  it('renders content on the page', () => {
    spyOn(loan, 'getDevice').and.returnValue(of(new Device(testDeviceInfo)));
    app.ready();
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent)
        .toContain('Choose your return date');
  });

  it('retrieves the loan information', () => {
    spyOn(loan, 'getDevice').and.returnValue(of(new Device(testDeviceInfo)));
    app.ready();
    fixture.detectChanges();
    expect(app.device.dueDate).toEqual(testDeviceInfo.due_date);
  });

  it('fails to retrieve the loan information and provides a helpful card',
     () => {
       spyOn(loan, 'getDevice').and.returnValue(of(new Device()));
       fixture.detectChanges();
       expect(app.device.dueDate).toBeFalsy();
       expect(fixture.nativeElement.textContent)
           .toContain('Oh no! There was an issue');
     });

  it('allows the loan to be extended 1 day', () => {
    spyOn(loan, 'getDevice').and.returnValue(of(new Device(testDeviceInfo)));
    app.ready();
    fixture.detectChanges();
    app.newReturnDate = moment().add(1, 'd').toDate();
    returnService.updateNewReturnDate(app.newReturnDate);
    const attributes = fixture.debugElement.nativeElement
                           .querySelector('input.mat-input-element')
                           .attributes as NamedNodeMap;
    expect(attributes.getNamedItem('min')!.value)
        .toEqual(moment(app.getMinimumReturnDate()).format('YYYY[-]MM[-]DD'));
    expect(attributes.getNamedItem('max')!.value)
        .toEqual(
            moment(testDeviceInfo.max_extend_date!).format('YYYY[-]MM[-]DD'));
    expect(returnService.changeReturnDate()).toBeTruthy();
  });

  it('does NOT allow the loan to be extended 2 weeks', () => {
    spyOn(loan, 'getDevice').and.returnValue(of(new Device(testDeviceInfo)));
    app.ready();
    fixture.detectChanges();
    app.newReturnDate = moment().add(2, 'w').toDate();
    returnService.updateNewReturnDate(app.newReturnDate);
    const attributes = fixture.debugElement.nativeElement
                           .querySelector('input.mat-input-element')
                           .attributes as NamedNodeMap;
    expect(attributes.getNamedItem('min')!.value)
        .toEqual(moment(app.getMinimumReturnDate()).format('YYYY[-]MM[-]DD'));
    expect(attributes.getNamedItem('max')!.value)
        .toEqual(
            moment(testDeviceInfo.max_extend_date!).format('YYYY[-]MM[-]DD'));
    expect(returnService.changeReturnDate()).toBeFalsy();
  });

  it('uses loaner date adapter when displaying the date input', () => {
    spyOn(loan, 'getDevice').and.returnValue(of(new Device(testDeviceInfo)));
    app.ready();
    fixture.detectChanges();
    fixture.whenStable().then(() => {
      const compiled = fixture.debugElement.nativeElement;
      expect(compiled.querySelector('input.mat-input-element').value)
          .toBe('June 4, 2018');
    });
  });
});
