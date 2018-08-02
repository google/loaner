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

import {HttpClientTestingModule, HttpTestingController} from '@angular/common/http/testing';
import {fakeAsync, TestBed} from '@angular/core/testing';

import {ApiConfig, apiConfigFactory} from '../../services/api_config';

import {Survey, SurveyAnswer, SurveyResponse, SurveyType} from './survey_service';

describe('Survey Service', () => {
  let httpMock: HttpTestingController;
  let survey: Survey;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [
        HttpClientTestingModule,
      ],
      providers: [
        {
          provide: ApiConfig,
          useValue: apiConfigFactory(
              'http://example.com/', 'http://chrome-example.com')
        },
        Survey,
      ]
    });

    survey = TestBed.get(Survey);
    httpMock = TestBed.get(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should get ASSIGNMENT survey', fakeAsync(() => {
       const testSurveyData: SurveyResponse = {
         answers: [
           {
             more_info_enabled: false,
             text: 'Yes',
           },
           {
             more_info_enabled: true,
             more_info_text: 'Let us know',
             text: 'No',
           },
         ],
         question_text: 'Is this a question about assignment?',
         question_type: SurveyType.Assignment,
         question_urlsafe_key: 'randomSurveyString0',
       };

       survey.getSurvey(SurveyType.Assignment).subscribe((survey) => {
         expect(survey).toEqual(testSurveyData);
       });
       const req = httpMock.expectOne(
           `${survey.apiBaseUrl}/loaner/v1/survey/request?question_type=${
               SurveyType.Assignment}`);
       expect(req.request.method).toBe('GET');
       req.flush(testSurveyData);
     }));

  it('should get RETURN survey', fakeAsync(() => {
       const testSurveyData: SurveyResponse = {
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
         ],
         question_text: 'Is this a question about return?',
         question_type: SurveyType.Return,
         question_urlsafe_key: 'randomQuestionString0',
       };

       survey.getSurvey(SurveyType.Return).subscribe((survey) => {
         expect(survey).toEqual(testSurveyData);
       });

       const req = httpMock.expectOne(
           `${survey.apiBaseUrl}/loaner/v1/survey/request?question_type=${
               SurveyType.Return}`);
       expect(req.request.method).toBe('GET');
       req.flush(testSurveyData);
     }));

  it('should submit survey', fakeAsync(() => {
       const testAnswer: SurveyAnswer = {
         more_info_text: 'Yes, this is more info.',
         question_urlsafe_key: 'randomQuestionString0',
         selected_answer: {
           more_info_enabled: true,
           more_info_text: 'Not sure what you mean',
           text: 'Yes',
         },
       };

       survey.submitSurvey(testAnswer).subscribe((submitted) => {
         expect(testAnswer).toBeTruthy();
       });

       const req =
           httpMock.expectOne(`${survey.apiBaseUrl}/loaner/v1/survey/submit`);
       expect(req.request.method).toBe('POST');
       req.flush(testAnswer);
     }));
});
