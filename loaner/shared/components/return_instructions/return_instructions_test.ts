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

import {async, ComponentFixture, TestBed} from '@angular/core/testing';
import {MatDialog, MatDialogRef} from '@angular/material';

import {AnimationMenuService} from '../../services/animation_menu_service';
import {AnimationMenuServiceMock} from '../../testing/mocks';

import {FlowsEnum, LoanerReturnInstructions} from './index';
import {MaterialModule} from './material_module';

/** Mock material Dialog. */
class MatDialogMock {}

/** Mock material DialogRef. */
class MatDialogRefMock {}

describe('LoanerReturnInstructions', () => {
  let animationService: AnimationMenuService;
  let app: LoanerReturnInstructions;
  let fixture: ComponentFixture<LoanerReturnInstructions>;

  beforeEach(async(() => {
    TestBed
        .configureTestingModule({
          declarations: [LoanerReturnInstructions],
          imports: [MaterialModule],
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
  }));

  beforeEach(async(() => {
    fixture = TestBed.createComponent(LoanerReturnInstructions);
    app = fixture.debugElement.componentInstance;
    animationService = TestBed.get(AnimationMenuService);
    app.flow = FlowsEnum.ONBOARDING;
    fixture.detectChanges();
  }));

  it('renders the animation or return text', () => {
    app.flow = FlowsEnum.ONBOARDING;
    app.animationEnabled = true;
    fixture.detectChanges();
    const returnAnimation =
        fixture.debugElement.nativeElement.querySelector('.return-animation');
    expect(returnAnimation).toBeTruthy();
  });

  it('has a playback rate of 100% for animation', () => {
    app.flow = FlowsEnum.ONBOARDING;
    app.animationEnabled = true;
    fixture.detectChanges();
    expect(app.animationElement.nativeElement.playbackRate).toBe(1);
  });

  it('has a playback rate of 50% for animation', () => {
    app.flow = FlowsEnum.ONBOARDING;
    spyOn(animationService, 'setAnimationSpeed').and.callThrough();
    app.animationEnabled = true;
    animationService.setAnimationSpeed(50);
    fixture.detectChanges();
    expect(animationService.setAnimationSpeed).toHaveBeenCalledWith(50);

    expect(app.animationElement.nativeElement.playbackRate).toBe(0.5);
    expect(app.playbackRate).toBe(0.5);
  });

  it('does NOT render the animation or return text', () => {
    app.flow = FlowsEnum.ONBOARDING;
    app.animationEnabled = false;
    fixture.detectChanges();
    const returnAnimation =
        fixture.debugElement.nativeElement.querySelector('.return-animation');
    expect(returnAnimation).toBeFalsy();
  });

  it('applies the proper classes for the Chrome App', () => {
    app.flow = FlowsEnum.ONBOARDING;
    app.chromeApp = true;
    app.animationEnabled = true;
    fixture.detectChanges();
    const returnAnimation =
        fixture.debugElement.nativeElement.querySelector('.return-animation');
    const returnAnimationChrome =
        fixture.debugElement.nativeElement.querySelector(
            '.return-animation-chrome');
    expect(returnAnimationChrome).toBeTruthy();
    expect(returnAnimation).toBeFalsy();
  });

  it('applies the proper classes for the Web App', () => {
    app.flow = FlowsEnum.ONBOARDING;
    app.chromeApp = false;
    app.animationEnabled = true;
    fixture.detectChanges();
    const returnAnimation =
        fixture.debugElement.nativeElement.querySelector('.return-animation');
    const returnAnimationChrome =
        fixture.debugElement.nativeElement.querySelector(
            '.return-animation-chrome');
    expect(returnAnimation).toBeTruthy();
    expect(returnAnimationChrome).toBeFalsy();
  });

  it('renders the return text for the onboarding flow', () => {
    app.flow = FlowsEnum.ONBOARDING;
    app.animationEnabled = false;
    fixture.detectChanges();
    const returnBox =
        fixture.debugElement.nativeElement.querySelector('.return-card');
    expect(returnBox.textContent).toContain(`Before you go!`);
  });

  it('renders the return text for the offboarding flow', () => {
    app.flow = FlowsEnum.OFFBOARDING;
    app.programName = 'Test Program';
    app.animationEnabled = false;
    fixture.detectChanges();
    const returnBox =
        fixture.debugElement.nativeElement.querySelector('.return-card');
    expect(returnBox.textContent).toContain(`Thanks for using Test Program!`);
  });
});
