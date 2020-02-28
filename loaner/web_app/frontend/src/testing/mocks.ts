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

import {BehaviorSubject, Observable, Observer, of} from 'rxjs';

import {CONFIG} from '../app.config';
import * as bootstrap from '../models/bootstrap';
import * as config from '../models/config';
import * as template from '../models/template';
import {Device, ListDevicesResponse} from '../models/device';
import {ListRolesResponse, Role} from '../models/role';
import {ListShelfResponse, Shelf, ShelfRequestParams} from '../models/shelf';
import {ListTagRequest, ListTagResponse, Tag} from '../models/tag';
import {Template} from '../models/template';
import {User} from '../models/user';

/* Disabling jsdocs on this file because they do not add much information   */
// tslint:disable:enforce-comments-on-exported-symbols
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
      },
      audit_notification_enabled: true,
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
    return of(new Shelf());
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
      has_additional_results: false,
      page_token: '',
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
    return of({
      'started': true,
      'completed': false,
      'is_update': true,
      'app_version': '0.0.7-alpha',
      'running_version': '0.0.6-alpha',
      'tasks': []
    } as bootstrap.Status);
  }
  getStatus() {
    return new Observable(observer => {
      observer.next({
        'completed': true,
        'is_update': false,
        'app_version': '0.0.7-alpha',
        'running_version': '0.0.7-alpha',
        'tasks': []
      });
    });
  }
}

export const SHELF_CAPACITY_1 = new Shelf({
  friendly_name: 'The smallest shelf',
  location: 'Location 6',
  last_audit_by: 'user',
  capacity: 1,
  last_audit_time: new Date(2018, 1, 1),
  shelf_request: {
    location: 'Location 6',
    urlsafe_key: 'urlsafekey6',
  }
});

export const DEVICE_1 = new Device({
  asset_tag: 'device1',
  device_model: 'chromebook',
  serial_number: '321653',
  identifier: 'device1',
  pending_return: false,
  assignment_date: new Date(2018, 1, 1),
  last_known_healthy: new Date(2018, 1, 1),
  due_date: new Date(2018, 1, 1),
  max_extend_date: new Date(2018, 1, 4),
});

export const DEVICE_2 = new Device({
  asset_tag: 'device2',
  device_model: 'chromebook',
  serial_number: '236135',
  identifier: 'device2',
  pending_return: true,
  assignment_date: new Date(2018, 1, 1),
  last_known_healthy: new Date(2018, 1, 1),
  due_date: new Date(2018, 1, 1),
  max_extend_date: new Date(2018, 1, 4),

});

export const DEVICE_WITH_ASSET_TAG = new Device({
  asset_tag: 'abc',
  device_model: 'chromebook',
  serial_number: '777001',
  identifier: 'abc',
  pending_return: false,
  assignment_date: new Date(2018, 1, 1),
  last_known_healthy: new Date(2018, 1, 1),
  due_date: new Date(2018, 1, 1),
  max_extend_date: new Date(2018, 1, 4),

});

export const DEVICE_WITHOUT_ASSET_TAG = new Device({
  asset_tag: '',
  device_model: 'chromebook',
  serial_number: '777002',
  identifier: '777002',
  pending_return: false,
  assignment_date: new Date(2018, 1, 1),
  last_known_healthy: new Date(2018, 1, 1),
  due_date: new Date(2018, 1, 1),
  max_extend_date: new Date(2018, 1, 4),
});

export const DEVICE_MARKED_FOR_RETURN = new Device({
  asset_tag: '',
  device_model: 'chromebook',
  serial_number: '777003',
  identifier: '777003',
  pending_return: true,
  assignment_date: new Date(2018, 1, 1),
  last_known_healthy: new Date(2018, 1, 1),
  due_date: new Date(2018, 1, 1),
});

export const DEVICE_NOT_MARKED_FOR_RETURN = new Device({
  asset_tag: '',
  device_model: 'chromebook',
  serial_number: '777004',
  identifier: '777004',
  pending_return: false,
  assignment_date: new Date(2018, 1, 1),
  last_known_healthy: new Date(2018, 1, 1),
  due_date: new Date(2018, 1, 1),
  max_extend_date: new Date(2018, 1, 4),
});

