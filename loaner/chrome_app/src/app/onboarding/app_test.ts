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

import {HttpClientTestingModule} from '@angular/common/http/testing';
import {ComponentFixture, TestBed} from '@angular/core/testing';

import {AnimationMenuService} from '../../../../shared/components/animation_menu';
import {Survey, SurveyMock} from '../../../../shared/components/survey';
import {PROGRAM_NAME} from '../../../../shared/config';
import {NetworkService} from '../../../../shared/services/network_service';
import {AnimationMenuServiceMock} from '../../../../shared/testing/mocks';
import {AnalyticsService, AnalyticsServiceMock} from '../shared/analytics';
import {Background, BackgroundMock} from '../shared/background_service';
import {Loan, LoanMock} from '../shared/loan';

import {AppModule, AppRoot} from './app';

describe('Onboarding AppRoot', () => {
  let app: AppRoot;
  let fixture: ComponentFixture<AppRoot>;

  beforeEach(() => {
    TestBed
        .configureTestingModule({
          imports: [AppModule, HttpClientTestingModule],
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
              provide: Loan,
              useClass: LoanMock,
            },
            {
              provide: Survey,
              useClass: SurveyMock,
            },
            NetworkService,
          ],
        })
        .compileComponents();

    fixture = TestBed.createComponent(AppRoot);
    app = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('shows the title of the page in the toolbar', () => {
    const toolbarDebugEl =
        fixture.debugElement.nativeElement.querySelector('mat-toolbar');
    expect(toolbarDebugEl.textContent).toContain(`Welcome to ${PROGRAM_NAME}`);
  });

  it('renders flow sequence and buttons', () => {
    expect(fixture.debugElement.nativeElement.querySelector(
               'loaner-flow-sequence'))
        .toBeDefined();
    expect(fixture.debugElement.nativeElement.querySelector(
               'loaner-flow-sequence-buttons'))
        .toBeDefined();
  });

  it('updates the step number when flow changes', () => {
    expect(app.currentStep).toBe(0);
    app.flowSequenceButtons.goForward();
    expect(app.currentStep).toBe(1);
  });

  it('FAILs to go forward when canProceed is false', () => {
    app.flowSequenceButtons.canProceed = false;
    expect(app.currentStep).toBe(0);
    app.flowSequenceButtons.goForward();
    expect(app.currentStep).toBe(0);
  });

  it('should FAIL to go forward when allowButtonClick is false', () => {
    app.flowSequenceButtons.allowButtonClick = false;
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
    app.surveyAnswer = fakeSurveyData;
    app.launchManageView();
    fixture.detectChanges();
    expect(app.flowSequenceButtons.canProceed).toBe(false);
    expect(surveyService.submitSurvey).toHaveBeenCalledWith(fakeSurveyData);
  });

  it('should open the manage view and NOT send the survey', () => {
    expect(app.surveySent).toBeFalsy();
    expect(app.surveyAnswer).toBeFalsy();
    const bg: Background = TestBed.get(Background);
    spyOn(bg, 'openView');
    app.launchManageView();
    fixture.detectChanges();
    expect(app.flowSequenceButtons.canProceed).toBe(false);
    expect(bg.openView).toHaveBeenCalledWith('manage');
  });
});
