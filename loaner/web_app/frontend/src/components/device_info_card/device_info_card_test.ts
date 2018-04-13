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
import {ActivatedRoute, Params} from '@angular/router';
import {RouterTestingModule} from '@angular/router/testing';
import {BehaviorSubject, Observable, of} from 'rxjs';

import {Damaged} from '../../../../../shared/components/damaged';
import {Extend} from '../../../../../shared/components/extend';
import {GuestMode} from '../../../../../shared/components/guest';
import {Lost} from '../../../../../shared/components/lost';
import {DamagedMock, ExtendMock, GuestModeMock, LostMock} from '../../../../../shared/testing/mocks';
import {Device} from '../../models/device';
import {User} from '../../models/user';
import {DeviceService} from '../../services/device';
import {UserService} from '../../services/user';
import {DeviceServiceMock, TEST_DEVICE_1, TEST_DEVICE_2, TEST_DEVICE_NOT_MARKED_FOR_RETURN, TEST_DEVICE_WITH_ASSET_TAG, TEST_DEVICE_WITHOUT_ASSET_TAG, TEST_USER, UserServiceMock} from '../../testing/mocks';

import {DeviceInfoCard, DeviceInfoCardModule} from '.';

@Component({
  preserveWhitespaces: true,
  template: `<loaner-device-info-card></loaner-device-info-card>`,
})
class DummyComponent {
}

describe('DeviceInfoCardComponent', () => {
  let fixture: ComponentFixture<DummyComponent>;
  let testComponent: DummyComponent;
  let deviceInfoCard: DeviceInfoCard;
  const params = new BehaviorSubject<Params>({
    id: TEST_DEVICE_2.serialNumber,
  });
  // Month array for testing devices.
  const monthNames = [
    'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August',
    'September', 'October', 'November', 'December'
  ];

  // tslint:disable:no-any Jasmine returns any for the nativeElement
  const getCorrectButton = (compiled: any, buttonText: string) => {
    const buttons: any[] = Array.from(compiled.querySelectorAll('button'));

    return buttons.find(b => b.textContent!.indexOf(buttonText) > -1);
  };
  // tslint:enable:no-any

  beforeEach(fakeAsync(() => {
    TestBed
        .configureTestingModule({
          declarations: [DummyComponent],
          imports: [
            BrowserAnimationsModule,
            RouterTestingModule.withRoutes([
              {path: 'user/:id', component: DummyComponent},
            ]),
            DeviceInfoCardModule,
          ],
          providers: [
            {provide: ActivatedRoute, useValue: {params}},
            {provide: Damaged, useClass: DamagedMock},
            {provide: DeviceService, useClass: DeviceServiceMock},
            {provide: Extend, useClass: ExtendMock},
            {provide: GuestMode, useClass: GuestModeMock},
            {provide: Lost, useClass: LostMock},
            {provide: UserService, useClass: UserServiceMock},
          ],
        })
        .compileComponents();

    flushMicrotasks();

    fixture = TestBed.createComponent(DummyComponent);
    testComponent = fixture.debugElement.componentInstance;

    deviceInfoCard = fixture.debugElement.query(By.directive(DeviceInfoCard))
                         .componentInstance;
  }));

  it('creates the DeviceInfoCard', () => {
    expect(deviceInfoCard).toBeDefined();
  });

  it('lists all devices in a mat-tab-header by asset tag if possible.', () => {
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    const tabListContent =
        compiled.querySelector('.mat-tab-header').textContent;
    expect(tabListContent).toContain(TEST_DEVICE_WITH_ASSET_TAG.assetTag);
    expect(tabListContent)
        .toContain(TEST_DEVICE_WITHOUT_ASSET_TAG.serialNumber);
  });

  it('should display the username on the card.', () => {
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    const usernameText =
        compiled.querySelector('loaner-greetings-card').textContent;
    expect(usernameText).toContain(TEST_USER.givenName);
  });

  it('should show a due date if the device is not marked for return', () => {
    const deviceService: DeviceService = TestBed.get(DeviceService);
    spyOn(deviceService, 'listUserDevices')
        .and.returnValue(of([TEST_DEVICE_NOT_MARKED_FOR_RETURN]));
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    const tabGroupText = compiled.querySelector('.mat-tab-body').textContent;
    const dueDate = {
      month: TEST_DEVICE_NOT_MARKED_FOR_RETURN.dueDate.getMonth(),
      day: TEST_DEVICE_NOT_MARKED_FOR_RETURN.dueDate.getDate(),
      year: TEST_DEVICE_NOT_MARKED_FOR_RETURN.dueDate.getFullYear(),
    };
    const dateStringToExpect =
        `${monthNames[dueDate.month]} ${dueDate.day}, ${dueDate.year}`;
    expect(tabGroupText).toContain(dateStringToExpect);
  });

  it('should hide "...buttons below" text when no devices are assigned', () => {
    const deviceService: DeviceService = TestBed.get(DeviceService);
    spyOn(deviceService, 'listUserDevices').and.returnValue(of([]));
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    const greetingCardText =
        compiled.querySelector('loaner-greetings-card').textContent;
    expect(greetingCardText).not.toContain('buttons below');
  });

  it('should select the correct tab when route is provided', () => {
    const deviceService: DeviceService = TestBed.get(DeviceService);
    spyOn(deviceService, 'listUserDevices').and.returnValue(of([
      TEST_DEVICE_1,
      TEST_DEVICE_2,
    ]));
    params.next({id: TEST_DEVICE_2.assetTag});
    fixture.detectChanges();
    let compiled = fixture.debugElement.nativeElement;
    let selectedTab =
        compiled.querySelector('.mat-tab-label[aria-selected=true]')
            .textContent;
    expect(selectedTab).toContain(TEST_DEVICE_2.assetTag);

    params.next({id: TEST_DEVICE_1.assetTag});
    deviceInfoCard.ngOnInit();
    fixture.detectChanges();
    compiled = fixture.debugElement.nativeElement;
    selectedTab = compiled.querySelector('.mat-tab-label[aria-selected=true]')
                      .textContent;
    expect(selectedTab).toContain(TEST_DEVICE_1.assetTag);
  });
});
