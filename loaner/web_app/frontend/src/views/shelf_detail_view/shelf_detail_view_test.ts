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

import {HttpClientTestingModule} from '@angular/common/http/testing';
import {ComponentFixture, fakeAsync, flushMicrotasks, TestBed} from '@angular/core/testing';
import {DomSanitizer} from '@angular/platform-browser';
import {RouterTestingModule} from '@angular/router/testing';

import {MatIconRegistry} from '../../core/material_module';
import {ConfigService} from '../../services/config';
import {DeviceService} from '../../services/device';
import {ShelfService} from '../../services/shelf';
import {UserService} from '../../services/user';
import {ConfigServiceMock, DeviceServiceMock, ShelfServiceMock, UserServiceMock} from '../../testing/mocks';

import {ShelfDetailView, ShelfDetailViewModule} from '.';


describe('ShelfDetailView', () => {
  let fixture: ComponentFixture<ShelfDetailView>;
  let shelfDetailView: ShelfDetailView;

  beforeEach(fakeAsync(() => {
    TestBed
        .configureTestingModule({
          imports: [
            HttpClientTestingModule,
            RouterTestingModule,
            ShelfDetailViewModule,
          ],
          providers: [
            {provide: ConfigService, useClass: ConfigServiceMock},
            {provide: DeviceService, useClass: DeviceServiceMock},
            {provide: ShelfService, useClass: ShelfServiceMock},
            {provide: UserService, useClass: UserServiceMock},
          ],
        })
        .compileComponents();

    flushMicrotasks();

    const iconRegistry = TestBed.get(MatIconRegistry);
    const sanitizer = TestBed.get(DomSanitizer);
    iconRegistry.addSvgIcon(
        'checkin',
        // Note: The bypassSecurity here can't be refactored: the code
        // is destined to be open-sourced.
        sanitizer.bypassSecurityTrustResourceUrl('/fakepath/checkin'));
    fixture = TestBed.createComponent(ShelfDetailView);
    shelfDetailView = fixture.debugElement.componentInstance;
  }));

  it('should create the shelfDetailView', () => {
    expect(shelfDetailView).toBeTruthy();
  });

  it('should render shelf details', () => {
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    expect(compiled.getElementsByTagName('loaner-shelf-details')[0])
        .toBeTruthy();
  });

  it('should render device list table', () => {
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    expect(compiled.getElementsByTagName('loaner-device-list-table')[0])
        .toBeTruthy();
  });
});
