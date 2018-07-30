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
import {of} from 'rxjs';

import {DeviceService} from '../../services/device';
import {DEVICE_1, DEVICE_2} from '../../testing/mocks';
import {DeviceServiceMock} from '../../testing/mocks';

import {DeviceEnrollUnenrollList, DeviceEnrollUnenrollListModule} from '.';

@Component({
  template:
      `<loaner-device-enroll-unenroll-list [currentAction]="currentAction">
      </loaner-device-enroll-unenroll-list>`,
})
class DummyComponent {
  currentAction = '';
}

describe('DeviceEnrollUnenrollList', () => {
  let fixture: ComponentFixture<DummyComponent>;
  let deviceEnrollUnenrollList: DeviceEnrollUnenrollList;

  beforeEach(fakeAsync(() => {
    TestBed
        .configureTestingModule({
          declarations: [DummyComponent],
          imports: [
            DeviceEnrollUnenrollListModule,
            BrowserAnimationsModule,
          ],
          providers: [{provide: DeviceService, useClass: DeviceServiceMock}],
        })
        .compileComponents();

    flushMicrotasks();

    fixture = TestBed.createComponent(DummyComponent);
    deviceEnrollUnenrollList =
        fixture.debugElement.query(By.directive(DeviceEnrollUnenrollList))
            .componentInstance;
  }));

  it('creates the DeviceEnrollUnenrollList', () => {
    expect(deviceEnrollUnenrollList).toBeTruthy();
    expect(deviceEnrollUnenrollList.devices.length).toBe(0);
  });

  it('renders "Identifier" inside row-header', () => {
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    expect(compiled.querySelector('.header-row').textContent)
        .toContain('Identifier');
  });

  it('renders enroll when current action is enroll', () => {
    const testComponent = fixture.debugElement.componentInstance;
    testComponent.currentAction = 'enroll';
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    expect(compiled.querySelector('.mat-card-content').textContent)
        .toContain('There are no devices to be enrolled');
  });

  it('renders unenroll when current action is unenroll', () => {
    const testComponent = fixture.debugElement.componentInstance;
    testComponent.currentAction = 'unenroll';
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    expect(compiled.querySelector('.mat-card-content').textContent)
        .toContain('There are no devices to be unenrolled');
  });

  it('renders enrolled device', () => {
    deviceEnrollUnenrollList.currentAction = 'enroll';
    const deviceService: DeviceService = TestBed.get(DeviceService);
    spyOn(deviceService, 'enroll').and.returnValue(of(['success']));
    deviceEnrollUnenrollList.deviceAction(DEVICE_1);
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    expect(compiled.querySelector('.mat-list-item').textContent)
        .toContain('device1');
    expect(compiled.querySelector('.mat-list-item').textContent)
        .toContain('check');
    expect(compiled.querySelector('.mat-icon')
               .attributes.getNamedItem('ng-reflect-message')
               .textContent)
        .toContain('Successfully enrolled');
  });

  it('renders unenrolled device', () => {
    deviceEnrollUnenrollList.currentAction = 'unenroll';
    const deviceService: DeviceService = TestBed.get(DeviceService);
    spyOn(deviceService, 'enroll').and.returnValue(of(['success']));
    spyOn(deviceService, 'unenroll').and.returnValue(of(['success']));
    deviceEnrollUnenrollList.deviceAction(DEVICE_2);
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    expect(compiled.querySelector('.mat-list-item').textContent)
        .toContain('device2');
    expect(compiled.querySelector('.mat-list-item').textContent)
        .toContain('check');
    expect(compiled.querySelector('.mat-icon')
               .attributes.getNamedItem('ng-reflect-message')
               .textContent)
        .toContain('Successfully unenrolled');
  });
});