export const DEVICE_UNASSIGNED = new Device({
  device_model: 'chromebook',
  serial_number: '777005',
  identifier: '777005',
  pending_return: false,
  due_date: new Date(2018, 1, 1),
});

export const DEVICE_ASSIGNED = new Device({
  assigned_user: 'test_user',
  device_model: 'chromebook',
  serial_number: '777006',
  identifier: '777006',
  pending_return: false,
  assignment_date: new Date(2018, 1, 1),
  last_known_healthy: new Date(2018, 1, 1),
  due_date: new Date(2018, 1, 1),
  max_extend_date: new Date(2018, 1, 4),
  guest_permitted: true,
});

export const DEVICE_GUEST_NOT_PERMITTED = new Device({
  assigned_user: 'test_user',
  device_model: 'chromebook',
  serial_number: '777006',
  identifier: '777006',
  pending_return: false,
  assignment_date: new Date(2018, 1, 1),
  last_known_healthy: new Date(2018, 1, 1),
  due_date: new Date(2018, 1, 1),
  max_extend_date: new Date(2018, 1, 4),
  guest_permitted: false,
});

export const DEVICE_GUEST_PERMITTED = new Device({
  assigned_user: 'test_user',
  device_model: 'chromebook',
  serial_number: '777006',
  identifier: '777006',
  pending_return: false,
  assignment_date: new Date(2018, 1, 1),
  last_known_healthy: new Date(2018, 1, 1),
  due_date: new Date(2018, 1, 1),
  max_extend_date: new Date(2018, 1, 4),
  guest_permitted: true,
});

export const DEVICE_LOST = new Device({
  assigned_user: 'test_user',
  device_model: 'chromebook',
  serial_number: '777007',
  identifier: '777007',
  assignment_date: new Date(2018, 1, 1),
  last_known_healthy: new Date(2018, 1, 1),
  due_date: new Date(2018, 1, 1),
  lost: true,
  locked: true,
});

export const DEVICE_DAMAGED = new Device({
  assigned_user: 'test_user',
  device_model: 'chromebook',
  serial_number: '777008',
  identifier: '777008',
  pending_return: false,
  assignment_date: new Date(2018, 1, 1),
  last_known_healthy: new Date(2018, 1, 1),
  due_date: new Date(2018, 1, 1),
  damaged: true,
  damaged_reason: 'Broken keyboard.',
});

export const DEVICE_LOCKED = new Device({
  assigned_user: 'test_user',
  device_model: 'chromebook',
  serial_number: '777009',
  identifier: '777009',
  pending_return: false,
  assignment_date: new Date(2018, 1, 1),
  last_known_healthy: new Date(2018, 1, 1),
  due_date: new Date(2018, 1, 1),
  locked: true,
});

export const DEVICE_OVERDUE = new Device({
  assigned_user: 'test_user',
  device_model: 'chromebook',
  serial_number: '77700112',
  identifier: '77700112',
  pending_return: false,
  assignment_date: new Date(2018, 1, 1),
  last_known_healthy: new Date(2018, 1, 1),
  due_date: new Date(2017, 4, 4),
  overdue: true,
});

export const DEVICE_LOST_AND_MORE = new Device({
  device_model: 'chromebook',
  serial_number: '777007',
  identifier: '777007',
  assignment_date: new Date(2018, 1, 1),
  last_known_healthy: new Date(2018, 1, 1),
  due_date: new Date(2018, 1, 1),
  lost: true,
  damaged: true,
  pending_return: true,
});

