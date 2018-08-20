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
import {By} from '@angular/platform-browser';
import {RouterTestingModule} from '@angular/router/testing';

import {AnimationMenuService} from '../../../../shared/services/animation_menu_service';
import {AnimationMenuServiceMock} from '../../../../shared/testing/mocks';
import {AnalyticsService, AnalyticsServiceMock} from '../shared/analytics';

import {AppModule, AppRoot} from './app';

describe('AppRoot offboarding', () => {
  let fixture: ComponentFixture<AppRoot>;
  let app: AppRoot;

  beforeEach(() => {
    TestBed
        .configureTestingModule({
          imports: [RouterTestingModule, AppModule],
          providers: [
            {
              provide: AnimationMenuService,
              useClass: AnimationMenuServiceMock,
            },
            {
              provide: AnalyticsService,
              useClass: AnalyticsServiceMock,
            },
          ],
        })
        .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(AppRoot);
    app = fixture.debugElement.componentInstance;
  });

  it('should show the title of the page in the toolbar', () => {
    // Settle the initial view before updating the title.
    fixture.detectChanges();
    const toolbarDebugEl = fixture.debugElement.query(By.css('mat-toolbar'));
    expect(toolbarDebugEl.nativeElement.textContent)
        .toContain('Get ready to return this device');
  });
});
