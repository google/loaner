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


import {HttpClient} from '@angular/common/http';
import {Inject, Injectable} from '@angular/core';
import {BehaviorSubject, Observable, of, Subject, throwError} from 'rxjs';
import {retry, tap} from 'rxjs/operators';

import {ApiConfig} from '../../services/api_config';

/**
 * The type of survey being received from the API.
 * Survey Types match backend SurveyModel SurveyType enum.
 */
export enum SurveyType {
  Assignment = 'ASSIGNMENT',
  Return = 'RETURN',
}

/** Answer interface per backend API. */
export declare interface SurveyAnswer {
  more_info_text?: string;
  question_urlsafe_key?: string;
  selected_answer?: SurveyResponseAnswer;
}

/** Answers for SurveyResponse.answers */
export declare interface SurveyResponseAnswer {
  more_info_enabled?: boolean;
  more_info_text?: string;
  placeholder_text?: string;
  text: string;
}

/** Response recieved on a survey request. */
export declare interface SurveyResponse {
  answers: SurveyResponseAnswer[];
  enabled?: boolean;
  question_text: string;
  question_type: string;
  question_urlsafe_key: string;
  rand_weight?: number;
  required?: boolean;
}

/** Service for retrieving and submitting survey information. */
@Injectable()
export class Survey {
  apiBaseUrl: string;
  answer = new Subject<SurveyAnswer>();
  retrievedSurvey!: SurveyResponse;
  surveySent = new BehaviorSubject<boolean>(false);

  constructor(
      @Inject(ApiConfig) private readonly apiConfig: ApiConfig,
      private readonly http: HttpClient) {
    this.apiBaseUrl = this.apiConfig.baseUrl;
  }

  /**
   * Submits the survey
   * @param answer SurveyAnswer used to reference a users answer in the survey.
   */
  submitSurvey(answer: SurveyAnswer): Observable<boolean> {
    const surveyEndpoint = `${this.apiBaseUrl}/loaner/v1/survey/submit`;
    return new Observable((observer) => {
      this.http.post(surveyEndpoint, answer)
          .pipe(retry(2), tap(() => this.surveySent.next(true)))
          .subscribe(
              () => {
                observer.next(true);
              },
              error => {
                this.surveySent.next(false);
                throw throwError(error);
              });
    });
  }

  /**
   * Retrieves the survey
   * @param type SurveyType represents the type of survey being retrieved.
   */
  getSurvey(type: SurveyType): Observable<SurveyResponse> {
    const surveyEndpoint =
        `${this.apiBaseUrl}/loaner/v1/survey/request?question_type=${type}`;
    return this.http.get<SurveyResponse>(surveyEndpoint)
        .pipe(retry(2), tap((survey) => this.retrievedSurvey = survey));
  }
}

export class SurveyMock {
  answer = new Subject<SurveyAnswer>();
  surveySent = new BehaviorSubject<boolean>(false);

  submitSurvey(answer: SurveyAnswer): Observable<boolean> {
    return of(true);
  }

  getSurvey(type: SurveyType): Observable<SurveyResponse> {
    return new Observable(observer => {
      if (type === SurveyType.Assignment) {
        observer.next({
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
          question_urlsafe_key: 'randomQuestionString0',
          question_text: 'Is this a question about assignment?',
          question_type: SurveyType.Assignment,
        });
      } else if (type === SurveyType.Return) {
        observer.next({
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
          question_urlsafe_key: 'randomQuestionString0',
          question_text: 'Is this a question about return?',
          question_type: SurveyType.Return,
        });
      }
    });
  }
}