export class DeviceServiceMock {
  dataChange = new BehaviorSubject<Device[]>([
    DEVICE_1,
    DEVICE_2,
    DEVICE_WITH_ASSET_TAG,
    DEVICE_WITHOUT_ASSET_TAG,
    DEVICE_MARKED_FOR_RETURN,
    DEVICE_UNASSIGNED,
    DEVICE_ASSIGNED,
    DEVICE_LOST,
    DEVICE_DAMAGED,
    DEVICE_LOCKED,
    DEVICE_OVERDUE,
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
      has_additional_results: false,
      page_token: '',
    });
  }

  listUserDevices(): Observable<Device[]> {
    return this.dataChange;
  }

  getDevice(deviceId: string): Observable<Device> {
    const foundDevice = this.dataChange.value.find(mockDevice => {
      return mockDevice.identifier === deviceId;
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
    return of();
  }

  markAsLost(id: string) {
    return;
  }

  enableGuestMode(id: string) {
    return of();
  }

  enroll(newDevice: Device) {
    return of();
  }

  unenroll(deviceToBeUnenrolled: Device) {
    return of();
  }
}

export const CONFIG_RESPONSE_MOCK = [
  {boolean_value: false, name: 'shelf_audit_email'},
  {integer_value: '3', name: 'loan_duration'},
  {boolean_value: true, name: 'allow_guest_mode'},
  {name: 'device_identifier_mode', string_value: 'serial_number'},
  {list_value: ['technicians@test.domain'], name: 'responsible_for_audit'},
  {boolean_value: true, name: 'bootstrap_completed'},
  {boolean_value: false, name: 'use_asset_tags'},
  {name: 'unenroll_ou', string_value: '/'},
  {boolean_value: true, name: 'loan_duration_email'},
  {name: 'img_banner_primary', string_value: 'images/testbanner.png'},
  {integer_value: '1000', name: 'sync_roles_user_query_size'},
  {boolean_value: true, name: 'shelf_audit'},
  {integer_value: '24', name: 'audit_interval'},
  {boolean_value: true, name: 'timeout_guest_mode'},
  {boolean_value: true, name: 'bootstrap_started'},
  {list_value: [''], name: 'shelf_audit_email_to'},
  {integer_value: '14', name: 'maximum_loan_duration'},
  {name: 'org_unit_prefix', string_value: ''},
  {integer_value: '12', name: 'guest_mode_timeout_in_hours'},
  {integer_value: '15', name: 'return_grace_period'},
  {name: 'support_contact', string_value: 'File a ticket!'},
  {boolean_value: false, name: 'require_surveys'},
  {integer_value: '1', name: 'reminder_delay'},
  {name: 'img_button_manage', string_value: 'images/testbutton.png'},
  {integer_value: '24', name: 'shelf_audit_interval'},
  {integer_value: '1', name: 'datastore_version'},
  {boolean_value: true, name: 'anonymous_surveys'},
  {boolean_value: false, name: 'silent_onboarding'},
  {boolean_value: false, name: 'enable_backups'},
  {name: 'gcp_cloud_storage_bucket', string_value: 'test_bucket'},
];

export const TEMPLATE_RESPONSE_MOCK = {
  templates: [
    new Template({
      name: 'test_email_template_1',
      body: 'hello world',
      title: 'test_title'
    }),
    new Template({
      name: 'test_email_template_2',
      body: '<html><body>world hello<body/><html/>',
      title: ''
    }),
  ]
};

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

  list() {
    return of(CONFIG_RESPONSE_MOCK);
  }

  updateAll(configUpdates: config.ConfigUpdate[]) {}
}

export class TemplateServiceMock {
  list() {
    return of(TEMPLATE_RESPONSE_MOCK);
  }
  create(templateCreate: template.CreateTemplateRequest) {
    return of();
  }

  remove(templateRemove: template.RemoveTemplateRequest) {
    return of();
  }

