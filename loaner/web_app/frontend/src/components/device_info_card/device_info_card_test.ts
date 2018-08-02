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
import {ActivatedRoute, Params, Router} from '@angular/router';
import {RouterTestingModule} from '@angular/router/testing';
import {BehaviorSubject, of} from 'rxjs';

import {Damaged} from '../../../../../shared/components/damaged';
import {Extend} from '../../../../../shared/components/extend';
import {GuestMode} from '../../../../../shared/components/guest';
import {Lost} from '../../../../../shared/components/lost';
import {DamagedMock, ExtendMock, GuestModeMock, LostMock} from '../../../../../shared/testing/mocks';
import {DeviceService} from '../../services/device';
import {UserService} from '../../services/user';
import {DEVICE_1, DEVICE_2, DEVICE_ASSIGNED, DEVICE_NOT_MARKED_FOR_RETURN, DEVICE_WITH_ASSET_TAG, DEVICE_WITHOUT_ASSET_TAG, DeviceServiceMock, TEST_USER, UserServiceMock} from '../../testing/mocks';

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
  let router: Router;
  const mockParams = new BehaviorSubject<Params>({
    id: DEVICE_2.serialNumber,
  });
  // By default, we leave this view query parameter empty, but initialized.
  const mockQueryParams = new BehaviorSubject<Params>({
    user: undefined,
  });
  // Month array for testing devices.
  const monthNames = [
    'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August',
    'September', 'October', 'November', 'December'
  ];

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
            {
              provide: ActivatedRoute,
              useValue: {
                params: mockParams,
                queryParams: mockQueryParams,
              }
            },
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
    router = TestBed.get(Router);

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
    expect(tabListContent).toContain(DEVICE_WITH_ASSET_TAG.assetTag);
    expect(tabListContent).toContain(DEVICE_WITHOUT_ASSET_TAG.serialNumber);
  });

  it('displays the username on the card.', () => {
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    const usernameText =
        compiled.querySelector('loaner-greetings-card').textContent;
    expect(usernameText).toContain(TEST_USER.givenName);
  });

  it('shows a due date if the device is not marked for return', () => {
    const deviceService: DeviceService = TestBed.get(DeviceService);
    spyOn(deviceService, 'listUserDevices')
        .and.returnValue(of([DEVICE_NOT_MARKED_FOR_RETURN]));
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    const tabGroupText = compiled.querySelector('.mat-tab-body').textContent;
    const dueDate = {
      month: DEVICE_NOT_MARKED_FOR_RETURN.dueDate.getMonth(),
      day: DEVICE_NOT_MARKED_FOR_RETURN.dueDate.getDate(),
      year: DEVICE_NOT_MARKED_FOR_RETURN.dueDate.getFullYear(),
    };
    const dateStringToExpect =
        `${monthNames[dueDate.month]} ${dueDate.day}, ${dueDate.year}`;
    expect(tabGroupText).toContain(dateStringToExpect);
  });

  it('hides "...buttons below" text when no devices are assigned', () => {
    const deviceService: DeviceService = TestBed.get(DeviceService);
    spyOn(deviceService, 'listUserDevices').and.returnValue(of([]));
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    const greetingCardText =
        compiled.querySelector('loaner-greetings-card').textContent;
    expect(greetingCardText).not.toContain('buttons below');
  });

  it('selects the correct tab when route is provided', () => {
    const deviceService: DeviceService = TestBed.get(DeviceService);
    spyOn(deviceService, 'listUserDevices').and.returnValue(of([
      DEVICE_1,
      DEVICE_2,
    ]));
    mockParams.next({id: DEVICE_2.assetTag});
    fixture.detectChanges();
    let compiled = fixture.debugElement.nativeElement;
    let selectedTab =
        compiled.querySelector('.mat-tab-label[aria-selected=true]')
            .textContent;
    expect(selectedTab).toContain(DEVICE_2.assetTag);

    mockParams.next({id: DEVICE_1.assetTag});
    deviceInfoCard.ngOnInit();
    fixture.detectChanges();
    compiled = fixture.debugElement.nativeElement;
    selectedTab = compiled.querySelector('.mat-tab-label[aria-selected=true]')
                      .textContent;
    expect(selectedTab).toContain(DEVICE_1.assetTag);
  });

  it('goes to the search results page for user magic with no devices assigned',
     () => {
       const deviceService: DeviceService = TestBed.get(DeviceService);
       spyOn(deviceService, 'list').and.returnValue(of({
         devices: [],
         totalResults: 0,
         totalPages: 1,
       }));
       spyOn(router, 'navigate');
       mockParams.next({id: ''});
       mockQueryParams.next({user: 'magic'});
       fixture.detectChanges();
       expect(router.navigate).toHaveBeenCalledWith(['/search/user/', 'magic']);
     });

  it('shows the user search for test_user with an assigned device', () => {
    const deviceService: DeviceService = TestBed.get(DeviceService);
    spyOn(deviceService, 'list').and.returnValue(of({
      devices: [DEVICE_ASSIGNED],
      totalResults: 0,
      totalPages: 1,
    }));
    mockParams.next({id: ''});
    mockQueryParams.next({user: 'test_user'});
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    const imitatingUserCardText =
        compiled.querySelector('mat-card').textContent;
    const selectedTab =
        compiled.querySelector('.mat-tab-label[aria-selected=true]')
            .textContent;
    expect(selectedTab).toContain(DEVICE_ASSIGNED.serialNumber);
    expect(imitatingUserCardText)
        .toContain('You are viewing devices on behalf of test_user');
  });

  it('updates list of devices after marking a device as lost', () => {
    const deviceService: DeviceService = TestBed.get(DeviceService);
    spyOn(deviceService, 'markAsLost').and.returnValue(of([
      DEVICE_1,
    ]));
    spyOn(deviceService, 'list').and.returnValue(of({
      devices: [DEVICE_ASSIGNED],
      totalResults: 0,
      totalPages: 1,
    }));
    deviceInfoCard.onLost(DEVICE_1);
    expect(deviceService.list).toHaveBeenCalled();
  });
});
