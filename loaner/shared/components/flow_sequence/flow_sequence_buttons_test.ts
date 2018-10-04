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

import {ComponentFixture, fakeAsync, flushMicrotasks, TestBed} from '@angular/core/testing';
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

  beforeEach(fakeAsync(() => {
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
    flushMicrotasks();

    fixture = TestBed.createComponent(LoanerFlowSequenceButtons);
    component = fixture.debugElement.componentInstance;
    component.steps = steps;
    component.navLabels = labels;
  }));

  it('should compile', () => {
    expect(component).toBeTruthy();
  });

  it('should show only the forward button when on step 0', () => {
    expect(component.maxStepNumber).toBe(3);
    component.currentStepNumber = 0;
    fixture.detectChanges();
    expect(fixture.debugElement.nativeElement.querySelectorAll('button').length)
        .toBe(1);
    expect(
        fixture.debugElement.nativeElement.querySelector('button').getAttribute(
            'aria-label'))
        .toContain('Next step');
  });

  it('should show both forward and back buttons when in middle of sequence',
     () => {
       component.currentStepNumber = 1;
       fixture.detectChanges();
       expect(
           fixture.debugElement.nativeElement.querySelectorAll('button').length)
           .toBe(2);
       expect(fixture.debugElement.nativeElement.querySelectorAll('button')[0]
                  .getAttribute('aria-label'))
           .toContain('Previous step');
       expect(fixture.debugElement.nativeElement.querySelectorAll('button')[1]
                  .getAttribute('aria-label'))
           .toContain('Next step');
     });

  it('should show the back and finished button when on last step', () => {
    component.currentStepNumber = 3;
    fixture.detectChanges();
    expect(fixture.debugElement.nativeElement.querySelectorAll('button').length)
        .toBe(2);
    expect(fixture.debugElement.nativeElement.querySelectorAll('button')[0]
               .getAttribute('aria-label'))
        .toContain('Previous step');
    expect(fixture.debugElement.nativeElement.querySelectorAll('button')[1]
               .getAttribute('aria-label'))
        .toContain('All done');
  });

  it('forward button should send flow forward', fakeAsync(() => {
       component.currentStepNumber = 0;
       fixture.detectChanges();
       expect(
           fixture.debugElement.nativeElement.querySelectorAll('button').length)
           .toBe(1);
       const compiled = fixture.debugElement.nativeElement;
       const forwardButton = compiled.querySelector('button') as HTMLElement;
       let forwardOutput = false;
       component.forward.subscribe(value => {
         forwardOutput = value;
       });

       forwardButton.click();
       expect(forwardOutput).toBeTruthy();
     }));

  it('forward button should NOT send flow forward when canProceed is false',
     fakeAsync(() => {
       component.currentStepNumber = 0;
       fixture.detectChanges();
       component.canProceed = false;
       expect(
           fixture.debugElement.nativeElement.querySelectorAll('button').length)
           .toBe(1);
       const compiled = fixture.debugElement.nativeElement;
       const forwardButton = compiled.querySelector('button') as HTMLElement;
       let forwardOutput = false;
       component.forward.subscribe(value => {
         forwardOutput = value;
       });

       forwardButton.click();
       expect(forwardOutput).toBeFalsy();
     }));


  it('forward button should NOT send flow forward when allowButtonClick is false',
     fakeAsync(() => {
       component.currentStepNumber = 0;
       fixture.detectChanges();
       component.allowButtonClick = false;
       expect(
           fixture.debugElement.nativeElement.querySelectorAll('button').length)
           .toBe(1);
       const compiled = fixture.debugElement.nativeElement;
       const forwardButton = compiled.querySelector('button') as HTMLElement;
       let forwardOutput = false;
       component.forward.subscribe(value => {
         forwardOutput = value;
       });

       forwardButton.click();
       expect(forwardOutput).toBeFalsy();
     }));

  it('back button should send flow backward', fakeAsync(() => {
       component.currentStepNumber = 2;
       fixture.detectChanges();
       component.allowButtonClick = true;
       expect(
           fixture.debugElement.nativeElement.querySelectorAll('button').length)
           .toBe(2);
       const compiled = fixture.debugElement.nativeElement;
       const backButton = compiled.querySelector('button') as HTMLElement;
       let backOutput = false;
       component.back.subscribe(value => {
         backOutput = value;
       });

       backButton.click();
       expect(backOutput).toBeTruthy();
     }));

  it('back button should NOT send flow backward', fakeAsync(() => {
       component.currentStepNumber = 2;
       fixture.detectChanges();
       component.allowButtonClick = false;
       expect(
           fixture.debugElement.nativeElement.querySelectorAll('button').length)
           .toBe(2);
       const compiled = fixture.debugElement.nativeElement;
       const backButton = compiled.querySelector('button') as HTMLElement;
       let backOutput = false;
       component.back.subscribe(value => {
         backOutput = value;
       });

       backButton.click();
       expect(backOutput).toBeFalsy();
     }));


  it('finished button should send flow to finished state', fakeAsync(() => {
       component.currentStepNumber = 3;
       fixture.detectChanges();
       expect(
           fixture.debugElement.nativeElement.querySelectorAll('button').length)
           .toBe(2);
       const compiled = fixture.debugElement.nativeElement;
       const finishedButton =
           compiled.querySelectorAll('button')[1] as HTMLElement;
       let finishedOutput = false;
       component.finished.subscribe(value => {
         finishedOutput = value;
       });

       finishedButton.click();
       expect(finishedOutput).toBeTruthy();
     }));

});
