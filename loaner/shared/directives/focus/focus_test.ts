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
import {By} from '@angular/platform-browser';

import {FocusDirective} from './focus';

@Component({
  selector: 'focus-test-component',
  template: `
  <div id="one">Hello!</div>
  <div id="two">How are you</div>
  <div id="three" loaner-focus>Should be focused</div>
  <div id="four">Stuff</div>
  `,
})
class FocusTestComponent {
}

describe('FocusDirective', () => {
  let fixture: ComponentFixture<FocusTestComponent>;

  beforeEach(() => {
    TestBed
        .configureTestingModule({
          declarations: [FocusTestComponent, FocusDirective],
        })
        .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(FocusTestComponent);
    fixture.detectChanges();
  });

  it('should focus the div with loaner-focus', () => {
    expect(
        fixture.debugElement.query(By.css('#three')).attributes['loaner-focus'])
        .toBeDefined();
  });

  it('should report the fourth div as not focused', () => {
    expect(
        fixture.debugElement.query(By.css('#four')).attributes['loaner-focus'])
        .toBeUndefined();
  });
});
