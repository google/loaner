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

import {DEVICE} from '../../../testing/mocks';

import {LoanActionsCardModule} from './index';

@Component({
  template: `
  <loaner-loan-actions-card [device]="device">
    <loan-button extendButton
                 (done)="onExtended($event)"></loan-button>
    <loan-button guestButton
                 (done)="onGuestModeEnabled()"></loan-button>
    <loan-button returnButton (done)="onReturned()"></loan-button>
    <loan-button damagedButton (done)="onDamaged($event)"></loan-button>
    <loan-button lostButton (done)="onLost()"></loan-button>
  </loaner-loan-actions-card>`,
})
class AllButtonsComponent {
  device = DEVICE;
  onExtended(newDate: string) {}
  onGuestModeEnabled() {}
  onReturned() {}
  onDamaged(reason: string) {}
  onLost() {}
}

@Component({
  template: `
  <loaner-loan-actions-card [device]="device">
    <loan-button returnButton (done)="onReturned()"></loan-button>
    <loan-button damagedButton (done)="onDamaged($event)"></loan-button>
    <loan-button lostButton (done)="onDamaged($event)"></loan-button>
  </loaner-loan-actions-card>`,
})
class TwoButtonsComponent {
  device = DEVICE;
  onReturned() {}
  onDamaged(reason: string) {}
}

describe('LoanActionsCardComponent', () => {
  beforeEach(() => {
    TestBed
        .configureTestingModule({
          declarations: [
            AllButtonsComponent,
            TwoButtonsComponent,
          ],
          imports: [
            BrowserAnimationsModule,
            LoanActionsCardModule,
            RouterTestingModule,
          ],
        })
        .compileComponents();
  });

  it('renders all buttons defined.', () => {
    const fixture: ComponentFixture<AllButtonsComponent> =
        TestBed.createComponent(AllButtonsComponent);
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    expect(compiled.querySelectorAll('button').length).toBe(5);
  });

  it('renders only buttons that are defined.', () => {
    const fixture: ComponentFixture<TwoButtonsComponent> =
        TestBed.createComponent(TwoButtonsComponent);
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    expect(compiled.querySelectorAll('button').length).toBe(3);
  });
});
