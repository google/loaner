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

import * as moment from 'moment';


import {Device} from './device';

describe('Device', () => {
  const today: Date = moment()
                          .set({
                            hour: 0,
                            minute: 0,
                            second: 0,
                          })
                          .toDate();
  const underdueDevice = new Device({
    serial_number: 'fakeserial1',
    assigned_user: 'fakeuser1',
    device_model: 'fakemodel1',
    due_date: moment(today).add(1, 'w').toDate(),
    overdue: false,
  });
  const overdueDevice = new Device({
    serial_number: 'fakeserial2',
    assigned_user: 'fakeuser2',
    device_model: 'fakemodel2',
    due_date: moment(today).subtract(1, 'w').toDate(),
    overdue: true,
  });
  const pendingReturnDevice =
      new Device({serial_number: '789', pending_return: true});
  const maximumExtendedDevice = new Device({
    serial_number: '012',
    pending_return: false,
    due_date: moment(today).toDate(),
    max_extend_date: moment(today).toDate()
  });

  it('returns a value < 0 when a device is overdue', () => {
    expect(overdueDevice.timeUntilDue).toBeLessThan(0);
  });

  it('returns a value >= 0 when a device is underdue', () => {
    expect(underdueDevice.timeUntilDue).toBeGreaterThanOrEqual(0);
  });

  it('isn\'t able to extend if marked pending return', () => {
    expect(pendingReturnDevice.canExtend).toBe(false);
  });

  it('isn\'t able to extend if due date exceeds maximum return date', () => {
    expect(maximumExtendedDevice.canExtend).toBe(false);
    maximumExtendedDevice.maxExtendDate = moment(today).add(1, 'd').toDate();
    expect(maximumExtendedDevice.canExtend).toBe(true);
  });
});
