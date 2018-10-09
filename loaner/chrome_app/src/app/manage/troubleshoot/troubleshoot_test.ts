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

import {TroubleshootComponent} from './index';
import {MaterialModule} from './material_module';

describe('TroubleshootComponent', () => {
  let fixture: ComponentFixture<TroubleshootComponent>;
  let app: TroubleshootComponent;

  beforeEach(() => {
    TestBed
        .configureTestingModule({
          declarations: [TroubleshootComponent],
          imports: [
            FlexLayoutModule,
            MaterialModule,
          ],
        })
        .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(TroubleshootComponent);
    app = fixture.debugElement.componentInstance;
  });

  it('should render content on the page', () => {
    expect(fixture.nativeElement.textContent).toContain('Having issues?');
  });

  it('should show the contact information on the page', () => {
    app.contactEmail = 'support@example.com';
    app.contactPhone = ['12345678', '910111213'];
    app.contactWebsite = 'support.example.com';
    app.troubleshootingInformation = 'Contact IT';
    fixture.detectChanges();

    expect(fixture.nativeElement.textContent).toContain('support@example.com');
    expect(fixture.nativeElement.textContent).toContain('12345678');
    expect(fixture.nativeElement.textContent).toContain('support.example.com');
    expect(fixture.nativeElement.textContent).toContain('Contact IT');
  });

});
