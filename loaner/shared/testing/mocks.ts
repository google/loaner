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

import {Injectable, NgModule} from '@angular/core';
import {ComponentFixtureAutoDetect} from '@angular/core/testing';
import {BehaviorSubject, Observable, of} from 'rxjs';

import {Damaged} from '../components/damaged';
import {Extend} from '../components/extend';
import {GuestMode} from '../components/guest';
import {Lost} from '../components/lost';
import {Unenroll} from '../components/unenroll';

import {Device} from '../models/device';

export const DEVICE = new Device({
  asset_tag: 'asset',
  serial_number: 'serial',
  identifier: 'asset',
  assigned_user: 'daredevil@example.com',
  due_date: new Date(2018, 1, 1),
  max_extend_date: new Date(2018, 1, 3),
  pending_return: false,
  guest_permitted: true,
  guest_enabled: false,
});

export abstract class DeviceActionsDialogService {
  openDialog() {}

  finished() {}

  close() {}
}

export class DamagedMock extends DeviceActionsDialogService {
  get onDamaged(): Observable<string> {
    return of('damagedReason');
  }
  get overdue(): boolean {
    return true;
  }
}

export class ExtendMock extends DeviceActionsDialogService {
  get onExtended(): Observable<string> {
    return of('newDate');
  }
}

export class GuestModeMock extends DeviceActionsDialogService {
  get onGuestModeEnabled(): Observable<boolean> {
    return of(true);
  }
}

export class ResumeLoanMock extends DeviceActionsDialogService {
  get onLoanResumed(): Observable<boolean> {
    return of(true);
  }
}

export class LostMock extends DeviceActionsDialogService {
  get onLost(): Observable<boolean> {
    return of(true);
  }
}

export class UnenrollMock extends DeviceActionsDialogService {
  get onUnenroll(): Observable<boolean> {
    return of(true);
  }
}

@NgModule({
  providers: [
    {provide: ComponentFixtureAutoDetect, useValue: true},
    {provide: Damaged, useClass: DamagedMock},
    {provide: Extend, useClass: ExtendMock},
    {provide: GuestMode, useClass: GuestModeMock},
    {provide: Lost, useClass: LostMock},
    {provide: Unenroll, useClass: UnenrollMock},
  ],
})
export class SharedMocksModule {
}

/** Mock of service to interact with the animation menu between components. */
@Injectable()
export class AnimationMenuServiceMock {
  playbackRate = new BehaviorSubject<number>(100);

  /**
   * Set the animation speed in Chrome Storage.
   * @param value The value to store for animationSpeed in Chrome Storage.
   */
  setAnimationSpeed(value: number) {
    this.playbackRate.next(value);
  }

  /** Gets the animation speed. */
  getAnimationSpeed(): Observable<number> {
    return this.playbackRate.asObservable();
  }
}
