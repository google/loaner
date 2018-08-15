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
import {UppercaseModule} from '.';

@Component({
  preserveWhitespaces: true,
  template: `<input loanerUppercase type="text" value="test123Test">`,
})
class DummyComponent {
}

describe('Uppercase input directive', () => {
  let fixture: ComponentFixture<DummyComponent>;

  beforeEach(fakeAsync(() => {
    TestBed
        .configureTestingModule({
          declarations: [DummyComponent],
          imports: [UppercaseModule],
        })
        .compileComponents();

    flushMicrotasks();
    fixture = TestBed.createComponent(DummyComponent);
  }));

  it('transforms lowercase input to uppercase on change', () => {
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    const inputEl = compiled.querySelector('input');
    expect(inputEl.value).toContain('test123Test');

    inputEl.dispatchEvent(new Event('change'));
    fixture.detectChanges();
    expect(inputEl.value).toContain('TEST123TEST');
  });

  it('transforms input to uppercase on keyup', () => {
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    const inputEl = compiled.querySelector('input');
    expect(inputEl.value).toContain('test123Test');

    inputEl.dispatchEvent(new Event('keyup'));
    fixture.detectChanges();
    expect(inputEl.value).toContain('TEST123TEST');
  });
});
