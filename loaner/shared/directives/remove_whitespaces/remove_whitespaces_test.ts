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
import {RemoveWhitespacesModule} from '.';

@Component({
  preserveWhitespaces: true,
  template:
      `<input loanerRemoveWhitespaces type="text" value="with whitespace">`,
})
class DummyComponent {
}

describe('Remove whitespaces directive', () => {
  let fixture: ComponentFixture<DummyComponent>;

  beforeEach(fakeAsync(() => {
    TestBed
        .configureTestingModule({
          declarations: [DummyComponent],
          imports: [RemoveWhitespacesModule],
        })
        .compileComponents();

    flushMicrotasks();
    fixture = TestBed.createComponent(DummyComponent);
  }));

  it('Directive should strip whitespace from default input value', () => {
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    const inputEl = compiled.querySelector('input');
    expect(inputEl.value).toContain('with whitespace');

    inputEl.dispatchEvent(new Event('change'));
    fixture.detectChanges();
    expect(inputEl.value).toContain('withwhitespace');
  });
});
