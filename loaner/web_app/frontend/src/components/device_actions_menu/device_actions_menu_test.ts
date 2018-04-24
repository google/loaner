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
import {ComponentFixture, ComponentFixtureAutoDetect, fakeAsync, flushMicrotasks, TestBed, tick} from '@angular/core/testing';
import {By} from '@angular/platform-browser';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {RouterTestingModule} from '@angular/router/testing';
import {of} from 'rxjs';

import {Damaged} from '../../../../../shared/components/damaged';
import {Extend} from '../../../../../shared/components/extend';
import {GuestMode} from '../../../../../shared/components/guest';
import {Lost} from '../../../../../shared/components/lost';
import {Unenroll} from '../../../../../shared/components/unenroll';
import {SharedMocksModule} from '../../../../../shared/testing/mocks';
import {DeviceService} from '../../services/device';
import {DeviceServiceMock, TEST_DEVICE_1} from '../../testing/mocks';

import {DeviceActionsMenu, DeviceActionsMenuModule} from '.';

@Component({
  preserveWhitespaces: true,
  template: `
    <loaner-device-actions-menu [device]="testDevice">
    </loaner-device-actions-menu>`,
})
class DummyComponent {
  testDevice = TEST_DEVICE_1;
}

describe('DeviceActionsMenu', () => {
  let fixture: ComponentFixture<DummyComponent>;
  let deviceActionsMenu: DeviceActionsMenu;

  beforeEach(fakeAsync(() => {
    TestBed
        .configureTestingModule({
          declarations: [DummyComponent],
          imports: [
            RouterTestingModule,
            DeviceActionsMenuModule,
            BrowserAnimationsModule,
            SharedMocksModule,
          ],
          providers: [
            {provide: DeviceService, useClass: DeviceServiceMock},
          ],
        })
        .compileComponents();

    flushMicrotasks();

    fixture = TestBed.createComponent(DummyComponent);
    deviceActionsMenu = fixture.debugElement.componentInstance;
  }));

  it('creates the DeviceActionsMenu', () => {
    expect(DummyComponent).toBeTruthy();
  });

  it('renders the Extend button after more is clicked', () => {
    fixture.detectChanges();
    const actionsButton = fixture.debugElement.query(By.css('.icon-more'));
    actionsButton.triggerEventHandler('click', null);
    fixture.detectChanges();
    const button = fixture.debugElement.query(By.css('.actions-menu'))
                       .query(By.css('.button-extend'))
                       .nativeElement as HTMLElement;
    expect(button.textContent).toContain('Extend');
  });

  it('renders the Return button after more is clicked', () => {
    fixture.detectChanges();
    const actionsButton = fixture.debugElement.query(By.css('.icon-more'));
    actionsButton.triggerEventHandler('click', null);
    fixture.detectChanges();
    const button = fixture.debugElement.query(By.css('.actions-menu'))
                       .query(By.css('.button-return'))
                       .nativeElement as HTMLElement;
    expect(button.textContent).toContain('Return');
  });

  it('renders the Enable guest button after more is clicked', () => {
    fixture.detectChanges();
    const actionsButton = fixture.debugElement.query(By.css('.icon-more'));
    actionsButton.triggerEventHandler('click', null);
    fixture.detectChanges();
    const button = fixture.debugElement.query(By.css('.actions-menu'))
                       .query(By.css('.button-guest'))
                       .nativeElement as HTMLElement;
    expect(button.textContent).toContain('Enable guest');
  });

  it('renders the Damaged button after more is clicked', () => {
    fixture.detectChanges();
    const actionsButton = fixture.debugElement.query(By.css('.icon-more'));
    actionsButton.triggerEventHandler('click', null);
    fixture.detectChanges();
    const button = fixture.debugElement.query(By.css('.actions-menu'))
                       .query(By.css('.button-damaged'))
                       .nativeElement as HTMLElement;
    expect(button.textContent).toContain('Mark as damaged');
  });

  it('renders the Lost button after more is clicked', () => {
    fixture.detectChanges();
    const actionsButton = fixture.debugElement.query(By.css('.icon-more'));
    actionsButton.triggerEventHandler('click', null);
    fixture.detectChanges();
    const button = fixture.debugElement.query(By.css('.actions-menu'))
                       .query(By.css('.button-lost'))
                       .nativeElement as HTMLElement;
    expect(button.textContent).toContain('Mark as lost');
  });

  it('renders the Unenroll button after more is clicked', () => {
    fixture.detectChanges();
    const actionsButton = fixture.debugElement.query(By.css('.icon-more'));
    actionsButton.triggerEventHandler('click', null);
    fixture.detectChanges();
    const button = fixture.debugElement.query(By.css('.actions-menu'))
                       .query(By.css('.button-unenroll'))
                       .nativeElement as HTMLElement;
    expect(button.textContent).toContain('Unenroll');
  });

  it('calls DeviceService extend when Extend is clicked.', () => {
    const deviceService: DeviceService = TestBed.get(DeviceService);
    const extendService: Extend = TestBed.get(Extend);
    spyOn(deviceService, 'extend');
    const actionsButton = fixture.debugElement.query(By.css('.icon-more'));
    actionsButton.triggerEventHandler('click', null);
    fixture.detectChanges();
    const button = fixture.debugElement.query(By.css('.actions-menu'))
                       .query(By.css('.button-extend'));
    button.triggerEventHandler('click', null);
    fakeAsync(() => {
      extendService.openDialog(
          TEST_DEVICE_1.dueDate, TEST_DEVICE_1.maxExtendDate);
      tick(500);
      flushMicrotasks();
      tick(500);
      fixture.detectChanges();
      expect(deviceService.extend).toHaveBeenCalled();
    });
  });

  it('calls returnDevice when Return is clicked.', () => {
    const deviceService: DeviceService = TestBed.get(DeviceService);
    spyOn(deviceService, 'returnDevice');
    const actionsButton = fixture.debugElement.query(By.css('.icon-more'));
    actionsButton.triggerEventHandler('click', null);
    fixture.detectChanges();
    const button = fixture.debugElement.query(By.css('.actions-menu'))
                       .query(By.css('.button-return'));
    button.triggerEventHandler('click', null);
    fixture.detectChanges();
    expect(deviceService.returnDevice).toHaveBeenCalled();
  });

  it('calls onGuestModeEnabled when Enable guest is clicked.', () => {
    const guestModeService: GuestMode = TestBed.get(GuestMode);
    spyOn(guestModeService, 'onGuestModeEnabled');
    const actionsButton = fixture.debugElement.query(By.css('.icon-more'));
    actionsButton.triggerEventHandler('click', null);
    fixture.detectChanges();
    const button = fixture.debugElement.query(By.css('.actions-menu'))
                       .query(By.css('.button-extend'));
    button.triggerEventHandler('click', null);
    fakeAsync(() => {
      guestModeService.openDialog();
      tick(500);
      flushMicrotasks();
      tick(500);
      fixture.detectChanges();
      expect(guestModeService.onGuestModeEnabled).toHaveBeenCalled();
    });
  });

  it('calls onDamaged when Mark as damaged is clicked.', () => {
    const damagedService: Damaged = TestBed.get(Damaged);
    spyOn(damagedService, 'onDamaged');
    const actionsButton = fixture.debugElement.query(By.css('.icon-more'));
    actionsButton.triggerEventHandler('click', null);
    fixture.detectChanges();
    const button = fixture.debugElement.query(By.css('.actions-menu'))
                       .query(By.css('.button-extend'));
    button.triggerEventHandler('click', null);
    fakeAsync(() => {
      damagedService.openDialog();
      tick(500);
      flushMicrotasks();
      tick(500);
      fixture.detectChanges();
      expect(damagedService.onDamaged).toHaveBeenCalled();
    });
  });

  it('calls onLost when Mark as lost is clicked.', () => {
    const lostService: Lost = TestBed.get(Lost);
    spyOn(lostService, 'onLost');
    const actionsButton = fixture.debugElement.query(By.css('.icon-more'));
    actionsButton.triggerEventHandler('click', null);
    fixture.detectChanges();
    const button = fixture.debugElement.query(By.css('.actions-menu'))
                       .query(By.css('.button-extend'));
    button.triggerEventHandler('click', null);
    fakeAsync(() => {
      lostService.openDialog();
      tick(500);
      flushMicrotasks();
      tick(500);
      fixture.detectChanges();
      expect(lostService.onLost).toHaveBeenCalled();
    });
  });

  it('calls onUnenroll when Unenroll is clicked.', () => {
    const unenrollService: Unenroll = TestBed.get(Unenroll);
    spyOn(unenrollService, 'onUnenroll');
    const actionsButton = fixture.debugElement.query(By.css('.icon-more'));
    actionsButton.triggerEventHandler('click', null);
    fixture.detectChanges();
    const button = fixture.debugElement.query(By.css('.actions-menu'))
                       .query(By.css('.button-extend'));
    button.triggerEventHandler('click', null);
    fakeAsync(() => {
      unenrollService.openDialog('123');
      tick(500);
      flushMicrotasks();
      tick(500);
      fixture.detectChanges();
      expect(unenrollService.onUnenroll).toHaveBeenCalled();
    });
  });
});
