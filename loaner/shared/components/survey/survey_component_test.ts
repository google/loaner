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

import {CommonModule} from '@angular/common';
import {HttpClientModule} from '@angular/common/http';
import {DebugElement} from '@angular/core';
import {ComponentFixture, TestBed} from '@angular/core/testing';
import {FormsModule} from '@angular/forms';
import {MatRadioButton} from '@angular/material';
import {By} from '@angular/platform-browser';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';

import {ApiConfig, apiConfigFactory} from '../../services/api_config';
import {LoaderModule} from '../loader';

import {SurveyComponent} from './index';
import {MaterialModule} from './material_module';
import {Survey, SurveyResponse, SurveyType} from './survey_service';

describe('SurveyComponent', () => {
  let app: SurveyComponent;
  let fixture: ComponentFixture<SurveyComponent>;

  /** Radio elements */
  let radioDebugElements: DebugElement[];
  let radioInstances: MatRadioButton[];
  let radioLabelElements: HTMLLabelElement[];

  /** Test Data */
  const surveyData: SurveyResponse = {
    answers: [
      {
        more_info_enabled: true,
        placeholder_text: 'Let us know more.',
        text: 'Yes',
      },
      {
        more_info_enabled: false,
        text: 'No',
      },
      {
        more_info_enabled: true,
        placeholder_text: 'Please explain why',
        text: 'I have no idea',
      },
    ],
    question_text: 'Is this a question about return?',
    question_type: SurveyType.Return,
    question_urlsafe_key: 'randomQuestionString0',
  };

  beforeEach(() => {
    TestBed
        .configureTestingModule({
          declarations: [SurveyComponent],
          imports: [
            CommonModule,
            BrowserAnimationsModule,
            FormsModule,
            HttpClientModule,
            LoaderModule,
            MaterialModule,
          ],
          providers: [
            {
              provide: ApiConfig,
              useValue: apiConfigFactory(
                  'http://example.com/', 'http://chrome-example.com')
            },

            Survey,
          ],
        })
        .compileComponents();

    fixture = TestBed.createComponent(SurveyComponent);
    app = fixture.debugElement.componentInstance;
  });

  it('should display the correct question', () => {
    app.surveyData = surveyData;
    app.ready();
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent)
        .toContain(surveyData.question_text);
  });

  it('should display answers to question', () => {
    app.surveyData = surveyData;
    app.ready();
    fixture.detectChanges();
    radioDebugElements =
        fixture.debugElement.queryAll(By.directive(MatRadioButton));
    radioLabelElements = radioDebugElements.map(
        debugEl => debugEl.query(By.css('label')).nativeElement);
    radioInstances =
        radioDebugElements.map(debugEl => debugEl.componentInstance);
    const radioButtons = fixture.nativeElement.querySelector('mat-radio-group');
    for (const answer of surveyData.answers) {
      expect(radioButtons.textContent).toContain(answer.text);
    }
  });

  it('applies the proper classes for the Chrome App', () => {
    app.surveyData = surveyData;
    app.ready();
    app.chromeApp = true;
    fixture.detectChanges();
    const surveyCardChrome =
        fixture.debugElement.nativeElement.querySelector('.survey-card-chrome');
    expect(surveyCardChrome).toBeTruthy();
  });

  it('applies the proper classes for the Web App', () => {
    app.surveyData = surveyData;
    app.ready();
    app.chromeApp = false;
    fixture.detectChanges();
    const surveyCardChrome =
        fixture.debugElement.nativeElement.querySelector('.survey-card-chrome');
    expect(surveyCardChrome).toBeFalsy();
  });

  it('should show surveyDescription if given', () => {
    app.surveyData = surveyData;
    app.surveyDescription = 'This is a description';
    app.ready();
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent)
        .toContain('This is a description');
    app.surveyDescription = undefined;
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent)
        .not.toContain('This is a description');
  });

  it('should display \'no survey\' text when no survey data is populated',
     () => {
       fixture.detectChanges();
       expect(fixture.nativeElement.textContent)
           .toContain('looks like we don\'t have a survey for you');
     });

  it('should display a text field when a question with more_info_enabled has been clicked',
     () => {
       app.surveyData = surveyData;
       app.ready();
       fixture.detectChanges();
       radioDebugElements =
           fixture.debugElement.queryAll(By.directive(MatRadioButton));
       radioLabelElements = radioDebugElements.map(
           debugEl => debugEl.query(By.css('label')).nativeElement);
       radioInstances =
           radioDebugElements.map(debugEl => debugEl.componentInstance);

       expect(app.surveyAnswer).not.toBeDefined();
       radioLabelElements[0].click();
       expect(radioInstances[0].checked).toBeTruthy();
       expect(app.surveyAnswer).toBeDefined();
       fixture.detectChanges();
       expect(fixture.nativeElement.textContent)
           .toContain(surveyData.answers[0].placeholder_text);
       expect(fixture.nativeElement.textContent)
           .not.toContain(surveyData.answers[2].placeholder_text);
       radioLabelElements[2].click();
       fixture.detectChanges();
       expect(fixture.nativeElement.textContent)
           .toContain(surveyData.answers[2].placeholder_text);
       expect(fixture.nativeElement.textContent)
           .not.toContain(surveyData.answers[0].placeholder_text);
     });
});
