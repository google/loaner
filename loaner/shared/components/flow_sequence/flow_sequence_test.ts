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

import {ComponentFixture, fakeAsync, TestBed} from '@angular/core/testing';
import {FlexLayoutModule} from '@angular/flex-layout';

import {LoanerFlowSequence} from './flow_sequence';
import {LoanerFlowSequenceButtons} from './flow_sequence_buttons';
import {NavigationLabels, Step} from './index';
import {MaterialModule} from './material_module';

describe('LoanerFlowSequence', () => {
  let component: LoanerFlowSequence;
  let fixture: ComponentFixture<LoanerFlowSequence>;
  let buttonsFixture: ComponentFixture<LoanerFlowSequenceButtons>;
  let buttonsComponent: LoanerFlowSequenceButtons;

  const steps: Step[] = [
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

  const labels: NavigationLabels = {
    previous: {aria: 'Previous step', toolTip: 'Previous Step'},
    next: {aria: 'Next step', toolTip: 'Next Step'},
    done: {
      aria: 'All done! Your loaner can now be returned.',
      toolTip: 'All done! Your loaner can now be returned.',
    },
  };

  beforeEach(() => {
    TestBed
        .configureTestingModule({
          declarations: [
            LoanerFlowSequence,
            LoanerFlowSequenceButtons,
          ],
          imports: [
            FlexLayoutModule,
            MaterialModule,
          ],
        })
        .compileComponents();

    fixture = TestBed.createComponent(LoanerFlowSequence);
    buttonsFixture = TestBed.createComponent(LoanerFlowSequenceButtons);
    component = fixture.debugElement.componentInstance;
    buttonsComponent = buttonsFixture.debugElement.componentInstance;
    component.steps = steps;
    fixture.detectChanges();
  });

  it('should compile', () => {
    expect(component).toBeTruthy();
  });

  it('should update max step number', () => {
    expect(component.maxStepNumber).toBe(3);
  });

  describe('flowState', () => {
    it('should emit  when step changes forward.', fakeAsync(() => {
         component.currentStepNumber = 0;
         component.flowState.subscribe((val) => {
           expect(val.activeStep.title)
               .toBe('One final question before you go');
           expect(val.previousStep.title)
               .toBe('Get ready to return this device');
           expect(val.optional!.activeStepNumber).toBe(1);
           expect(val.optional!.maxStepNumber).toBe(3);
         });
         component.goForward();
       }));
    it('should emit when goForward is triggered.', fakeAsync(() => {
         component.currentStepNumber = 2;
         component.flowState.subscribe((val) => {
           expect(val.activeStep.title)
               .toBe('One final question before you go');
           expect(val.previousStep.title)
               .toBe('Are you sure you want to return this device?');
           expect(val.optional!.activeStepNumber).toBe(1);
           expect(val.optional!.maxStepNumber).toBe(3);
         });
         component.goBack();
       }));

    it('should emit when goBack is triggered', fakeAsync(() => {
         component.currentStepNumber = 2;
         component.flowState.subscribe((val) => {
           expect(val.activeStep.title)
               .toBe('One final question before you go');
           expect(val.previousStep.title)
               .toBe('Are you sure you want to return this device?');
           expect(val.optional!.activeStepNumber).toBe(1);
           expect(val.optional!.maxStepNumber).toBe(3);
         });
         component.goBack();
       }));

    it('should emit when finishFlow is triggered', fakeAsync(() => {
         component.currentStepNumber = 2;
         component.flowState.subscribe((val) => {
           expect(val.optional!.flowFinished).toBeTruthy();
         });
         component.finishFlow();
       }));

    it('should emit when goToStep is run', () => {
      component.currentStepNumber = 2;
      component.flowState.subscribe((val) => {
        expect(val.activeStep.title).toBe('Get ready to return this device');
        expect(val.previousStep.title)
            .toBe('Are you sure you want to return this device?');
      });
      component.goToStep('return');
    });
  });

  describe('activeStep and previous step', () => {
    it('should emit values when step is changed', () => {
      component.currentStepNumber = 0;
      component.activeStep.subscribe((val) => {
        expect(val.title).toBe('One final question before you go');
      });
      component.previousStep.subscribe((val) => {
        expect(val.title).toBe('Get ready to return this device');
      });
      component.goForward();
    });
  });

  describe('with LoanerFlowSequenceButtons', () => {
    beforeEach(() => {
      buttonsComponent.navLabels = labels;
      buttonsComponent.steps = steps;
      component.flowSequenceButtons = buttonsComponent;
      component.setupFlowButtonsListener();
      fixture.detectChanges();
    });

    describe('should update parent FlowState', () => {
      it('when forward button is pressed', () => {
        component.currentStepNumber = 0;
        component.flowState.subscribe(state => {
          expect(state.activeStep).toBe(steps[1]);
          expect(state.optional!.activeStepNumber).toBe(1);
          expect(state.previousStep).toBe(steps[0]);
        });
        buttonsComponent.goForward();
      });

      it('when back button is pressed', () => {
        component.currentStepNumber = 2;
        component.flowState.subscribe(state => {
          expect(state.activeStep).toBe(steps[1]);
          expect(state.optional!.activeStepNumber).toBe(1);
          expect(state.previousStep).toBe(steps[2]);
        });
        buttonsComponent.goBack();
      });

      it('when finished button is pressed', () => {
        component.currentStepNumber = 3;
        expect(component.maxStepNumber).toBe(component.currentStepNumber);
        component.flowState.subscribe(state => {
          expect(state.optional!.flowFinished).toBe(true);
          expect(state.activeStep).toBe(steps[3]);
          expect(state.previousStep).toBe(steps[2]);
        });
        buttonsComponent.finishFlow();
      });
    });
  });
});
