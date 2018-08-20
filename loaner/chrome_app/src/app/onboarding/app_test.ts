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

import {AnimationMenuService} from '../../../../shared/components/animation_menu';
import {Survey, SurveyMock} from '../../../../shared/components/survey';
import {PROGRAM_NAME} from '../../../../shared/config';
import {AnimationMenuServiceMock} from '../../../../shared/testing/mocks';
import {AnalyticsService, AnalyticsServiceMock} from '../shared/analytics';
import {Background, BackgroundMock} from '../shared/background_service';

import {AppModule, AppRoot} from './app';

describe('Onboarding AppRoot', () => {
  let app: AppRoot;
  let fixture: ComponentFixture<AppRoot>;

  beforeEach(() => {
    TestBed
        .configureTestingModule({
          imports: [AppModule],
          providers: [
            {
              provide: AnimationMenuService,
              useClass: AnimationMenuServiceMock,
            },
            {
              provide: AnalyticsService,
              useClass: AnalyticsServiceMock,
            },
            {
              provide: Background,
              useClass: BackgroundMock,
            },
            {
              provide: Survey,
              useClass: SurveyMock,
            },
          ],
        })
        .compileComponents();

    fixture = TestBed.createComponent(AppRoot);
    app = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should show the title of the page in the toolbar', () => {
    const toolbarDebugEl =
        fixture.debugElement.nativeElement.querySelector('mat-toolbar');
    expect(toolbarDebugEl.textContent).toContain(`Welcome to ${PROGRAM_NAME}`);
  });

  it('should render flow sequence and buttons', () => {
    expect(fixture.debugElement.nativeElement.querySelector(
               'loaner-flow-sequence'))
        .toBeDefined();
    expect(fixture.debugElement.nativeElement.querySelector(
               'loaner-flow-sequence-buttons'))
        .toBeDefined();
  });

  it('should update the step number when flow changes', () => {
    expect(app.currentStep).toBe(0);
    app.flowSequenceButtons.goForward();
    expect(app.currentStep).toBe(1);
  });

  it('should FAIL to go forward when canProceed is false', () => {
    app.flowSequenceButtons.canProceed = false;
    expect(app.currentStep).toBe(0);
    app.flowSequenceButtons.goForward();
    expect(app.currentStep).toBe(0);
  });

  it('should send survey and update surveySent value', () => {
    expect(app.surveySent).toBeFalsy();
    const surveyService: Survey = TestBed.get(Survey);
    spyOn(surveyService, 'submitSurvey').and.callThrough();
    const fakeSurveyData = {
      more_info_text: 'Yes, this is more info.',
      question_urlsafe_key: 'randomQuestionString0',
      selected_answer: {
        more_info_enabled: true,
        more_info_text: 'Not sure what you mean',
        text: 'Yes',
      },
    };
    app.sendSurvey(fakeSurveyData);
    expect(surveyService.submitSurvey).toHaveBeenCalledWith(fakeSurveyData);
    expect(app.surveySent).toBeTruthy();
    expect(app.surveyComponent.surveySent).toBeTruthy();
  });
});
