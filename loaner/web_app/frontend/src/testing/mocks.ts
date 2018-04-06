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
import {Device} from '../models/device';
import {Shelf} from '../models/shelf';
import {User} from '../models/user';


export class ShelfServiceMock {
  dataChange = new BehaviorSubject<Shelf[]>([
    new Shelf({
      friendly_name: 'Friendly name 1',
      location: 'Location 1',
      last_audit_by: 'user',
      capacity: 10,
      last_audit_time: 1499202031707,
    }),
    new Shelf({
      friendly_name: 'Friendly name 2',
      location: 'Location 2',
      last_audit_by: 'user',
      capacity: 10,
      last_audit_time: 1499202031707,
    }),
    new Shelf({
      friendly_name: 'Friendly name 3',
      location: 'Location 3',
      last_audit_by: 'user',
      capacity: 10,
      last_audit_time: 1499202031707,
    }),
    new Shelf({
      friendly_name: 'Friendly name 4',
      location: 'Location 4',
      last_audit_by: 'user',
      capacity: 10,
      last_audit_time: 1499202031707,
    }),
    new Shelf({
      friendly_name: 'Friendly name 5',
      location: 'Location 5',
      last_audit_by: 'user',
      capacity: 10,
      last_audit_time: 1499202031707,
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

  list(): Observable<Shelf[]> {
    return this.dataChange;
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

export const TEST_DEVICE_1 = new Device({
  asset_tag: 'device1',
  device_model: 'chromebook',
  serial_number: '321653',
  pending_return: false,
  assigned_on_date: 1499202031707,
  last_update: 1499202031707,
  due_date: 1499202031707,
  current_ou: 'ROOT',
  max_extend_date: 1499400000000,
});

export const TEST_DEVICE_2 = new Device({
  asset_tag: 'device2',
  device_model: 'chromebook',
  serial_number: '236135',
  pending_return: true,
  assigned_on_date: 1499202031707,
  last_update: 1499202031707,
  due_date: 1499202031707,
  current_ou: 'ROOT',
  max_extend_date: 1499400000000,

});

export const TEST_DEVICE_WITH_ASSET_TAG = new Device({
  asset_tag: 'abc',
  device_model: 'chromebook',
  serial_number: '777001',
  pending_return: false,
  assigned_on_date: 1499202031707,
  last_update: 1499202031707,
  due_date: 1499202031707,
  current_ou: 'ROOT',
  max_extend_date: 1499400000000,

});

export const TEST_DEVICE_WITHOUT_ASSET_TAG = new Device({
  asset_tag: '',
  device_model: 'chromebook',
  serial_number: '777002',
  pending_return: false,
  assigned_on_date: 1499202031707,
  last_update: 1499202031707,
  due_date: 1499202031707,
  current_ou: 'ROOT',
  max_extend_date: 1499400000000,
});

export const TEST_DEVICE_MARKED_FOR_RETURN = new Device({
  asset_tag: '',
  device_model: 'chromebook',
  serial_number: '777003',
  pending_return: true,
  assigned_on_date: 1499202031707,
  last_update: 1499202031707,
  due_date: 1499202031707,
  current_ou: 'ROOT',
});

export const TEST_DEVICE_NOT_MARKED_FOR_RETURN = new Device({
  asset_tag: '',
  device_model: 'chromebook',
  serial_number: '777004',
  pending_return: false,
  assigned_on_date: 1499202031707,
  last_update: 1499202031707,
  due_date: 1499202031707,
  current_ou: 'ROOT',
  max_extend_date: 1499400000000,
});

export const TEST_DEVICE_UNASSIGNED = new Device({
  device_model: 'chromebook',
  serial_number: '777005',
  pending_return: false,
  due_date: 1499202031707,
  current_ou: 'ROOT',
});

export const TEST_DEVICE_ASSIGNED = new Device({
  assigned_user: 'test_user',
  device_model: 'chromebook',
  serial_number: '777006',
  pending_return: false,
  assigned_on_date: 1499202031707,
  last_update: 1499202031707,
  due_date: 1499202031707,
  current_ou: 'ROOT',
  max_extend_date: 1499400000000,
});

export const TEST_DEVICE_LOST = new Device({
  device_model: 'chromebook',
  serial_number: '777007',
  assigned_on_date: 1499202031707,
  last_update: 1499202031707,
  due_date: 1499202031707,
  current_ou: 'ROOT',
  lost: true,
});

export const TEST_DEVICE_DAMAGED = new Device({
  assigned_user: 'test_user',
  device_model: 'chromebook',
  serial_number: '777008',
  pending_return: false,
  assigned_on_date: 1499202031707,
  last_update: 1499202031707,
  due_date: 1499202031707,
  current_ou: 'ROOT',
  damaged: true,
});

export const TEST_DEVICE_LOCKED = new Device({
  assigned_user: 'test_user',
  device_model: 'chromebook',
  serial_number: '777009',
  pending_return: false,
  assigned_on_date: 1499202031707,
  last_update: 1499202031707,
  due_date: 1499202031707,
  current_ou: 'ROOT',
  locked: true,
});

export const TEST_DEVICE_OVERDUE = new Device({
  assigned_user: 'test_user',
  device_model: 'chromebook',
  serial_number: '777009',
  pending_return: false,
  assigned_on_date: 1499202031707,
  last_update: 1499202031707,
  due_date: 0,
  current_ou: 'ROOT',
  max_extend_date: 1499400000000,
});

export class DeviceServiceMock {
  dataChange = new BehaviorSubject<Device[]>([
    TEST_DEVICE_1, TEST_DEVICE_2, TEST_DEVICE_WITH_ASSET_TAG,
    TEST_DEVICE_WITHOUT_ASSET_TAG
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

  list(): Observable<Device[]> {
    return this.dataChange;
  }

  listUserDevices(): Observable<Device[]> {
    return this.dataChange;
  }

  getDevice(deviceId: string): Observable<Device> {
    return of (this.data[0]);
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
    return of (true);
  }

  enroll(newDevice: Device) {
    return;
  }

  unenroll(deviceToBeUnenrolled: Device) {
    return of(true);
  }
}

export class ConfigServiceMock {
  getConfig(name: string, configType: config.ConfigType) {
    return new Observable(observer => {
      observer.next({});
    });
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
    return of (true);
  }

  whenSignedIn(): Observable<boolean> {
    return of (true);
  }

  updateSigninStatus(isSignedIn: boolean) {}

  signIn() {}

  signOut() {}
}

export const TEST_USER = new User({
  roles: [
    CONFIG.roles.USER,
    CONFIG.roles.TECHNICIAN,
    CONFIG.roles.TECHNICAL_ADMIN,
    CONFIG.roles.OPERATIONAL_ADMIN,
  ],
});
TEST_USER.email = 'daredevil@example.com';
TEST_USER.givenName = 'Daredevil';

export class UserServiceMock {
  user = TEST_USER;

  getRole(): Observable<User> {
    return of (this.user);
  }

  whenUserLoaded(): Observable<User> {
    return of (this.user);
  }

  loadUser(): Observable<User> {
    return of (this.user);
  }
}

export const TEST_SHELF = new Shelf({
  friendly_name: 'FAKE SHELF',
  location: 'FAKE LOCATION',
  capacity: 5,
  responsible_for_audit: 'me',
});

export class ActivatedRouteMock {
  get params(): Observable<{[key: string]: {}}> {
    return of ({id: 'Location 1'});
  }
}
