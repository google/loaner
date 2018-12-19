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

import {PlatformLocation} from '@angular/common';
import {AfterViewInit, Component, NgModule, OnInit, ViewChild, ViewEncapsulation} from '@angular/core';
import {FlexLayoutModule} from '@angular/flex-layout';
import {BrowserModule, Title} from '@angular/platform-browser';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';

import {AnimationMenuModule} from '../../../../shared/components/animation_menu';
import {FlowState, LoanerFlowSequence, LoanerFlowSequenceButtons, LoanerFlowSequenceModule, NavigationLabels, Step} from '../../../../shared/components/flow_sequence';
import {LoanerTextCardModule} from '../../../../shared/components/info_card';
import {LoanerProgressModule} from '../../../../shared/components/progress';
import {FlowsEnum, LoanerReturnInstructions, LoanerReturnInstructionsModule} from '../../../../shared/components/return_instructions';
import {Survey, SurveyAnswer, SurveyComponent, SurveyModule, SurveyType} from '../../../../shared/components/survey';
import {BACKGROUND_LOGO, BACKGROUND_LOGO_ENABLED, ConfigService, PROGRAM_NAME, RETURN_ANIMATION_ALT_TEXT, RETURN_ANIMATION_ENABLED, RETURN_ANIMATION_URL, TOOLBAR_ICON, TOOLBAR_ICON_ENABLED} from '../../../../shared/config';
import {ApiConfig, apiConfigFactory} from '../../../../shared/services/api_config';
import {NetworkService} from '../../../../shared/services/network_service';
import {AnalyticsModule, AnalyticsService} from '../shared/analytics';
import {Background} from '../shared/background_service';
import {ChromeAppPlatformLocation} from '../shared/chrome_app_platform_location';
import {FailAction, FailType, Failure, FailureModule} from '../shared/failure';
import {HttpModule} from '../shared/http/http_module';
import {Loan} from '../shared/loan';

import {MaterialModule} from './material_module';

/**
 * Steps for the flow sequence.
 * Important: Insert components in to HTML in same order as seen below.
 */
const STEPS: Step[] = [
  {
    id: 'return',
    title: 'Get ready to return this device',
  },
  {
    id: 'survey',
    title: 'One final question before you go',
  },
  {
    id: 'return_instructions',
    title: 'Are you sure you want to return this device?',
  },
  {
    id: 'logout',
    title: 'Logout and return the loaner',
  },
];

@Component({
  encapsulation: ViewEncapsulation.None,
  preserveWhitespaces: true,
  selector: 'app-root',
  styleUrls: ['./app.scss'],
  templateUrl: './app.ng.html',
})
export class AppRoot implements AfterViewInit, OnInit {
  readonly backgroundLogo = BACKGROUND_LOGO;
  readonly backgroundLogoEnabled = BACKGROUND_LOGO_ENABLED;
  readonly toolbarIcon = TOOLBAR_ICON;
  readonly toolbarIconEnabled = TOOLBAR_ICON_ENABLED;

  /** Labels to be used on navigation buttons. */
  readonly labels: NavigationLabels = {
    previous: {aria: 'Previous step', toolTip: 'Previous Step'},
    next: {aria: 'Next step', toolTip: 'Next Step'},
    done: {
      aria: 'All done! Your loaner can now be returned.',
      toolTip: 'All done! Your loaner can now be returned.',
    }
  };
  flows = FlowsEnum;
  currentStep = 0;
  maxStep = 0;
  readonly steps = STEPS;
  @ViewChild(LoanerFlowSequence) flowSequence!: LoanerFlowSequence;
  @ViewChild(LoanerFlowSequenceButtons)
  flowSequenceButtons!: LoanerFlowSequenceButtons;

  surveyAnswer!: SurveyAnswer;
  surveySent = false;

  returnCompleted = false;

  // Flow components to be manipulated.
  @ViewChild(SurveyComponent) surveyComponent!: SurveyComponent;
  @ViewChild(LoanerReturnInstructions)
  returnInstructions!: LoanerReturnInstructions;

  // Represents the analytics image in the body.
  @ViewChild('analytics') analyticsImg!: HTMLImageElement|null;

  // Text to be populated on an info card for logout step.
  logoutPage = {
    title: 'Your loaner is now set to be returned.',
    body:
        `You may now logout and return this loaner to the nearest shelf. We hope
    you enjoyed your ${PROGRAM_NAME} experience!`,
  };
  // Text to be populated on an info card for return step.
  returnPage = {
    title: `Are you sure you want to return this ${PROGRAM_NAME} device?`,
    body: `By proceeding to the next step, you will mark the loaner as being
    returned. Once you proceed to the next step, you will need to return the
device to your nearest shelf as soon as possible.`,
  };

  constructor(
      private readonly analyticsService: AnalyticsService,
      private readonly bg: Background,
      private readonly config: ConfigService,
      private readonly failure: Failure,
      private readonly loan: Loan,
      private readonly networkService: NetworkService,
      private readonly survey: Survey,
      readonly title: Title,
  ) {
    title.setTitle(`Return your ${PROGRAM_NAME} loaner`);
    this.survey.answer.subscribe(val => {
      this.surveyAnswer = val;
    });
  }

  /**
   * Updates the analytics view and changes the analytics img src to match.
   * @param view represents the current page/view.
   */
  private updateAnalytics(view: string) {
    if (this.config.analyticsEnabled) {
      this.analyticsService.sendView('offboarding', view).subscribe(url => {
        if (this.analyticsImg) {
          this.analyticsImg.src = window.URL.createObjectURL(url);
        }
      });
    }
  }

