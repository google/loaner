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
import {ComponentFixture, TestBed} from '@angular/core/testing';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {RouterTestingModule} from '@angular/router/testing';

import {DEVICE, GuestModeMock} from '../../../testing/mocks';
import {GuestMode} from '../../guest';

import {LoanActionsCardModule} from './index';

const GUEST_DEVICE = {...DEVICE};

@Component({
  template: `
  <loaner-loan-actions-card [device]="device">
    <loan-button guestButton
                 (done)="onGuestModeEnabled()"></loan-button>
  </loaner-loan-actions-card>`,
})
class GuestButtonComponent {
  device = GUEST_DEVICE;
  onGuestModeEnabled() {}
}

describe('LoanActionsCardComponent GuestModeButton', () => {
  let app: GuestButtonComponent;
  let fixture: ComponentFixture<GuestButtonComponent>;
  let compiled: HTMLElement;

  beforeEach(() => {
    TestBed
        .configureTestingModule({
          declarations: [
            GuestButtonComponent,
          ],
          imports: [
            BrowserAnimationsModule,
            LoanActionsCardModule,
            RouterTestingModule,
          ],
          providers: [
            {provide: GuestMode, useClass: GuestModeMock},
          ],
        })
        .compileComponents();

    fixture = TestBed.createComponent(GuestButtonComponent);
    app = fixture.debugElement.componentInstance;
    fixture.detectChanges();
    compiled = fixture.debugElement.nativeElement;
  });

  it('renders guest button.', () => {
    const buttons = compiled.querySelectorAll('button');
    expect(buttons).toBeDefined();
    expect(buttons.length).toBe(1);
    expect(buttons[0].textContent).toContain('Enable Guest');
  });

  it('calls onGuestModeEnabled function after is clicked.', () => {
    spyOn(app, 'onGuestModeEnabled');
    const button = compiled.querySelector('button');

    button!.dispatchEvent(new Event('click'));
    expect(app.onGuestModeEnabled).toHaveBeenCalled();
  });

  it('disables guest button after is clicked.', () => {
    spyOn(app, 'onGuestModeEnabled');
    let button = compiled.querySelector('button');

    button!.dispatchEvent(new Event('click'));

    fixture.detectChanges();
    compiled = fixture.debugElement.nativeElement;
    button = compiled.querySelector('button');
    expect(button!.getAttribute('disabled')).toBeDefined();
  });

  it('does not render guest button if guestAllowed is false.', () => {
    GUEST_DEVICE.guestAllowed = false;
    fixture.detectChanges();
    compiled = fixture.debugElement.nativeElement;
    const button = compiled.querySelector('button');
    expect(button).toBeNull();
  });
});
