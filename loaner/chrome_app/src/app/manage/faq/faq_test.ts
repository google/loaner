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

import {HttpClient, HttpClientModule} from '@angular/common/http';
import {ComponentFixture, TestBed} from '@angular/core/testing';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {of} from 'rxjs';

import {FaqComponent} from './index';
import {MaterialModule} from './material_module';

describe('FaqComponent', () => {
  let fixture: ComponentFixture<FaqComponent>;

  beforeEach(() => {
    TestBed
        .configureTestingModule({
          declarations: [FaqComponent],
          imports: [
            BrowserAnimationsModule,
            HttpClientModule,
            MaterialModule,
          ],
        })
        .compileComponents();
    fixture = TestBed.createComponent(FaqComponent);
  });

  it('should render markdown as HTML', () => {
    const httpService = TestBed.get(HttpClient);
    const faqMock = `
# Heading 1
## Heading 2
### Heading 3

You can do the following:
1. This way
2. That way
3. The other way
    `;
    spyOn(httpService, 'get').and.returnValue(of(faqMock));
    fixture.detectChanges();

    expect(fixture.debugElement.nativeElement.querySelector('h1').textContent)
        .toContain('Heading 1');
    expect(fixture.debugElement.nativeElement.querySelector('h2').textContent)
        .toContain('Heading 2');
    expect(fixture.debugElement.nativeElement.querySelector('li').textContent)
        .toContain('This way');
  });
});
