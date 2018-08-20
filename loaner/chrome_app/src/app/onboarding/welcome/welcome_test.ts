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
import {MatDialog, MatDialogRef} from '@angular/material';
import {By} from '@angular/platform-browser';

import {AnimationMenuService} from '../../../../../shared/services/animation_menu_service';
import {AnimationMenuServiceMock} from '../../../../../shared/testing/mocks';

import {MaterialModule} from './material_module';
import {WelcomeComponent} from './welcome';

/** Mock material Dialog. */
class MatDialogMock {}

/** Mock material DialogRef. */
class MatDialogRefMock {}

describe('WelcomeComponent', () => {
  let animationService: AnimationMenuService;
  let component: WelcomeComponent;
  let fixture: ComponentFixture<WelcomeComponent>;

  beforeEach(() => {
    TestBed
        .configureTestingModule({
          declarations: [WelcomeComponent],
          imports: [
            MaterialModule,
          ],
          providers: [
            {
              provide: AnimationMenuService,
              useClass: AnimationMenuServiceMock,
            },
            {
              provide: MatDialog,
              useClass: MatDialogMock,
            },
            {
              provide: MatDialogRef,
              useClass: MatDialogRefMock,
            },
          ],
        })
        .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(WelcomeComponent);
    component = fixture.debugElement.componentInstance;
    animationService = TestBed.get(AnimationMenuService);
    fixture.detectChanges();
  });

  it('should render welcome animation instead of text', () => {
    component.welcomeAnimationEnabled = true;
    fixture.detectChanges();
    expect(
        fixture.debugElement.query(By.css('.welcome-animation')).nativeElement)
        .toBeTruthy();
    expect(fixture.debugElement.query(By.css('.welcome-card'))).toBeFalsy();
  });

  it('should have a playback rate of 100% for the welcome animation', () => {
    component.welcomeAnimationEnabled = true;
    fixture.detectChanges();
    expect(component.animationElement.nativeElement.playbackRate).toBe(1);
  });

  it('should have a playback rate of 50% for the welcome animation', () => {
    component.welcomeAnimationEnabled = true;
    animationService.setAnimationSpeed(50);
    fixture.detectChanges();
    expect(component.animationElement.nativeElement.playbackRate).toBe(0.5);
  });

  it('should render welcome text instead of animation', () => {
    component.welcomeAnimationEnabled = false;
    fixture.detectChanges();
    expect(fixture.debugElement.query(By.css('.welcome-card')).nativeElement)
        .toBeTruthy();
    expect(fixture.debugElement.query(By.css('.welcome-animation')))
        .toBeFalsy();
  });

  it('should show the welcome text', () => {
    component.welcomeAnimationEnabled = false;
    fixture.detectChanges();
    expect(fixture.debugElement.query(By.css('.welcome-card'))
               .nativeElement.textContent)
        .toContain('Let\'s get started');
  });
});
