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

import {DatePipe} from '@angular/common';
import {ComponentFixture, ComponentFixtureAutoDetect, fakeAsync, flushMicrotasks, TestBed} from '@angular/core/testing';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {RouterTestingModule} from '@angular/router/testing';
import {DeviceService} from '../../services/device';
import {DEVICE_1, DeviceServiceMock} from '../../testing/mocks';

import {DeviceDetails, DeviceDetailsModule} from './';

describe('DeviceDetails', () => {
  let fixture: ComponentFixture<DeviceDetails>;
  let deviceDetails: DeviceDetails;

  beforeEach(fakeAsync(() => {
    TestBed
        .configureTestingModule({
          imports: [
            RouterTestingModule,
            DeviceDetailsModule,
            BrowserAnimationsModule,
          ],
          providers: [
            {provide: ComponentFixtureAutoDetect, useValue: true},
            {provide: DeviceService, useClass: DeviceServiceMock},
          ],
        })
        .compileComponents();

    flushMicrotasks();

    fixture = TestBed.createComponent(DeviceDetails);
    deviceDetails = fixture.debugElement.componentInstance;
  }));

  it('should create the DeviceDetails', () => {
    expect(deviceDetails).toBeTruthy();
  });

  it('should render the serial as title in a .mat-card-title', () => {
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    expect(compiled.querySelector('.mat-card-title').textContent)
        .toContain('Serial No:');
  });

  it('should render the asset tag inside .mat-list', () => {
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    expect(compiled.querySelector('.mat-list').textContent)
        .toContain('Asset tag');
  });

  it('should render device model inside .mat-list', () => {
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    expect(compiled.querySelector('.mat-list').textContent)
        .toContain('Device model');
  });

  it('should render current shelf inside .mat-list', () => {
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    expect(compiled.querySelector('.mat-list').textContent)
        .toContain('Current Shelf');
  });

  it('should render Current OU inside .mat-list', () => {
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    expect(compiled.querySelector('.mat-list').textContent)
        .toContain('Current OU');
  });

  it('should render Assigned to inside .mat-list', () => {
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    expect(compiled.querySelector('.mat-list').textContent)
        .toContain('Assigned to');
  });

  it('should render Due date inside .mat-list', () => {
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    expect(compiled.querySelector('.mat-list').textContent)
        .toContain('Due date');
  });

  it('should render Status inside .mat-list', () => {
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    expect(compiled.querySelector('.mat-list').textContent).toContain('Status');
  });

  it('renders the last known healthy datetime inside .mat-list', () => {
    deviceDetails.device = DEVICE_1;
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    expect(compiled.querySelector('.mat-list').textContent)
        .toContain('Last known healthy');
    const datePipe = new DatePipe('en');
    expect(compiled.querySelector('.lastKnownHealthy').textContent)
        .toContain(datePipe.transform(
            deviceDetails.device.lastKnownHealthy, 'medium'));
  });
});
