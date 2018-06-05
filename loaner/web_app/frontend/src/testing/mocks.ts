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

import {BehaviorSubject, Observable, of} from 'rxjs';

import {CONFIG} from '../app.config';
import * as bootstrap from '../models/bootstrap';
import * as config from '../models/config';
import {Device, ListDevicesResponse} from '../models/device';
import {ListShelfResponse, Shelf, ShelfRequestParams} from '../models/shelf';
import {User} from '../models/user';


export class ShelfServiceMock {
  dataChange = new BehaviorSubject<Shelf[]>([
    new Shelf({
      friendly_name: 'Friendly name 1',
      location: 'Location 1',
      last_audit_by: 'user',
      capacity: 10,
      last_audit_time: new Date(2018, 1, 1),
      shelf_request: {
        location: 'Location 1',
        urlsafe_key: 'urlsafekey1',
      }
    }),
    new Shelf({
      friendly_name: 'Friendly name 2',
      location: 'Location 2',
      last_audit_by: 'user',
      capacity: 10,
      last_audit_time: new Date(2018, 1, 1),
      shelf_request: {
        location: 'Location 2',
        urlsafe_key: 'urlsafekey2',
      }
    }),
    new Shelf({
      friendly_name: 'Friendly name 3',
      location: 'Location 3',
      last_audit_by: 'user',
      capacity: 10,
      last_audit_time: new Date(2018, 1, 1),
      shelf_request: {
        location: 'Location 3',
        urlsafe_key: 'urlsafekey3',
      }
    }),
    new Shelf({
      friendly_name: 'Friendly name 4',
      location: 'Location 4',
      last_audit_by: 'user',
      capacity: 10,
      last_audit_time: new Date(2018, 1, 1),
      shelf_request: {
        location: 'Location 4',
        urlsafe_key: 'urlsafekey4',
      }
    }),
    new Shelf({
      friendly_name: 'Friendly name 5',
      location: 'Location 5',
      last_audit_by: 'user',
      capacity: 10,
      last_audit_time: new Date(2018, 1, 1),
      shelf_request: {
        location: 'Location 5',
        urlsafe_key: 'urlsafekey5',
      }
    }),
  ]);
  create() {
    return;
  }
  update() {
    return;
  }
  disable() {
    return;
  }
  get data() {
    return this.dataChange.value;
  }
  getResponsiblesForAuditList(): Observable<string[]> {
    return new Observable(observer => {
      observer.next(['one']);
    });
  }

  list(): Observable<ListShelfResponse> {
    return of({
      shelves: this.data,
      totalResults: this.data.length,
      totalPages: 1,
    });
  }

  getShelf(): Observable<Shelf> {
    return new Observable(observer => {
      observer.next(this.data[0]);
    });
  }

  audit(shelf: Shelf, deviceIdList: string[]): Observable<null> {
    return new Observable(observer => {
      observer.next(null);
    });
  }
}

export class BootstrapServiceMock {
  run() {
    return of(
        {'started': true, 'enabled': true, 'completed': false, 'tasks': []} as
        bootstrap.Status);
  }
  getStatus() {
    return new Observable(observer => {
      observer.next({'enabled': true, 'completed': true, 'tasks': []});
    });
  }
}

export const DEVICE_1 = new Device({
  asset_tag: 'device1',
  device_model: 'chromebook',
  serial_number: '321653',
  pending_return: false,
  assignment_date: new Date(2018, 1, 1),
  last_known_healthy: new Date(2018, 1, 1),
  due_date: new Date(2018, 1, 1),
  current_ou: 'ROOT',
  max_extend_date: new Date(2018, 1, 4),
});

export const DEVICE_2 = new Device({
  asset_tag: 'device2',
  device_model: 'chromebook',
  serial_number: '236135',
  pending_return: true,
  assignment_date: new Date(2018, 1, 1),
  last_known_healthy: new Date(2018, 1, 1),
  due_date: new Date(2018, 1, 1),
  current_ou: 'ROOT',
  max_extend_date: new Date(2018, 1, 4),

});

export const DEVICE_WITH_ASSET_TAG = new Device({
  asset_tag: 'abc',
  device_model: 'chromebook',
  serial_number: '777001',
  pending_return: false,
  assignment_date: new Date(2018, 1, 1),
  last_known_healthy: new Date(2018, 1, 1),
  due_date: new Date(2018, 1, 1),
  current_ou: 'ROOT',
  max_extend_date: new Date(2018, 1, 4),

});