  update(templateUpdate: template.TemplateApiParams) {
    return of();
  }
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

export const TEST_USER_SUPERADMIN = new User({
  superadmin: true,
});
TEST_USER.email = 'superadmin@example.com';
TEST_USER.givenName = 'Superadmin';

export const TEST_USER_NO_PERMISSIONS = new User({});
TEST_USER.email = 'nopower@example.com';
TEST_USER.givenName = 'Generic';

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

export const TEST_SHELF_SYSTEM_AUDIT_ENABLED = new Shelf({
  friendly_name: 'SYSTEM AUDIT SHELF',
  location: 'FAKE LOCATION',
  capacity: 5,
  responsible_for_audit: 'me',
  audit_enabled: true,
  audit_notification_enabled: true,
});

export const TEST_SHELF_SYSTEM_AUDIT_DISABLED = new Shelf({
  friendly_name: 'SHELF AUDIT SHELF',
  location: 'FAKE LOCATION',
  capacity: 5,
  responsible_for_audit: 'me',
  audit_enabled: false,
  audit_notification_enabled: true,
});

export const TEST_SHELF_AUDIT_DISABLED = new Shelf({
  friendly_name: 'SYSTEM AUDIT SHELF',
  location: 'FAKE LOCATION',
  capacity: 5,
  responsible_for_audit: 'me',
  audit_enabled: true,
  audit_notification_enabled: false,
});
/** A class which mocks TagService calls without making any HTTP calls. */
export class TagServiceMock {
  tags: Tag[];

  constructor() {
    this.tags = [
      new Tag({
        name: '1',
        hidden: false,
        color: 'purple',
        protect: false,
        description: 'Devices reserved for executives'
      }),
      new Tag({
        name: '2',
        hidden: false,
        color: 'green',
        protect: false,
        description: 'Tag for chromebook used only for the Business Unit shelf'
      }),
      new Tag({
        name: '3',
        hidden: false,
        color: 'orange',
        protect: true,
        description: 'Security vulnerability update required'
      }),
      new Tag({
        name: '4',
        hidden: false,
        color: 'purple',
        protect: false,
        description: 'Devices reserved for executives'
      }),
      new Tag({
        name: '5',
        hidden: false,
        color: 'green',
        protect: false,
        description: 'Tag for chromebook used only for the Business Unit shelf'
      }),
      new Tag({
        name: '6',
        hidden: false,
        color: 'orange',
        protect: true,
        description: 'Security vulnerability update required'
      }),
      new Tag({
        name: '7',
        hidden: false,
        color: 'purple',
        protect: false,
        description: 'Devices reserved for executives'
      }),
      new Tag({
        name: '8',
        hidden: true,
        color: 'green',
        protect: false,
        description: 'Tag for chromebook used only for the Business Unit shelf'
      }),
      new Tag({
        name: '9',
        hidden: true,
        color: 'orange',
        protect: true,
        description: 'Security vulnerability update required'
      }),
      new Tag({
        name: '10',
        hidden: true,
        color: 'purple',
        protect: false,
        description: 'Devices reserved for executives'
      }),
      new Tag({
        name: '11',
        hidden: true,
        color: 'green',
        protect: false,
        description: 'Tag for chromebook used only for the Business Unit shelf'
      }),
      new Tag({
        name: '12',
        hidden: true,
        color: 'orange',
        protect: true,
        description: 'Security vulnerability update required'
      }),
      new Tag({
        name: '13',
        hidden: true,
        color: 'purple',
        protect: false,
        description: 'Devices reserved for executives'
      }),
      new Tag({
        name: '14',
        hidden: true,
        color: 'green',
        protect: false,
        description: 'Tag for chromebook used only for the Business Unit shelf'
      }),
      new Tag({
        name: '15',
        hidden: false,
        color: 'orange',
        protect: true,
        description: 'Security vulnerability update required'
      }),
      new Tag({
        name: '16',
        hidden: false,
        color: 'purple',
        protect: false,
        description: 'Devices reserved for executives'
      }),
      new Tag({
        name: '17',
        hidden: false,
        color: 'green',
        protect: false,
        description: 'Tag for chromebook used only for the Business Unit shelf'
      }),
      new Tag({
        name: '18',
        hidden: false,
        color: 'orange',
        protect: true,
        description: 'Security vulnerability update required'
      })
    ];

    this.tags.forEach(tag => {
      tag.urlSafeKey = this.urlSafeKeyGenerator();
    });
  }

  create(createTag: Tag) {
    return new Observable<boolean>((observer: Observer<boolean>) => {
      if (createTag.name === '') {
        observer.error(false);
        observer.complete();
      } else if (this.tags.find((tag) => tag.name === createTag.name)) {
        observer.error(new Error('A tag with this name already exists'));
      } else {
        createTag.urlSafeKey = this.urlSafeKeyGenerator();
        this.tags.push(createTag);
        observer.next(true);
      }
      observer.complete();
    });
  }

