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
import {ComponentFixture, fakeAsync, flushMicrotasks, TestBed, tick} from '@angular/core/testing';
import {By} from '@angular/platform-browser';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {RouterTestingModule} from '@angular/router/testing';
import {of} from 'rxjs';

import {DeviceIdentifierModeType} from '../../models/config';
import {Device} from '../../models/device';
import {ConfigService} from '../../services/config';
import {LoanerSnackBar} from '../../services/snackbar';
import {ConfigServiceMock} from '../../testing/mocks';

import {DeviceActionBox, DeviceActionBoxModule} from '.';

@Component({
  preserveWhitespaces: true,
  template: `
    <loaner-device-action-box [action]="action"
                              (takeAction)="takeAction($event)">
    </loaner-device-action-box>`,
})
class EnrollUnenrollComponentTest {
  action = '';
  takeAction(device: Device) {
    return;
  }
}

describe('DeviceActionBox', () => {
  let fixture: ComponentFixture<EnrollUnenrollComponentTest>;
  let testComponent: EnrollUnenrollComponentTest;
  let actionBox: DeviceActionBox;
  let configService: ConfigService;
  let configServiceSpy: jasmine.Spy;

  beforeEach(fakeAsync(() => {
    TestBed
        .configureTestingModule({
          declarations: [EnrollUnenrollComponentTest],
          imports: [
            DeviceActionBoxModule,
            RouterTestingModule,
            BrowserAnimationsModule,
          ],
          providers: [
            LoanerSnackBar,
            {provide: ConfigService, useClass: ConfigServiceMock},
          ],
        })
        .compileComponents();

    flushMicrotasks();

    fixture = TestBed.createComponent(EnrollUnenrollComponentTest);
    testComponent = fixture.debugElement.componentInstance;
    actionBox = fixture.debugElement.query(By.directive(DeviceActionBox))
                    .componentInstance;

    configService = TestBed.get(ConfigService);
    configServiceSpy = spyOn(configService, 'getStringConfig');
    configServiceSpy.and.returnValue(
        of(DeviceIdentifierModeType.SERIAL_NUMBER));

    actionBox.ngOnInit();
  }));

  it('creates the EnrollUnenrollComponentTest', () => {
    expect(EnrollUnenrollComponentTest).toBeTruthy();
  });

  it('does not render the action box with an invalid action', () => {
    testComponent.action = 'invalid';
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;

    expect(compiled.querySelector('.action-box')).toBeNull();
  });

  describe('with enroll action', () => {
    beforeEach(() => {
      testComponent.action = 'enroll';
      fixture.detectChanges();
    });

    it('renders the action box', () => {
      const compiled = fixture.debugElement.nativeElement;
      const actionBoxContent = compiled.querySelector('.action-box');

      expect(actionBoxContent).toBeDefined();
      expect(actionBoxContent.querySelector('h2').textContent)
          .toContain('Add device');
    });

    it('renders serial input if device_identifier_mode is set to serial_number',
       () => {
         configServiceSpy.and.returnValue(
             of(DeviceIdentifierModeType.SERIAL_NUMBER));
         actionBox.ngOnInit();
         fixture.detectChanges();
         const compiled = fixture.debugElement.nativeElement;
         const formField =
             compiled.querySelector('.mat-form-field.serial-number');
         const input = formField.querySelector('input');

         expect(formField.textContent).toContain('Serial Number');
         expect(input).toBeDefined();
         expect(input.getAttribute('required')).not.toBeNull();
       });

    it('renders serial input if device_identifier_mode is set to both_required',
       () => {
         configServiceSpy.and.returnValue(
             of(DeviceIdentifierModeType.BOTH_REQUIRED));
         actionBox.ngOnInit();
         fixture.detectChanges();
         const compiled = fixture.debugElement.nativeElement;
         const formField =
             compiled.querySelector('.mat-form-field.serial-number');
         const input = formField.querySelector('input');

         expect(formField.textContent).toContain('Serial Number');
         expect(input).toBeDefined();
         expect(input.getAttribute('required')).not.toBeNull();
       });

    it('renders asset input if device_identifier_mode is set to asset_tag',
       () => {
         configServiceSpy.and.returnValue(
             of(DeviceIdentifierModeType.ASSET_TAG));
         actionBox.ngOnInit();
         fixture.detectChanges();
         const compiled = fixture.debugElement.nativeElement;
         const formField = compiled.querySelector('.mat-form-field.asset-tag');
         const input = formField.querySelector('input');

         expect(formField.textContent).toContain('Asset tag');
         expect(input).toBeDefined();
         expect(input.getAttribute('required')).not.toBeNull();
       });

    it('renders asset input if device_identifier_mode is set to both_required',
       () => {
         configServiceSpy.and.returnValue(
             of(DeviceIdentifierModeType.BOTH_REQUIRED));
         actionBox.ngOnInit();
         fixture.detectChanges();
         const compiled = fixture.debugElement.nativeElement;
         const formField = compiled.querySelector('.mat-form-field.asset-tag');
         const input = formField.querySelector('input');

         expect(formField.textContent).toContain('Asset tag');
         expect(input).toBeDefined();
         expect(input.getAttribute('required')).not.toBeNull();
       });

    it('renders 2 inputs if device_identifier_mode is set to both_required',
       () => {
         configServiceSpy.and.returnValue(
             of(DeviceIdentifierModeType.BOTH_REQUIRED));
         actionBox.ngOnInit();
         fixture.detectChanges();
         const compiled = fixture.debugElement.nativeElement;
         const inputFields = compiled.querySelectorAll('.mat-form-field');

         expect(inputFields.length).toBe(2);
       });

    it('renders 1 input if device_identifier_mode is not set to both_required',
       fakeAsync(() => {
         configServiceSpy.and.returnValue(
             of(DeviceIdentifierModeType.ASSET_TAG));
         actionBox.ngOnInit();
         tick();
         fixture.detectChanges();
         let compiled = fixture.debugElement.nativeElement;
         let inputFields = compiled.querySelectorAll('.mat-form-field');

         expect(inputFields.length).toBe(1);

         configServiceSpy.and.returnValue(
             of(DeviceIdentifierModeType.SERIAL_NUMBER));
         actionBox.ngOnInit();
         fixture.detectChanges();
         compiled = fixture.debugElement.nativeElement;
         inputFields = compiled.querySelectorAll('.mat-form-field');

         expect(inputFields.length).toBe(1);
       }));

    it('only emits the device when button is pressed with asset tag', () => {
      configServiceSpy.and.returnValue(
          of(DeviceIdentifierModeType.BOTH_REQUIRED));
      spyOn(testComponent, 'takeAction');
      actionBox.device.serialNumber = '123123';
      actionBox.ngOnInit();
      fixture.detectChanges();
      let compiled = fixture.debugElement.nativeElement;
      let actionButton =
          compiled.querySelector('.action-button') as HTMLElement;

      actionButton.click();

      expect(testComponent.takeAction).not.toHaveBeenCalled();
      actionBox.device.assetTag = 'asset';
      actionBox.ngOnInit();
      fixture.detectChanges();
      compiled = fixture.debugElement.nativeElement;
      actionButton = compiled.querySelector('.action-button') as HTMLElement;

      actionButton.click();

      expect(testComponent.takeAction).toHaveBeenCalled();
    });

    it('enables submit button only with serial AND asset filled', () => {
      actionBox.device.serialNumber = 'serial';
      actionBox.device.assetTag = 'asset';
      fixture.detectChanges();
      const actionButton =
          fixture.debugElement.nativeElement.querySelector('.action-button');
      expect(actionButton.getAttribute('disabled')).toBeNull();
    });
  });

  describe('with unenroll action', () => {
    beforeEach(() => {
      testComponent.action = 'unenroll';
      fixture.detectChanges();
    });

    it('renders the action box', () => {
      const compiled = fixture.debugElement.nativeElement;
      const actionBoxContent = compiled.querySelector('.action-box');

      expect(actionBoxContent).toBeDefined();
      expect(actionBoxContent.querySelector('h2').textContent)
          .toContain('Remove device');
    });

    it('only renders 1 input with placeholder depending on device_identifier',
       () => {
         let compiled = fixture.debugElement.nativeElement;
         let formFields = compiled.querySelectorAll('.mat-form-field');
         expect(formFields.length).toBe(1);

         let field = formFields[0];
         let input = field.querySelector('input');
         expect(field.textContent).toContain('Serial Number');
         expect(input).toBeDefined();
         expect(input.getAttribute('required')).not.toBeNull();

         configServiceSpy.and.returnValue(
             of(DeviceIdentifierModeType.BOTH_REQUIRED));
         actionBox.ngOnInit();
         fixture.detectChanges();

         compiled = fixture.debugElement.nativeElement;
         formFields = compiled.querySelectorAll('.mat-form-field');
         expect(formFields.length).toBe(1);

         field = formFields[0];
         input = field.querySelector('input');
         expect(field.textContent).toContain('Asset tag');
         expect(input).toBeDefined();
         expect(input.getAttribute('required')).not.toBeNull();
       });
  });
});
