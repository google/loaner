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
import {FormsModule} from '@angular/forms';

import {MinValidatorModule} from '.';

@Component({
  preserveWhitespaces: true,
  template: `
      <form #form="ngForm">
        <input name="field" loanerMinValidator="1"
               #control="ngModel" [(ngModel)]="field">
       <div id="error" *ngIf="!control.valid">Error</div>
      </form>`,
})
class DummyComponent {
  field = 2;
}

describe('Min validator directive', () => {
  let fixture: ComponentFixture<DummyComponent>;
  let compiled: HTMLElement;
  let component: DummyComponent;

  beforeEach(() => {
    TestBed
        .configureTestingModule({
          declarations: [DummyComponent],
          imports: [MinValidatorModule, FormsModule],
        })
        .compileComponents();
    fixture = TestBed.createComponent(DummyComponent);
    compiled = fixture.debugElement.nativeElement;
    component = fixture.componentInstance;
  });

  it('sets input field as invalid when out of min value', () => {
    component.field = 0;
    fixture.detectChanges();
    fixture.whenStable().then(() => {
      fixture.detectChanges();
      const inputField = compiled.querySelector('input[name=field]');
      expect(inputField!.attributes.getNamedItem('class')!.textContent)
          .toContain('ng-untouched ng-pristine ng-invalid');
      expect(compiled.querySelector('#error')).toBeTruthy();
    });
  });

  it('keeps input field as valid when greater min value', () => {
    component.field = 4;
    fixture.detectChanges();
    fixture.whenStable().then(() => {
      fixture.detectChanges();
      const inputField = compiled.querySelector('input[name=field]');
      expect(inputField!.attributes.getNamedItem('class')!.textContent)
          .toContain('ng-untouched ng-pristine ng-valid');
      expect(compiled.querySelector('#error')).toBeFalsy();
    });
  });
});
