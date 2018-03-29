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

import {Device} from '../../models/device';
import {LoanerSnackBar} from '../../services/snackbar';

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

  beforeEach(fakeAsync(() => {
    TestBed
        .configureTestingModule({
          declarations: [EnrollUnenrollComponentTest],
          imports: [
            DeviceActionBoxModule,
            RouterTestingModule,
            BrowserAnimationsModule,
          ],
          providers: [LoanerSnackBar],
        })
        .compileComponents();

    flushMicrotasks();

    fixture = TestBed.createComponent(EnrollUnenrollComponentTest);
    testComponent = fixture.debugElement.componentInstance;
  }));

  it('creates the EnrollUnenrollComponentTest', () => {
    expect(EnrollUnenrollComponentTest).toBeTruthy();
  });

  it('renders the DeviceActionBox with serial number input', () => {
    testComponent.action = 'enroll';
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    const actionBoxContent = compiled.querySelector('.action-box');
    const formField = compiled.querySelector('.mat-form-field.serial-number');
    const input = formField.querySelector('input');

    expect(actionBoxContent).toBeDefined();
    expect(actionBoxContent.textContent).toContain('Serial number');
    expect(formField).toBeDefined();
    expect(formField.textContent).toContain('Serial number');
    expect(input).toBeDefined();
  });

  it('renders the DeviceActionBox with asset tag input', () => {
    testComponent.action = 'enroll';
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    const actionBoxContent = compiled.querySelector('.action-box');
    const formField = compiled.querySelector('.mat-form-field.asset-tag');
    const input = formField.querySelector('input');

    expect(actionBoxContent).toBeDefined();
    expect(actionBoxContent.textContent).toContain('Asset tag');
    expect(formField).toBeDefined();
    expect(formField.textContent).toContain('Asset tag');
    expect(input).toBeDefined();
  });

  it('renders the asset tag input as not required', () => {
    testComponent.action = 'enroll';
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    const formField = compiled.querySelector('.mat-form-field.asset-tag');
    const input = formField.querySelector('input');

    expect(input).toBeDefined();
    expect(input.getAttribute('required')).toBeFalsy();
  });

  it('renders the DeviceActionBox with enroll action', () => {
    testComponent.action = 'enroll';
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    const actionBoxContent = compiled.querySelector('.action-box');
    const deviceInput = actionBoxContent.querySelector('.mat-form-field');
    const actionButton = actionBoxContent.querySelector('.action-button');

    expect(actionBoxContent).toBeDefined();
    expect(actionBoxContent.querySelector('h2').textContent)
        .toContain('Add device');
    expect(deviceInput).toBeDefined();
    expect(deviceInput.textContent).toContain('Serial number');
    expect(actionButton).toBeDefined();
    expect(actionButton.getAttribute('disabled')).toBe('');
  });

  it('renders the DeviceActionBox with unenroll action', () => {
    testComponent.action = 'unenroll';
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    const actionBoxContent = compiled.querySelector('.action-box');
    const deviceInput = actionBoxContent.querySelector('.mat-form-field');
    const actionButton = actionBoxContent.querySelector('.action-button');

    expect(actionBoxContent).toBeDefined();
    expect(actionBoxContent.querySelector('h2').textContent)
        .toContain('Remove device');
    expect(deviceInput).toBeDefined();
    expect(deviceInput.textContent).toContain('Serial number');
    expect(actionButton).toBeDefined();
    expect(actionButton.getAttribute('disabled')).toBe('');
  });

  it('does not render the DeviceActionBox with an invalid action', () => {
    testComponent.action = 'invalid';
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;

    expect(compiled.querySelector('.action-box')).toBeNull();
  });

  it('emits device event when action button is pressed', () => {
    testComponent.action = 'enroll';
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    const actionBoxContent = compiled.querySelector('.action-box');
    const actionButton = actionBoxContent.querySelector('.action-button');

    const actionBoxFixture =
        fixture.debugElement.query(By.directive(DeviceActionBox));
    const actionBox = actionBoxFixture.componentInstance;

    actionBox.device.serialNumber = '123123';
    fixture.detectChanges();

    spyOn(testComponent, 'takeAction');
    fixture.detectChanges();

    actionButton.dispatchEvent(new Event('click'));

    expect(testComponent.takeAction).toHaveBeenCalled();
  });

  it('disables the submit button while serial number is missing', () => {
    testComponent.action = 'enroll';
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    const actionBoxContent = compiled.querySelector('.action-box');
    const actionButton = actionBoxContent.querySelector('.action-button');

    const actionBoxFixture =
        fixture.debugElement.query(By.directive(DeviceActionBox));
    const actionBox = actionBoxFixture.componentInstance;

    actionBox.device.serialNumber = null;
    fixture.detectChanges();

    expect(actionButton.getAttribute('disabled')).toBeDefined();
  });

  it('enables the submit button when serial number is filled', () => {
    testComponent.action = 'enroll';
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    const actionBoxContent = compiled.querySelector('.action-box');
    const actionButton = actionBoxContent.querySelector('.action-button');

    const actionBoxFixture =
        fixture.debugElement.query(By.directive(DeviceActionBox));
    const actionBox = actionBoxFixture.componentInstance;

    actionBox.device.serialNumber = '123123';
    fixture.detectChanges();

    expect(actionButton.getAttribute('disabled')).toBeFalsy();
  });
});
