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

import {LoanerFlowSequenceButtons} from './flow_sequence_buttons';
import {NavigationLabels, Step} from './index';
import {MaterialModule} from './material_module';

describe('LoanerFlowSequenceButtons', () => {
  let component: LoanerFlowSequenceButtons;
  let fixture: ComponentFixture<LoanerFlowSequenceButtons>;
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
            LoanerFlowSequenceButtons,
          ],
          imports: [
            FlexLayoutModule,
            MaterialModule,
          ],
        })
        .compileComponents();

    fixture = TestBed.createComponent(LoanerFlowSequenceButtons);
    component = fixture.debugElement.componentInstance;
    component.steps = steps;
    component.navLabels = labels;
  });

  it('should compile', () => {
    expect(component).toBeTruthy();
  });

  it('should show only the forward button when on step 0', () => {
    expect(component.maxStepNumber).toBe(3);
    component.currentStepNumber = 0;
    fixture.detectChanges();
    expect(fixture.debugElement.nativeElement.querySelectorAll('button').length)
        .toBe(1);
  });

  it('should show both forward and back buttons when in middle of sequence',
     () => {
       expect(component.maxStepNumber).toBe(3);

       component.currentStepNumber = 1;
       fixture.detectChanges();
       expect(
           fixture.debugElement.nativeElement.querySelectorAll('button').length)
           .toBe(2);
     });

  it('should show the back and finished button when on last step', () => {
    expect(component.maxStepNumber).toBe(3);
    component.currentStepNumber = 3;
    fixture.detectChanges();
    expect(fixture.debugElement.nativeElement.querySelectorAll('button').length)
        .toBe(2);
    expect(fixture.debugElement.nativeElement.querySelectorAll('button')[1]
               .getAttribute('aria-label'))
        .toContain('All done');
  });

  it('should show the correct aria labels', () => {
    expect(component.maxStepNumber).toBe(3);
    component.currentStepNumber = 2;
    fixture.detectChanges();
    expect(fixture.debugElement.nativeElement.querySelectorAll('button')[0]
               .getAttribute('aria-label'))
        .toContain('Previous step');
    expect(fixture.debugElement.nativeElement.querySelectorAll('button')[1]
               .getAttribute('aria-label'))
        .toContain('Next step');
    component.currentStepNumber = 3;
    fixture.detectChanges();
    expect(fixture.debugElement.nativeElement.querySelectorAll('button')[1]
               .getAttribute('aria-label'))
        .toContain('All done');
  });

  it('forward button should send flow forward', fakeAsync(() => {
       component.currentStepNumber = 0;
       expect(component.currentStepNumber).toBe(0);
       component.flowState.subscribe(state => {
         expect(state.optional!.activeStepNumber).toBe(1);
       });
       component.forward.subscribe(val => {
         expect(val).toBeTruthy();
         component.flowState.next({
           activeStep: steps[component.currentStepNumber],
           previousStep: steps[component.currentStepNumber - 1],
           optional: {
             activeStepNumber: 1,
           }
         });
       });
       component.goForward();
     }));

  it('forward button should NOT send flow forward', fakeAsync(() => {
       component.currentStepNumber = 0;
       expect(component.currentStepNumber).toBe(0);
       component.flowState.subscribe(state => {
         expect(state.optional!.activeStepNumber).toBe(1);
       });
       component.canProceed = false;
       component.forward.subscribe(val => {
         expect(val).toBeFalsy();
         component.flowState.next({
           activeStep: steps[component.currentStepNumber],
           previousStep: steps[component.currentStepNumber - 1],
           optional: {
             activeStepNumber: 1,
           }
         });
       });
       component.goForward();
     }));

  it('back button should send flow backward', fakeAsync(() => {
       component.currentStepNumber = 2;
       expect(component.currentStepNumber).toBe(2);
       component.flowState.subscribe(state => {
         expect(state.optional!.activeStepNumber).toBe(1);
       });
       component.back.subscribe(val => {
         expect(val).toBeTruthy();
         component.flowState.next({
           activeStep: steps[component.currentStepNumber],
           previousStep: steps[component.currentStepNumber - 1],
           optional: {
             activeStepNumber: 1,
           }
         });
       });
       component.goBack();
     }));

  it('finished button should send flow to finished state', fakeAsync(() => {
       component.currentStepNumber = 3;
       expect(component.maxStepNumber).toBe(component.currentStepNumber);
       component.flowState.subscribe(state => {
         expect(state.optional!.flowFinished).toBe(true);
         expect(state.activeStep).toBe(steps[component.currentStepNumber]);
       });
       component.finished.subscribe(val => {
         expect(val).toBeTruthy();
         component.flowState.next({
           activeStep: steps[component.currentStepNumber],
           previousStep: steps[component.currentStepNumber - 1],
           optional: {
             flowFinished: true,
           }
         });
       });
       component.finishFlow();
     }));
});
