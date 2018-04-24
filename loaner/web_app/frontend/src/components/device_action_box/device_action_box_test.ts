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
import {ComponentFixture, fakeAsync, flushMicrotasks, TestBed} from '@angular/core/testing';
import {By} from '@angular/platform-browser';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {RouterTestingModule} from '@angular/router/testing';

import {of} from 'rxjs';

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
    configServiceSpy = spyOn(configService, 'getBooleanConfig');
    configServiceSpy.and.returnValue(of(true));
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

    it('renders serial number input', () => {
      const compiled = fixture.debugElement.nativeElement;
      const formField = compiled.querySelector('.mat-form-field.serial-number');
      const input = formField.querySelector('input');

      expect(formField.textContent).toContain('Serial number');
      expect(input).toBeDefined();
      expect(input.getAttribute('required')).not.toBeNull();
    });

    it('renders asset tag input if use_asset_tag is true', () => {
      const compiled = fixture.debugElement.nativeElement;
      const formField = compiled.querySelector('.mat-form-field.asset-tag');
      const input = formField.querySelector('input');

      expect(formField.textContent).toContain('Asset tag');
      expect(input).toBeDefined();
      expect(input.getAttribute('required')).not.toBeNull();
    });

    it('does not render asset tag input if use_asset_tag is false', () => {
      configServiceSpy.and.returnValue(of(false));
      actionBox.ngOnInit();
      fixture.detectChanges();
      const compiled = fixture.debugElement.nativeElement;
      const formField = compiled.querySelector('.mat-form-field.asset-tag');

      expect(formField).toBeNull();
    });

    it('only emits the device when button is pressed with asset tag', () => {
      const compiled = fixture.debugElement.nativeElement;
      const actionButton =
          compiled.querySelector('.action-button') as HTMLElement;

      spyOn(testComponent, 'takeAction');
      actionBox.device.serialNumber = '123123';
      fixture.detectChanges();

      actionButton.click();

      expect(testComponent.takeAction).not.toHaveBeenCalled();
      actionBox.device.assetTag = 'asset';
      fixture.detectChanges();

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

    it('only renders 1 input with placeholder depending on use_asset_tag',
       () => {
         let compiled = fixture.debugElement.nativeElement;
         let formFields = compiled.querySelectorAll('.mat-form-field');
         expect(formFields.length).toBe(1);

         let field = formFields[0];
         let input = field.querySelector('input');
         expect(field.textContent).toContain('Asset tag');
         expect(input).toBeDefined();
         expect(input.getAttribute('required')).not.toBeNull();

         configServiceSpy.and.returnValue(of(false));
         actionBox.ngOnInit();
         fixture.detectChanges();

         compiled = fixture.debugElement.nativeElement;
         formFields = compiled.querySelectorAll('.mat-form-field');
         expect(formFields.length).toBe(1);

         field = formFields[0];
         input = field.querySelector('input');
         expect(field.textContent).toContain('Serial Number');
         expect(input).toBeDefined();
         expect(input.getAttribute('required')).not.toBeNull();
       });
  });
});