  ngAfterViewInit() {
    this.updateAnalytics('/return');
  }

  ngOnInit() {
    this.flowSequence.steps = this.steps;
    this.maxStep = this.flowSequence.maxStepNumber;

    // Setup navigation buttons
    this.flowSequence.flowSequenceButtons = this.flowSequenceButtons;
    this.flowSequenceButtons.flowState = this.flowSequence.flowState;
    this.flowSequence.setupFlowButtonsListener();

    // Setup survey component
    this.surveySetup();
    this.surveyListener();

    // Setup return instructions
    this.returnInstructions.programName = PROGRAM_NAME;
    this.returnInstructions.animationEnabled = RETURN_ANIMATION_ENABLED;
    this.returnInstructions.animationAltText = RETURN_ANIMATION_ALT_TEXT;
    this.returnInstructions.animationURL = RETURN_ANIMATION_URL;

    // Listen for flow finished
    this.flowSequenceButtons.finished.subscribe(finished => {
      if (finished) this.closeApplication();
    });

    // If there is no network connection, disable the flow buttons.
    this.networkService.internetStatus.subscribe(
        status => this.flowSequenceButtons.allowButtonClick = status);

    // Subscribe to flow state
    this.flowSequence.flowState.subscribe(state => {
      this.updateStepNumber(state);

      // Actions to be taken when certain active/next step is shown.
      switch (state.activeStep.id) {
        case 'logout':
          this.updateAnalytics('/logout');
          this.completeReturn();
          break;
        case 'return':
          this.updateAnalytics('/return');
          // Ensure that can proceed isn't disabled because of a previous check.
          this.flowSequenceButtons.canProceed = true;
          this.returnInstructions.reloadAnimation();
          break;
        case 'return_instructions':
          this.updateAnalytics('/return_instructions');
          break;
        // Checks if surveys are required and if so that they are filled out.
        case 'survey':
          this.updateAnalytics('/survey');
          if (this.surveyAnswer == null &&
              this.surveyComponent.answerRequired) {
            this.flowSequenceButtons.canProceed = false;
            this.survey.answer.subscribe(val => {
              this.surveyAnswer = val;
              if (this.surveyAnswer !== null) {
                this.flowSequenceButtons.canProceed = true;
              } else {
                this.flowSequenceButtons.canProceed = false;
              }
            });
          }
          break;
        default:
          break;
      }
    });
  }

  /**
   * Update the step number based off of information from the current flow
   * state.
   * @param state FlowState of the application.
   */
  updateStepNumber(state: FlowState) {
    if (state.optional) {
      if (state.optional.activeStepNumber === 0 ||
          state.optional.activeStepNumber) {
        this.currentStep = state.optional.activeStepNumber;
      }
    }
  }

  /** Opens the managment window and closes the offboarding flow. */
  backToManage() {
    this.bg.openView('manage');
    this.bg.closeView('offboarding');
  }

  /**
   * Sends message to background service to close the 'offboarding' chrome
   * application window.
   */
  closeApplication() {
    this.flowSequenceButtons.canProceed = false;
    if (this.surveyAnswer) {
      this.surveyComponent.waiting();
      this.survey.submitSurvey(this.surveyAnswer)
          .subscribe(
              () => {
                this.surveyComponent.ready();
                this.bg.closeView('offboarding');
              },
              error => {
                console.error('The survey failed to submit: ', error);
                this.bg.closeView('offboarding');
              });
    } else {
      this.bg.closeView('offboarding');
    }
  }

  // Survey related items
  /**
   * Setup and configure the survey component.
   */
  surveySetup() {
    this.surveyComponent.surveyDescription =
        `Before you go, we have one more question to ask about your loaner
experience. This will help us improve and maintain the loaner program.`;

    this.surveyComponent.surveyType = SurveyType.Return;
  }

  /**
   * Handle changes from survey related items including the SurveyComponent.
   */
  surveyListener() {
    this.survey.answer.subscribe(val => this.surveyAnswer = val);
    this.surveyComponent.surveyError.subscribe(val => {
      const message = `We are unable to retrieve the survey at the moment,
continue using the app as normal.`;
      this.failure.register(message, FailType.Network, FailAction.Ignore, val);
    });
  }

  completeReturn() {
    if (!this.returnCompleted) {
      this.loan.return().subscribe(
          () => {
            this.returnCompleted = true;
          },
          error => {
            const message = `Something went wrong when marking the device
returned. Please return to the nearest shelf and we will take care of the
rest.`;
            this.failure.register(
                message, FailType.Other, FailAction.Quit, error);
          });
    }
  }
}

@NgModule({
  bootstrap: [AppRoot],
  declarations: [AppRoot],
  imports: [
    AnalyticsModule,
    AnimationMenuModule,
    BrowserAnimationsModule,
    BrowserModule,
    FlexLayoutModule,
    HttpModule,
    MaterialModule,
    LoanerProgressModule,
    FailureModule,
    LoanerReturnInstructionsModule,
    LoanerTextCardModule,
    SurveyModule,
    LoanerFlowSequenceModule,
  ],
  providers: [
    {provide: PlatformLocation, useClass: ChromeAppPlatformLocation},
    ConfigService,
    Background,
    NetworkService,
    Survey,
    Loan,
    // useValue used in this provide since useFactory with parameters doesn't
    // work in AOT land.
    {
      provide: ApiConfig,
      useValue: apiConfigFactory(
          new ConfigService().endpointsApiUrl,
          new ConfigService().chromeApiUrl),
    },
  ],
})
export class AppModule {
}