export const DEVICE_WITHOUT_ASSET_TAG = new Device({
  asset_tag: '',
  device_model: 'chromebook',
  serial_number: '777002',
  pending_return: false,
  assignment_date: new Date(2018, 1, 1),
  last_known_healthy: new Date(2018, 1, 1),
  due_date: new Date(2018, 1, 1),
  current_ou: 'ROOT',
  max_extend_date: new Date(2018, 1, 4),
});

export const DEVICE_MARKED_FOR_RETURN = new Device({
  asset_tag: '',
  device_model: 'chromebook',
  serial_number: '777003',
  pending_return: true,
  assignment_date: new Date(2018, 1, 1),
  last_known_healthy: new Date(2018, 1, 1),
  due_date: new Date(2018, 1, 1),
  current_ou: 'ROOT',
});

export const DEVICE_NOT_MARKED_FOR_RETURN = new Device({
  asset_tag: '',
  device_model: 'chromebook',
  serial_number: '777004',
  pending_return: false,
  assignment_date: new Date(2018, 1, 1),
  last_known_healthy: new Date(2018, 1, 1),
  due_date: new Date(2018, 1, 1),
  current_ou: 'ROOT',
  max_extend_date: new Date(2018, 1, 4),
});

export const DEVICE_UNASSIGNED = new Device({
  device_model: 'chromebook',
  serial_number: '777005',
  pending_return: false,
  due_date: new Date(2018, 1, 1),
  current_ou: 'ROOT',
});

export const DEVICE_ASSIGNED = new Device({
  assigned_user: 'test_user',
  device_model: 'chromebook',
  serial_number: '777006',
  pending_return: false,
  assignment_date: new Date(2018, 1, 1),
  last_known_healthy: new Date(2018, 1, 1),
  due_date: new Date(2018, 1, 1),
  current_ou: 'ROOT',
  max_extend_date: new Date(2018, 1, 4),
});

export const DEVICE_LOST = new Device({
  device_model: 'chromebook',
  serial_number: '777007',
  assignment_date: new Date(2018, 1, 1),
  last_known_healthy: new Date(2018, 1, 1),
  due_date: new Date(2018, 1, 1),
  current_ou: 'ROOT',
  lost: true,
  locked: true,
});

export const DEVICE_DAMAGED = new Device({
  assigned_user: 'test_user',
  device_model: 'chromebook',
  serial_number: '777008',
  pending_return: false,
  assignment_date: new Date(2018, 1, 1),
  last_known_healthy: new Date(2018, 1, 1),
  due_date: new Date(2018, 1, 1),
  current_ou: 'ROOT',
  damaged: true,
});

export const DEVICE_LOCKED = new Device({
  assigned_user: 'test_user',
  device_model: 'chromebook',
  serial_number: '777009',
  pending_return: false,
  assignment_date: new Date(2018, 1, 1),
  last_known_healthy: new Date(2018, 1, 1),
  due_date: new Date(2018, 1, 1),
  current_ou: 'ROOT',
  locked: true,
});

export const DEVICE_OVERDUE = new Device({
  assigned_user: 'test_user',
  device_model: 'chromebook',
  serial_number: '777009',
  pending_return: false,
  assignment_date: new Date(2018, 1, 1),
  last_known_healthy: new Date(2018, 1, 1),
  due_date: new Date(2018, 1, 3),
  current_ou: 'ROOT',
  max_extend_date: new Date(2018, 1, 4),
});

export const DEVICE_LOST_AND_MORE = new Device({
  device_model: 'chromebook',
  serial_number: '777007',
  assignment_date: new Date(2018, 1, 1),
  last_known_healthy: new Date(2018, 1, 1),
  due_date: new Date(2018, 1, 1),
  current_ou: 'ROOT',
  lost: true,
  damaged: true,
  pending_return: true,
});

export class DeviceServiceMock {
  dataChange = new BehaviorSubject<Device[]>([
    DEVICE_1, DEVICE_2, DEVICE_WITH_ASSET_TAG, DEVICE_WITHOUT_ASSET_TAG,
    DEVICE_MARKED_FOR_RETURN, DEVICE_UNASSIGNED, DEVICE_ASSIGNED, DEVICE_LOST,
    DEVICE_DAMAGED, DEVICE_LOCKED, DEVICE_OVERDUE
  ]);

