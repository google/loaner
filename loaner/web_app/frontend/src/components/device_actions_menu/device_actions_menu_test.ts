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

import {OverlayContainer} from '@angular/cdk/overlay';
import {Component} from '@angular/core';
import {ComponentFixture, fakeAsync, flushMicrotasks, TestBed, tick} from '@angular/core/testing';
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
import {DEVICE_1, DEVICE_ASSIGNED, DEVICE_DAMAGED, DEVICE_GUEST_NOT_PERMITTED, DEVICE_GUEST_PERMITTED, DEVICE_LOST, DEVICE_OVERDUE, DeviceServiceMock} from '../../testing/mocks';

import {DeviceActionsMenu, DeviceActionsMenuModule} from '.';

@Component({
  template: `
    <loaner-device-actions-menu [device]="testDevice">
    </loaner-device-actions-menu>`,
})
class DummyComponent {
  testDevice = DEVICE_1;
}

describe('DeviceActionsMenu', () => {
  let fixture: ComponentFixture<DummyComponent>;
  let deviceActionsMenu: DeviceActionsMenu;
  let dummyComponent: DummyComponent;
  let overlayContainerElement: HTMLElement;
  let compiled: HTMLElement;

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
    dummyComponent = fixture.debugElement.componentInstance;
    deviceActionsMenu =
        fixture.debugElement.query(By.directive(DeviceActionsMenu))
            .componentInstance;
    compiled = fixture.debugElement.nativeElement;
    overlayContainerElement =
        TestBed.get(OverlayContainer).getContainerElement();
  }));

  // Fake the jasmine clock to allow for extension.
  beforeEach(() => {
    jasmine.clock().mockDate(new Date(2018, 1, 2));
  });

  // Clean up the Jasmine clock mocks.
  afterEach(() => {
    jasmine.clock().uninstall();
  });

  it('creates the DeviceActionsMenu', () => {
    expect(DummyComponent).toBeTruthy();
  });

  it('renders the Extend button after more is clicked', () => {
    dummyComponent.testDevice = DEVICE_ASSIGNED;
    fixture.detectChanges();
    const actionsButton = compiled.querySelector('.icon-more') as HTMLElement;
    actionsButton.click();
    fixture.detectChanges();
    const button = overlayContainerElement.querySelector(
                       '.actions-menu .button-extend') as HTMLElement;
    expect(button.textContent).toContain('Extend');
    expect(button.getAttribute('disabled')).toBeFalsy();
  });

  it('renders the Extend button, but DISABLED after "more" is clicked', () => {
    dummyComponent.testDevice = DEVICE_OVERDUE;
    fixture.detectChanges();
    const actionsButton = compiled.querySelector('.icon-more') as HTMLElement;
    actionsButton.click();
    fixture.detectChanges();
    const button = overlayContainerElement.querySelector(
                       '.actions-menu .button-extend') as HTMLElement;
    expect(button.textContent).toContain('Extend');
    expect(button.getAttribute('disabled')).toBe('true');
  });

  it('renders the Return button after more is clicked', () => {
    fixture.detectChanges();
    const actionsButton = compiled.querySelector('.icon-more') as HTMLElement;
    actionsButton.click();
    fixture.detectChanges();
    const button = overlayContainerElement.querySelector(
                       '.actions-menu .button-return') as HTMLElement;
    expect(button.textContent).toContain('Return');
  });

  it('renders the Enable guest button after more is clicked', () => {
    fixture.detectChanges();
    const actionsButton = compiled.querySelector('.icon-more') as HTMLElement;
    actionsButton.click();
    fixture.detectChanges();
    const button = overlayContainerElement.querySelector(
                       '.actions-menu .button-guest') as HTMLElement;
    expect(button.textContent).toContain('Enable guest');
  });

  it('renders the Damaged button after more is clicked', () => {
    fixture.detectChanges();
    const actionsButton = compiled.querySelector('.icon-more') as HTMLElement;
    actionsButton.click();
    fixture.detectChanges();
    const button = overlayContainerElement.querySelector(
                       '.actions-menu .button-damaged') as HTMLElement;
    expect(button.textContent).toContain('Mark as damaged');
  });

  it('renders the Lost button after more is clicked', () => {
    fixture.detectChanges();
    const actionsButton = compiled.querySelector('.icon-more') as HTMLElement;
    actionsButton.click();
    fixture.detectChanges();
    const button = overlayContainerElement.querySelector(
                       '.actions-menu .button-lost') as HTMLElement;
    expect(button.textContent).toContain('Mark as lost');
  });

  it('renders the Mark as Repaired button after more is clicked', () => {
    dummyComponent.testDevice = DEVICE_DAMAGED;
    fixture.detectChanges();
    const actionsButton = compiled.querySelector('.icon-more') as HTMLElement;
    actionsButton.click();
    fixture.detectChanges();
    const button = overlayContainerElement.querySelector(
                       '.actions-menu .button-undamaged') as HTMLElement;
    expect(button.textContent).toContain('Mark as Repaired');
  });

  it('renders the Unlock button after more is clicked', () => {
    dummyComponent.testDevice = DEVICE_LOST;
    const actionsButton = compiled.querySelector('.icon-more') as HTMLElement;
    actionsButton.click();
    fixture.detectChanges();
    const button = overlayContainerElement.querySelector(
                       '.actions-menu .button-unlock') as HTMLElement;
    expect(button.textContent).toContain('Unlock');
  });

  it('renders a disabled Enable Guest button after more is clicked', () => {
    dummyComponent.testDevice = DEVICE_GUEST_NOT_PERMITTED;
    fixture.detectChanges();
    const actionsButton = compiled.querySelector('.icon-more') as HTMLElement;
    actionsButton.click();
    fixture.detectChanges();
    const button = overlayContainerElement.querySelector(
                       '.actions-menu .button-guest') as HTMLElement;
    expect(button.getAttribute('disabled')).toBe('true');
  });

  it('renders an enabled Enable Guest button after more is clicked', () => {
    dummyComponent.testDevice = DEVICE_GUEST_PERMITTED;
    fixture.detectChanges();
    const actionsButton = compiled.querySelector('.icon-more') as HTMLElement;
    actionsButton.click();
    fixture.detectChanges();
    const button = overlayContainerElement.querySelector(
                       '.actions-menu .button-guest') as HTMLElement;
    expect(button.getAttribute('disabled')).toBeFalsy();
  });


  it('renders the Unenroll button after more is clicked', () => {
    fixture.detectChanges();
    const actionsButton = compiled.querySelector('.icon-more') as HTMLElement;
    actionsButton.click();
    fixture.detectChanges();
    const button = overlayContainerElement.querySelector(
                       '.actions-menu .button-unenroll') as HTMLElement;
    expect(button.textContent).toContain('Unenroll');
  });

  it('calls extend when extend button is clicked and emits refresh event.',
     () => {
       dummyComponent.testDevice = DEVICE_ASSIGNED;
       const deviceService: DeviceService = TestBed.get(DeviceService);
       spyOn(deviceService, 'extend').and.returnValue(of(true));
       spyOn(deviceActionsMenu.refreshDevice, 'emit');
       fixture.detectChanges();
       const actionsButton =
           compiled.querySelector('.icon-more') as HTMLElement;
       actionsButton.click();
       fixture.detectChanges();
       const button = overlayContainerElement.querySelector(
                          '.actions-menu .button-extend') as HTMLElement;
       button.click();
       fixture.detectChanges();
       expect(deviceService.extend).toHaveBeenCalled();
       expect(deviceActionsMenu.refreshDevice.emit).toHaveBeenCalled();
     });

  it('calls returnDevice when Return is clicked and emits refresh event.',
     () => {
       dummyComponent.testDevice = DEVICE_ASSIGNED;
       const deviceService: DeviceService = TestBed.get(DeviceService);
       spyOn(deviceService, 'returnDevice').and.returnValue(of(true));
       spyOn(deviceActionsMenu.refreshDevice, 'emit');
       fixture.detectChanges();
       const actionsButton =
           compiled.querySelector('.icon-more') as HTMLElement;
       actionsButton.click();
       fixture.detectChanges();
       const button = overlayContainerElement.querySelector(
                          '.actions-menu .button-return') as HTMLElement;
       button.click();
       fixture.detectChanges();
       expect(deviceService.returnDevice).toHaveBeenCalled();
       expect(deviceActionsMenu.refreshDevice.emit).toHaveBeenCalled();
     });

  it('calls enableGuest when guest button is clicked and emits refresh event.',
     () => {
       dummyComponent.testDevice = DEVICE_ASSIGNED;
       const deviceService: DeviceService = TestBed.get(DeviceService);
       spyOn(deviceService, 'enableGuestMode').and.returnValue(of(true));
       spyOn(deviceActionsMenu.refreshDevice, 'emit');
       fixture.detectChanges();
       const actionsButton =
           compiled.querySelector('.icon-more') as HTMLElement;
       actionsButton.click();
       fixture.detectChanges();
       const button = overlayContainerElement.querySelector(
                          '.actions-menu .button-guest') as HTMLElement;
       button.click();
       fixture.detectChanges();
       expect(deviceService.enableGuestMode).toHaveBeenCalled();
       expect(deviceActionsMenu.refreshDevice.emit).toHaveBeenCalled();
     });

  it('calls onDamaged when Mark as damaged is clicked and emits refresh event.',
     () => {
       dummyComponent.testDevice = DEVICE_ASSIGNED;
       const deviceService: DeviceService = TestBed.get(DeviceService);
       spyOn(deviceService, 'markAsDamaged').and.returnValue(of(true));
       spyOn(deviceActionsMenu.refreshDevice, 'emit');
       fixture.detectChanges();
       const actionsButton =
           compiled.querySelector('.icon-more') as HTMLElement;
       actionsButton.click();
       fixture.detectChanges();
       const button = overlayContainerElement.querySelector(
                          '.actions-menu .button-damaged') as HTMLElement;
       button.click();
       fixture.detectChanges();
       expect(deviceService.markAsDamaged).toHaveBeenCalled();
       expect(deviceActionsMenu.refreshDevice.emit).toHaveBeenCalled();
     });

  it('calls onLost when Mark as lost is clicked and emits refresh event.',
     () => {
       dummyComponent.testDevice = DEVICE_ASSIGNED;
       const deviceService: DeviceService = TestBed.get(DeviceService);
       spyOn(deviceService, 'markAsLost').and.returnValue(of(true));
       spyOn(deviceActionsMenu.refreshDevice, 'emit');
       fixture.detectChanges();
       const actionsButton =
           compiled.querySelector('.icon-more') as HTMLElement;
       actionsButton.click();
       fixture.detectChanges();
       const button = overlayContainerElement.querySelector(
                          '.actions-menu .button-lost') as HTMLElement;
       button.click();
       fixture.detectChanges();
       expect(deviceService.markAsLost).toHaveBeenCalled();
       expect(deviceActionsMenu.refreshDevice.emit).toHaveBeenCalled();
     });

  it('calls onUnenroll when Unenroll is clicked and emits refresh event.',
     () => {
       dummyComponent.testDevice = DEVICE_ASSIGNED;
       const deviceService: DeviceService = TestBed.get(DeviceService);
       spyOn(deviceService, 'unenroll').and.returnValue(of(true));
       spyOn(deviceActionsMenu.refreshDevice, 'emit');
       fixture.detectChanges();
       const actionsButton =
           compiled.querySelector('.icon-more') as HTMLElement;
       actionsButton.click();
       fixture.detectChanges();
       const button = overlayContainerElement.querySelector(
                          '.actions-menu .button-unenroll') as HTMLElement;
       button.click();
       fixture.detectChanges();
       expect(deviceService.unenroll).toHaveBeenCalled();
       expect(deviceActionsMenu.refreshDevice.emit).toHaveBeenCalled();
     });
});
