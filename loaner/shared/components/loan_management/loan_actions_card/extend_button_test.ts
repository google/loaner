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

import {Device} from '../../../models/device';
import {ExtendMock} from '../../../testing/mocks';
import {Extend} from '../../extend';

import {LoanActionsCardModule} from './index';

const EXTEND_DEVICE = new Device({
  due_date: new Date(2018, 1, 1),
  max_extend_date: new Date(2018, 1, 3),
});

@Component({
  template: `
  <loaner-loan-actions-card [device]="device">
    <loan-button extendButton
                 (done)="onExtended($event)"></loan-button>
  </loaner-loan-actions-card>`,
})
class ExtendButtonComponent {
  device = EXTEND_DEVICE;
  onExtended(newDate: string) {}
}

describe('LoanActionsCardComponent ExtendButton', () => {
  let app: ExtendButtonComponent;
  let fixture: ComponentFixture<ExtendButtonComponent>;
  let compiled: HTMLElement;

  beforeEach(() => {
    TestBed
        .configureTestingModule({
          declarations: [
            ExtendButtonComponent,
          ],
          imports: [
            BrowserAnimationsModule,
            LoanActionsCardModule,
            RouterTestingModule,
          ],
          providers: [
            {provide: Extend, useClass: ExtendMock},
          ],
        })
        .compileComponents();

    fixture = TestBed.createComponent(ExtendButtonComponent);
    app = fixture.debugElement.componentInstance;
    fixture.detectChanges();
    compiled = fixture.debugElement.nativeElement;
    // Fake the jasmine clock to allow for extension.
    jasmine.clock().mockDate(new Date(2018, 1, 2));
  });

  afterEach(() => {
    jasmine.clock().uninstall();
  });

  it('renders extend button.', () => {
    const buttons = compiled.querySelectorAll('button');
    expect(buttons).toBeDefined();
    expect(buttons.length).toBe(1);
    expect(buttons[0].textContent).toContain('Extend');
  });

  it('calls extend function after is clicked.', () => {
    spyOn(app, 'onExtended');
    fixture.detectChanges();
    const button = compiled.querySelector('button');

    button!.dispatchEvent(new Event('click'));
    expect(app.onExtended).toHaveBeenCalled();
  });

  it('renders a disabled extend button if canExtend is false.', () => {
    EXTEND_DEVICE.dueDate = EXTEND_DEVICE.maxExtendDate;
    fixture.detectChanges();
    compiled = fixture.debugElement.nativeElement;
    const button = compiled.querySelector('button');
    expect(button!.getAttribute('disabled')).toBeDefined();
  });
});
