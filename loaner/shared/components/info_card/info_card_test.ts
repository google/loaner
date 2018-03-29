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

import {ComponentFixture, TestBed} from '@angular/core/testing';

import {LoanerTextCard, LoanerTextCardModule} from './index';
import {MaterialModule} from './material_module';

describe('LoanerTextCard', () => {
  let app: LoanerTextCard;
  let fixture: ComponentFixture<LoanerTextCard>;

  beforeEach(() => {
    TestBed
        .configureTestingModule({
          imports: [
            LoanerTextCardModule,
            MaterialModule,
          ],
        })
        .compileComponents();

    fixture = TestBed.createComponent(LoanerTextCard);
    app = fixture.debugElement.componentInstance;
  });

  it('should display nothing if no title or body are given', () => {
    fixture.detectChanges();
    expect(fixture.debugElement.nativeElement.textContent.trim()).toBeFalsy();
  });

  it('should display a title when given', () => {
    app.title = 'Hello world';
    fixture.detectChanges();
    expect(fixture.debugElement.nativeElement.querySelector('.card-title')
               .textContent)
        .toContain('Hello world');
    expect(
        fixture.debugElement.nativeElement.querySelector('.card-description'))
        .toBeNull();
  });

  it('should display a title and body when given', () => {
    app.title = 'Hello world';
    app.body = 'This is a simple message';
    fixture.detectChanges();
    expect(fixture.debugElement.nativeElement.querySelector('.card-title')
               .textContent)
        .toContain('Hello world');
    expect(fixture.debugElement.nativeElement.querySelector('.card-description')
               .textContent)
        .toContain('This is a simple message');
  });

  it('should display only a body if a title is not given', () => {
    app.body = 'This is a simple message';
    fixture.detectChanges();
    expect(fixture.debugElement.nativeElement.querySelector('.card-title'))
        .toBeNull();
    expect(fixture.debugElement.nativeElement.querySelector('.card-description')
               .textContent)
        .toContain('This is a simple message');
  });
});
