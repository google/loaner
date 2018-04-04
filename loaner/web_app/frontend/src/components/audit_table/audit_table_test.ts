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

import {ComponentFixture, fakeAsync, flushMicrotasks, TestBed, tick} from '@angular/core/testing';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {ActivatedRoute} from '@angular/router';
import {RouterTestingModule} from '@angular/router/testing';
import {Observable} from 'rxjs';
import {of} from 'rxjs/observable/of';

import {Device} from '../../models/device';
import {DeviceService} from '../../services/device';
import {Dialog} from '../../services/dialog';
import {ShelfService} from '../../services/shelf';
import {ActivatedRouteMock, DeviceServiceMock, ShelfServiceMock} from '../../testing/mocks';

import {AuditTable, AuditTableModule, Status} from '.';

describe('AuditTableComponent', () => {
  let fixture: ComponentFixture<AuditTable>;
  let auditTable: AuditTable;

  beforeEach(fakeAsync(() => {
    TestBed
        .configureTestingModule({
          imports: [
            RouterTestingModule,
            AuditTableModule,
            BrowserAnimationsModule,
          ],
          providers: [
            {provide: ActivatedRoute, useClass: ActivatedRouteMock},
            {provide: ShelfService, useClass: ShelfServiceMock},
            {provide: DeviceService, useClass: DeviceServiceMock},
          ],
        })
        .compileComponents();

    flushMicrotasks();

    fixture = TestBed.createComponent(AuditTable);
    auditTable = fixture.debugElement.componentInstance;
  }));

  it('creates the AuditTable', () => {
    expect(auditTable).toBeTruthy();
    expect(auditTable.devicesToBeCheckedIn.length).toBe(0);
  });

  it('renders card title in a mat-card-title', () => {
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    expect(compiled.querySelector('.mat-card-title').textContent)
        .toContain('Friendly name 1');
  });

  it('renders "Identifier" inside row-header', () => {
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    expect(compiled.querySelector('.header-row').textContent)
        .toContain('Identifier');
  });

  it('renders an mat-input with placeholder inside card title', () => {
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    const inputContainer =
        compiled.querySelector('.mat-card-title mat-form-field');
    expect(inputContainer).toBeTruthy();
    expect(inputContainer.querySelector('input[matInput]')
               .getAttribute('placeholder'))
        .toBe('Serial Number');
  });

  it('has a audit empty button at beginning', () => {
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    const auditEmptyButton = compiled.querySelector('button.audit');
    expect(auditEmptyButton).toBeTruthy();
    expect(auditEmptyButton.textContent).toBe('Audit Empty');
  });

  it('enables audit button with only READY elements in the list', () => {
    auditTable.devicesToBeCheckedIn = [
      {
        device: new Device({
          asset_tag: '321653',
          device_model: 'chromebook',
          serial_number: '321653',
          pending_return: false,
          assigned_on_date: 1499202031707,
          last_update: 1499202031707,
        }),
        status: Status.READY,
      },
    ];
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    const auditButton = compiled.querySelector('button.audit');
    expect(auditButton).toBeTruthy();
    expect(auditButton.getAttribute('disabled')).toBeNull();
  });

  it('disables audit button with ERROR elements only in the list', () => {
    auditTable.devicesToBeCheckedIn = [
      {
        device: new Device({
          asset_tag: '321653',
          device_model: 'chromebook',
          serial_number: '321653',
          pending_return: false,
          assigned_on_date: 1499202031707,
          last_update: 1499202031707,
        }),
        status: Status.READY,
      },
      {
        device: new Device({
          asset_tag: '321653',
          device_model: 'chromebook',
          serial_number: '321653',
          pending_return: false,
          assigned_on_date: 1499202031707,
          last_update: 1499202031707,
        }),
        status: Status.ERROR,
      },
    ];
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    const auditButton = compiled.querySelector('button.audit');
    expect(auditButton).toBeTruthy();
    expect(auditButton.getAttribute('disabled')).toBe('');
  });

  it('calls shelf service when audit button is clicked', () => {
    auditTable.devicesToBeCheckedIn = [
      {
        device: new Device({
          asset_tag: '1',
          device_model: 'chromebook',
          serial_number: '321653',
          pending_return: false,
          assigned_on_date: 1499202031707,
          last_update: 1499202031707,
        }),
        status: Status.READY,
      },
    ];
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;

    expect(auditTable.devicesToBeCheckedIn.length).toBe(1);
    const matCard = compiled.querySelector('.mat-card');
    const matCardContent = matCard.querySelector('.mat-card-content');
    const auditButton = compiled.querySelector('button.audit');
    const shelfService = TestBed.get(ShelfService);
    spyOn(shelfService, 'audit').and.callThrough();

    auditButton.dispatchEvent(new Event('click'));

    fixture.detectChanges();
    expect(auditTable.devicesToBeCheckedIn.length).toBe(0);
    expect(matCardContent.querySelectorAll('.mat-list > .mat-list-item').length)
        .toBe(0);
    expect(shelfService.audit).toHaveBeenCalledWith(auditTable.shelf, [
      '321653'
    ]);
  });

  it('calls shelf service when audit empty button is clicked', () => {
    auditTable.devicesToBeCheckedIn = [];
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;

    expect(auditTable.devicesToBeCheckedIn.length).toBe(0);
    const matCard = compiled.querySelector('.mat-card');
    const matCardContent = matCard.querySelector('.mat-card-content');
    const auditEmptyButton = compiled.querySelector('button.audit');
    console.log(auditEmptyButton);
    const shelfService = TestBed.get(ShelfService);
    spyOn(shelfService, 'audit').and.callThrough();

    auditEmptyButton.dispatchEvent(new Event('click'));
    fixture.detectChanges();
    const dialog: Dialog = TestBed.get(Dialog);
    spyOn(dialog, 'confirm').and.returnValue(of(true));
    fakeAsync(() => {
      auditTable.audit();
      tick(500);
      flushMicrotasks();
      tick(500);
      fixture.detectChanges();
      expect(shelfService.audit).toHaveBeenCalledWith(auditTable.shelf);
    });

    expect(auditTable.devicesToBeCheckedIn.length).toBe(0);
    expect(matCardContent.querySelectorAll('.mat-list > .mat-list-item').length)
        .toBe(0);
  });

  it('increment devicesToBeChecked when Add button is clicked', () => {
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    const matCard = compiled.querySelector('.mat-card');
    const matCardTitle = matCard.querySelector('.mat-card-title');
    const matCardContent = matCard.querySelector('.mat-card-content');
    const inputElement = matCardTitle.querySelector('mat-form-field input');
    const addButton = matCardTitle.querySelector('.add-to-audit-list-button');

    inputElement.value = '123123';
    addButton.dispatchEvent(new Event('click'));

    expect(auditTable.devicesToBeCheckedIn.length).toBe(1);
    expect(auditTable.devicesToBeCheckedIn[0].device.serialNumber)
        .toBe('123123');

    fixture.detectChanges();
    expect(matCardContent.querySelectorAll('.mat-list > .mat-list-item').length)
        .toBe(1);
  });

  it('increment devicesToBeChecked when "Enter" button is released', () => {
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    const matCard = compiled.querySelector('.mat-card');
    const matCardTitle = matCard.querySelector('.mat-card-title');
    const matCardContent = matCard.querySelector('.mat-card-content');
    const inputElement = matCardTitle.querySelector('mat-form-field input');

    inputElement.value = '123123';
    inputElement.dispatchEvent(new KeyboardEvent('keyup', {
      key: 'Enter',
    }));

    expect(auditTable.devicesToBeCheckedIn.length).toBe(1);
    expect(auditTable.devicesToBeCheckedIn[0].device.serialNumber)
        .toBe('123123');

    fixture.detectChanges();
    expect(matCardContent.querySelectorAll('.mat-list > .mat-list-item').length)
        .toBe(1);
  });

  it('decrement devicesToBeChecked when "Close" button is clicked.', () => {
    auditTable.devicesToBeCheckedIn = [
      {
        device: new Device({
          asset_tag: '321653',
          device_model: 'chromebook',
          serial_number: '321653',
          pending_return: false,
          assigned_on_date: 1499202031707,
          last_update: 1499202031707,
        }),
        status: Status.READY,
      },
      {
        device: new Device({
          asset_tag: '156854168',
          device_model: 'chromebook',
          serial_number: '156854168',
          pending_return: false,
          assigned_on_date: 1499202031707,
          last_update: 1499202031707,
        }),
        status: Status.READY,
      },
    ];
    fixture.detectChanges();
    expect(auditTable.devicesToBeCheckedIn.length).toBe(2);
    const compiled = fixture.debugElement.nativeElement;
    const matCard = compiled.querySelector('.mat-card');
    const matCardContent = matCard.querySelector('.mat-card-content');
    const matListItems =
        matCardContent.querySelectorAll('mat-list > mat-list-item');
    expect(matListItems.length).toBe(2);
    const closeButton = matListItems[0].querySelector('button:last-of-type');

    closeButton.dispatchEvent(new Event('click'));

    fixture.detectChanges();
    expect(matCardContent.querySelectorAll('.mat-list > .mat-list-item').length)
        .toBe(1);
  });

  it('check icon is present when devices are is in a READY status', () => {
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    const matCard = compiled.querySelector('.mat-card');
    const matCardContent = matCard.querySelector('.mat-card-content');

    auditTable.devicesToBeCheckedIn = [{
      device: new Device({asset_tag: '12123'}),
      status: Status.READY,
    }];

    fixture.detectChanges();
    const devicesOnScreen =
        matCardContent.querySelectorAll('.mat-list > .mat-list-item');

    expect(devicesOnScreen.length).toBe(1);
    expect(devicesOnScreen[0].querySelector('mat-icon')).not.toBe(null);
    expect(devicesOnScreen[0].querySelector('mat-icon').textContent)
        .toContain('check');
  });

  it('error icon is present when devices are is in a ERROR status', () => {
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    const matCard = compiled.querySelector('.mat-card');
    const matCardContent = matCard.querySelector('.mat-card-content');

    auditTable.devicesToBeCheckedIn = [{
      device: new Device({asset_tag: '12123'}),
      status: Status.ERROR,
    }];

    fixture.detectChanges();
    const devicesOnScreen =
        matCardContent.querySelectorAll('.mat-list > .mat-list-item');

    expect(devicesOnScreen.length).toBe(1);
    expect(devicesOnScreen[0].querySelector('mat-icon')).not.toBe(null);
    expect(devicesOnScreen[0].querySelector('mat-icon').textContent)
        .toContain('error');
  });
});
