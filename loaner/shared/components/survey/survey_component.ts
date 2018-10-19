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

import {Component, Input, OnInit, Output} from '@angular/core';
import {Subject} from 'rxjs';
import {take} from 'rxjs/operators';

import {LoaderView} from '../loader';

import {Survey, SurveyAnswer, SurveyResponse, SurveyResponseAnswer, SurveyType} from './survey_service';

@Component({
  host: {'class': 'mat-typography'},
  selector: 'survey',
  styleUrls: ['./survey_component.scss'],
  templateUrl: './survey_component.ng.html',
})
export class SurveyComponent extends LoaderView implements OnInit {
  @Input() surveyType?: SurveyType;
  @Input() surveyDescription?: string;
  @Input() chromeApp = false;
  answerRequired?: boolean;
  surveyAnswer?: SurveyResponseAnswer;
  surveyData?: SurveyResponse;
  userInput?: string;
  @Output() surveyError = new Subject<Error>();

  get surveyNew(): boolean|undefined {
    return this.surveyData && !this.loading;
  }

  get surveyNotGiven(): boolean|undefined {
    return !this.surveyType || !this.surveyNew;
  }

  constructor(private readonly survey: Survey) {
    super(true);
  }

  ngOnInit() {
    if (this.surveyType) {
      this.retrieveSurvey();
    } else {
      this.ready();
    }
  }
  /**
   * Triggered when the survey value changes.
   * Updates the value on the service.
   * @param e String of the more info input
   */
  onChange(e: string) {
    if (this.surveyData) {
      const answer: SurveyAnswer = {
        question_urlsafe_key: this.surveyData.question_urlsafe_key,
        selected_answer: this.surveyAnswer,
        more_info_text: e,
      };
      this.survey.answer.next(answer);
    }
  }

  /**
   * Communicate with survey service to retrieve the survey questions.
   */
  retrieveSurvey() {
    this.waiting();
    if (this.survey.retrievedSurvey) {
      this.surveyData = this.survey.retrievedSurvey;
      this.ready();
    } else if (this.surveyType) {
      this.survey.getSurvey(this.surveyType)
          .pipe(take(1))
          .subscribe(
              val => {
                this.answerRequired = val.required;
                this.surveyData = val;
                this.ready();
              },
              error => {
                this.surveyLoadFailure(error);
                this.ready();
              });
    } else {
      // Invalid survey type.
      this.surveyLoadFailure(new Error('Invalid survey type requested.'));
      this.ready();
    }
  }

  /**
   * Handle cases where survey cannot be loaded/retrieved.
   * @param error Error from the survey.
   */
  private surveyLoadFailure(error: Error) {
    this.surveyError.next(error);
  }
}
