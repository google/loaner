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
import {FlexLayoutModule} from '@angular/flex-layout';
import {By} from '@angular/platform-browser';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';

import {ProgressComponent} from './index';
import {MaterialModule} from './material_module';

describe('Shared ProgressComponent', () => {
  let fixture: ComponentFixture<ProgressComponent>;
  let app: ProgressComponent;

  beforeEach(() => {
    TestBed
        .configureTestingModule({
          declarations: [ProgressComponent],
          imports: [
            BrowserAnimationsModule,
            FlexLayoutModule,
            MaterialModule,
          ],
        })
        .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ProgressComponent);
    app = fixture.debugElement.componentInstance;
    fixture.detectChanges();
  });

  it('should set the app progress to 25', () => {
    app.current = 1;
    app.max = 4;
    const element =
        fixture.debugElement.query(By.css('mat-progress-bar')).attributes;
    fixture.detectChanges();
    expect(app.progress).toBe(25);
    expect(element['aria-valuenow']).toBe('25');
  });
});
