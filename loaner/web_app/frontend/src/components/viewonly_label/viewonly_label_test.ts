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
import {ComponentFixture, fakeAsync, flushMicrotasks, TestBed} from '@angular/core/testing';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {RouterTestingModule} from '@angular/router/testing';

import {ViewonlyLabelModule} from '.';

@Component({
  preserveWhitespaces: true,
  template: `
    <loaner-viewonly-label [topLabel]="topLabel" [text]="text">
    </loaner-viewonly-label>`,
})
class HostTestComponent {
  topLabel = '';
  text = '';
}

describe('LoanerViewonlyLabel', () => {
  let fixture: ComponentFixture<HostTestComponent>;
  let hostTestComponent: HostTestComponent;

  beforeEach(fakeAsync(() => {
    TestBed
        .configureTestingModule({
          declarations: [HostTestComponent],
          imports: [
            BrowserAnimationsModule,
            RouterTestingModule,
            ViewonlyLabelModule,
          ],
        })
        .compileComponents();

    flushMicrotasks();

    fixture = TestBed.createComponent(HostTestComponent);
    hostTestComponent = fixture.debugElement.componentInstance;
  }));

  it('should create the LoanerViewonlyLabel', () => {
    expect(hostTestComponent).toBeTruthy();
  });

  it('should render topLabel and text inside the loaner-viewonly-label',
     () => {
       hostTestComponent.topLabel = 'topLabel';
       hostTestComponent.text = 'text';
       fixture.detectChanges();

       const compiled = fixture.debugElement.nativeElement;
       expect(compiled.querySelector('.top-label').textContent)
           .toContain('topLabel');
       expect(compiled.querySelector('.lower-label').textContent)
           .toContain('text');
     });

});