  create() {
    return;
  }
  get data(): Device[] {
    return this.dataChange.value;
  }
  getResponsiblesForAuditList(): Observable<string[]> {
    return new Observable(observer => {
      observer.next(['one']);
    });
  }

  list(): Observable<ListDevicesResponse> {
    return of({
      devices: this.data,
      totalResults: this.data.length,
      totalPages: 1,
    });
  }

  listUserDevices(): Observable<Device[]> {
    return this.dataChange;
  }

  getDevice(deviceId: string): Observable<Device> {
    const foundDevice = this.dataChange.value.find(mockDevice => {
      return mockDevice.id === deviceId;
    });
    if (foundDevice === undefined) {
      throw new Error(`Could not find device in mock with id ${deviceId}`);
    }
    return of(foundDevice);
  }

  checkReadyForAudit(deviceId: string): Observable<string> {
    return new Observable(observer => {
      const percentage: number = Math.random();
      setTimeout(() => {
        if (percentage > 0.5) {
          observer.next('OH YEAH!');
        } else {
          observer.error('Aw, Loaner-snap!');
        }
      }, 1000);
    });
  }

  extend(id: string) {
    return;
  }

  returnDevice(id: string) {
    return;
  }

  markAsDamaged(id: string) {
    return;
  }

  markAsLost(id: string) {
    return;
  }

  enableGuestMode(id: string) {
    return of(true);
  }

  enroll(newDevice: Device) {
    return;
  }

  unenroll(deviceToBeUnenrolled: Device) {
    return of(true);
  }
}

export class ConfigServiceMock {
  getStringConfig(name: string) {
    return of('');
  }

  getNumberConfig(name: string) {
    return of(0);
  }

  getBooleanConfig(name: string) {
    return of(false);
  }

  getListConfig(name: string) {
    return of([]);
  }

  list() {}

  update(
      name: string, configType: config.ConfigType,
      value: string|number|boolean|string[]) {}
}

export class AuthServiceMock {
  isSignedIn = false;
  token = 'a token';
  loaded = false;

  whenLoaded(): Observable<boolean> {
    return of(true);
  }

  whenSignedIn(): Observable<boolean> {
    return of(true);
  }

  updateSigninStatus(isSignedIn: boolean) {}

  signIn() {}

  signOut() {}
}

export const TEST_USER = new User({
  permissions: [
    CONFIG.appPermissions.ADMINISTRATE_LOAN,
    CONFIG.appPermissions.READ_SHELVES,
    CONFIG.appPermissions.READ_DEVICES,
    CONFIG.appPermissions.MODIFY_DEVICE,
    CONFIG.appPermissions.MODIFY_SHELF,
  ],
});
TEST_USER.email = 'daredevil@example.com';
TEST_USER.givenName = 'Daredevil';

export const TEST_USER_WITHOUT_ADMINISTRATE_LOAN = new User({
  permissions: [
    CONFIG.appPermissions.READ_SHELVES,
    CONFIG.appPermissions.READ_DEVICES,
    CONFIG.appPermissions.MODIFY_DEVICE,
    CONFIG.appPermissions.MODIFY_SHELF,
  ],
});
TEST_USER_WITHOUT_ADMINISTRATE_LOAN.givenName = 'Test User';
TEST_USER_WITHOUT_ADMINISTRATE_LOAN.email = 'test_user@example.com';

export class UserServiceMock {
  user = TEST_USER;

  getRole(): Observable<User> {
    return of(this.user);
  }

  whenUserLoaded(): Observable<User> {
    return of(this.user);
  }

  loadUser(): Observable<User> {
    return of(this.user);
  }
}

export const TEST_SHELF_REQUEST: ShelfRequestParams = {
  location: 'FAKE LOCATION',
  urlsafe_key: 'FAKE_URLSAFE_KEY',
};

export const TEST_SHELF = new Shelf({
  friendly_name: 'FAKE SHELF',
  location: 'FAKE LOCATION',
  capacity: 5,
  responsible_for_audit: 'me',
  shelf_request: TEST_SHELF_REQUEST,
});

export class ActivatedRouteMock {
  get params(): Observable<{[key: string]: {}}> {
    return of({id: 'Location 1'});
  }
}

export class SearchServiceMock {
  searchText: Observable<string> = of('magical');

  changeSearchText(query: string) {
    this.searchText = of(query);
  }

  getHelp(): Observable<string> {
    return of(`# Testing
    ## 123
    ### 456
    Regular text.
    `);
  }
}
