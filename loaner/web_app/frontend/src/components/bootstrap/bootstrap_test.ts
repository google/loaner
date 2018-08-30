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
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {RouterTestingModule} from '@angular/router/testing';
import {of} from 'rxjs';

import {BootstrapService} from '../../services/bootstrap';
import {BootstrapServiceMock} from '../../testing/mocks';

import {Bootstrap, BootstrapModule} from '.';

describe('BootstrapComponent', () => {
  let fixture: ComponentFixture<Bootstrap>;
  let bootstrap: Bootstrap;

  beforeEach(fakeAsync(() => {
    TestBed
        .configureTestingModule({
          imports: [
            BootstrapModule,
            BrowserAnimationsModule,
            RouterTestingModule,
          ],
          providers: [
            {provide: BootstrapService, useClass: BootstrapServiceMock},
          ],
        })
        .compileComponents();

    flushMicrotasks();

    fixture = TestBed.createComponent(Bootstrap);
    bootstrap = fixture.debugElement.componentInstance;
  }));

  it('creates the bootstrap component', () => {
    expect(bootstrap).toBeDefined();
  });

  it('calls bootstrap service when the begin button is clicked', () => {
    const bootstrapService: BootstrapService = TestBed.get(BootstrapService);
    spyOn(bootstrapService, 'run');
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    const beginButton = compiled.querySelector('.beginButton');
    beginButton.dispatchEvent(new Event('click'));
    fixture.detectChanges();
    expect(bootstrapService.run).toHaveBeenCalledTimes(1);
  });

  it('renders each task in an expansion panel when bootstrap begins', () => {
    const bootstrapService: BootstrapService = TestBed.get(BootstrapService);
    spyOn(bootstrapService, 'run').and.returnValue(of({
      tasks: [
        {name: 'task1'},
        {name: 'task2'},
        {name: 'task3'},
      ]
    }));
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    const beginButton = compiled.querySelector('.beginButton');
    beginButton.dispatchEvent(new Event('click'));
    fixture.detectChanges();
    const expansionPanels =
        Array.from(compiled.querySelectorAll('mat-expansion-panel'));
    expect(expansionPanels.length).toBe(3);
    const expansionPanelsAsString =
        expansionPanels
            .map(expansionPanel => (expansionPanel as HTMLElement).textContent)
            .toString();
    expect(expansionPanelsAsString).toContain('task1');
    expect(expansionPanelsAsString).toContain('task2');
    expect(expansionPanelsAsString).toContain('task3');
  });

  it('marks successful tasks with a checkmark icon', () => {
    const bootstrapService: BootstrapService = TestBed.get(BootstrapService);
    spyOn(bootstrapService, 'run').and.returnValue(of({
      tasks: [
        {name: 'task1', success: true},
        {name: 'task2', success: false},
        {name: 'task3'},
      ]
    }));
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    const beginButton = compiled.querySelector('.beginButton');
    beginButton.dispatchEvent(new Event('click'));
    fixture.detectChanges();
    const successfulTaskExpansionPanel =
        Array.from(compiled.querySelectorAll('mat-expansion-panel'))
            .find(
                expansionPanel => (expansionPanel as HTMLElement)
                                      .textContent!.includes('task1'));
    expect(successfulTaskExpansionPanel).toBeDefined();
    const successfulTaskIcon =
        (successfulTaskExpansionPanel as HTMLElement).querySelector('mat-icon');
    expect(successfulTaskIcon).toBeDefined();
    expect((successfulTaskIcon as HTMLElement).textContent)
        .toContain('check_circle');
  });

  it('marks failed tasks with an alert icon', () => {
    const bootstrapService: BootstrapService = TestBed.get(BootstrapService);
    spyOn(bootstrapService, 'run').and.returnValue(of({
      tasks: [
        {name: 'task1', success: true},
        {name: 'task2', success: false, timestamp: 1},
        {name: 'task3'},
      ]
    }));
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    const beginButton = compiled.querySelector('.beginButton');
    beginButton.dispatchEvent(new Event('click'));
    fixture.detectChanges();
    const failedTaskExpansionPanel =
        Array.from(compiled.querySelectorAll('mat-expansion-panel'))
            .find(
                expansionPanel => (expansionPanel as HTMLElement)
                                      .textContent!.includes('task2'));
    expect(failedTaskExpansionPanel).toBeDefined();
    const failedTaskIcon =
        (failedTaskExpansionPanel as HTMLElement).querySelector('mat-icon');
    expect(failedTaskIcon).toBeDefined();
    expect((failedTaskIcon as HTMLElement).textContent).toContain('error');
  });

  it('marks in-progress tasks with a progress spinner', () => {
    const bootstrapService: BootstrapService = TestBed.get(BootstrapService);
    spyOn(bootstrapService, 'run').and.returnValue(of({
      tasks: [
        {name: 'task1', success: true},
        {name: 'task2', success: false, timestamp: 1},
        {name: 'task3'},
      ]
    }));
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    const beginButton = compiled.querySelector('.beginButton');
    beginButton.dispatchEvent(new Event('click'));
    fixture.detectChanges();
    const inProgressTaskExpansionPanel =
        Array.from(compiled.querySelectorAll('mat-expansion-panel'))
            .find(
                expansionPanel => (expansionPanel as HTMLElement)
                                      .textContent!.includes('task3'));
    expect(inProgressTaskExpansionPanel).toBeDefined();
    const inProgressTaskSpinner = (inProgressTaskExpansionPanel as HTMLElement)
                                      .querySelector('mat-spinner');
    expect(inProgressTaskSpinner).toBeDefined();
  });

  it('displays the task description instead of the task name whenever possible',
     () => {
       const bootstrapService: BootstrapService = TestBed.get(BootstrapService);
       spyOn(bootstrapService, 'run').and.returnValue(of({
         tasks: [
           {name: 'task1', description: 'testing task #1'},
         ]
       }));
       fixture.detectChanges();
       const compiled = fixture.debugElement.nativeElement;
       const beginButton = compiled.querySelector('.beginButton');
       (beginButton as HTMLElement).dispatchEvent(new Event('click'));
       fixture.detectChanges();
       const taskExpansionPanel = compiled.querySelector('mat-expansion-panel');
       expect(taskExpansionPanel).toBeDefined();
       expect(taskExpansionPanel.textContent).not.toContain('task1');
       expect(taskExpansionPanel.textContent).toContain('testing task #1');
     });

  it('displays failure information in an expansion panel', () => {
    const bootstrapService: BootstrapService = TestBed.get(BootstrapService);
    spyOn(bootstrapService, 'run').and.returnValue(of({
      tasks: [
        {
          name: 'task1',
          description: 'testing task #1',
          success: false,
          details: 'testing task #1 failed'
        },
      ]
    }));
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    const beginButton = compiled.querySelector('.beginButton');
    beginButton.dispatchEvent(new Event('click'));
    fixture.detectChanges();
    const taskExpansionPanel = compiled.querySelector('mat-expansion-panel');
    const taskExpansionPanelDetails = taskExpansionPanel.querySelector('p');
    expect(taskExpansionPanel).toBeDefined();
    expect(taskExpansionPanelDetails).toBeDefined();
    expect(taskExpansionPanelDetails.textContent)
        .toContain('testing task #1 failed');
  });
});