  destroy(destroyTag: Tag) {
    return new Observable<boolean>((observer: Observer<boolean>) => {
      const deleteIndex = this.tags.findIndex(
          (tag) => tag.urlSafeKey === destroyTag.urlSafeKey);
      if (deleteIndex > -1) {
        this.tags.splice(deleteIndex, 1);
        observer.next(true);
      } else {
        observer.error(new Error(
            `No Tag found with urlSafeKey: ${destroyTag.urlSafeKey}`));
      }
      observer.complete();
    });
  }

  update(updateTag: Tag) {
    return new Observable<boolean>((observer: Observer<boolean>) => {
      const updateIndex =
          this.tags.findIndex((tag) => tag.urlSafeKey === updateTag.urlSafeKey);
      if (updateIndex > -1) {
        this.tags.splice(updateIndex, 1, updateTag);
        observer.next(true);
      } else {
        observer.error(new Error(`No Tag found for: ${updateTag.name}`));
      }
      observer.complete();
    });
  }

  list(params: ListTagRequest = {
    page_size: 5,
    page_index: 1,
    include_hidden_tags: false
  }): Observable<ListTagResponse> {
    return new Observable<
        ListTagResponse>((observer: Observer<ListTagResponse>) => {
      const response: ListTagResponse =
          {total_pages: 0, has_additional_results: false, tags: [], cursor: ''};
      if (params.page_size && params.page_size <= 0) {
        observer.error(new Error(`Invalid page_size: ${params.page_size}`));
      } else if (params.page_size && params.page_index) {
        let filteredTags = this.tags;
        if (params.include_hidden_tags === false) {
          filteredTags = this.tags.filter(tag => {
            return !tag.hidden;
          });
        }
        response.total_pages =
            Math.ceil(filteredTags.length / params.page_size);
        const startIndex = (params.page_index - 1) * params.page_size;
        response.tags = filteredTags.slice(
            startIndex, params.page_size * params.page_index);
        response.has_additional_results =
            (response.total_pages > params.page_index) ? true : false;
        observer.next(response);
      }
      observer.complete();
    });
  }

  urlSafeKeyGenerator(): string {
    let key = Math.floor(Math.random() * 10000).toString();
    while (!this.tags.every(tag => tag.urlSafeKey !== key)) {
      key = Math.floor(Math.random() * 10000).toString();
    }
    return key;
  }
}

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

  reindex(searchType: string) {
    return of();
  }

  clearIndex(searchType: string) {
    return of();
  }
}

export class RoleServiceMock {
  dataChange = new BehaviorSubject<Role[]>([
    new Role({
      name: 'Role 1',
      associated_group: 'Role Group 1',
      permissions: ['permission1', 'permissions2', 'permissions3'],
    }),
    new Role({
      name: 'Role 2',
      associated_group: 'Role Group 2',
      permissions: ['permission1', 'permissions2', 'permissions3'],
    }),
    new Role({
      name: 'Role 3',
      associated_group: 'Role Group 3',
      permissions: ['permission1', 'permissions2', 'permissions3'],
    }),
  ]);

  create(role: Role) {
    return of();
  }

  getRole(role: Role) {
    return this.dataChange.value;
  }

  update(role: Role) {
    return of();
  }

  list() {
    return of(this.dataChange);
  }

  delete(role: Role) {
    return of();
  }
}

export const TEST_ROLE_1 = new Role({
  name: 'FAKE ROLE 1',
  associated_group: 'FAKE GROUP 1',
  permissions: ['fake_permission1', 'fake_permission2', 'fake_permission3'],
});

export const TEST_ROLE_2 = new Role({
  name: 'FAKE ROLE 2',
  associated_group: 'FAKE GROUP 2',
  permissions: ['fake_permission3', 'fake_permission4'],
});

export const SET_OF_ROLES: ListRolesResponse = {
  roles: [TEST_ROLE_1, TEST_ROLE_2],
};
