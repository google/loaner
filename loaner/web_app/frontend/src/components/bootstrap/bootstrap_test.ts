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

  it('should create the Bootstrap', () => {
    expect(bootstrap).toBeDefined();
  });

  it('should show each task after the bootstrap button is clicked', () => {
    const bootstrapService: BootstrapService = TestBed.get(BootstrapService);
    spyOn(bootstrapService, 'run').and.returnValue(of({
      tasks: [
        {name: 'task1'},
        {name: 'task2'},
        {name: 'task3'},
      ]
    }));
    bootstrap.bootstrapApplication();
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    expect(compiled.textContent).toContain('task1');
    expect(compiled.textContent).toContain('task2');
    expect(compiled.textContent).toContain('task3');
  });

  it('should mark successful tasks with a checkmark icon', () => {
    const bootstrapService: BootstrapService = TestBed.get(BootstrapService);
    spyOn(bootstrapService, 'getStatus').and.returnValue(of({
      tasks: [
        {name: 'task1', success: true, timestamp: (new Date().valueOf())}
      ]
    }));
    fakeAsync(() => {
      bootstrap.bootstrapApplication();
      fixture.detectChanges();
      const compiled = fixture.debugElement.nativeElement;
      expect(compiled.textContent).toContain('check');
    });
  });

  it('should mark failed task with an error icon', () => {
    const bootstrapService: BootstrapService = TestBed.get(BootstrapService);
    spyOn(bootstrapService, 'getStatus').and.returnValue(of({
      tasks: [
        {name: 'task1', success: false, timestamp: (new Date().valueOf())},
      ]
    }));
    fakeAsync(() => {
      bootstrap.bootstrapApplication();
      fixture.detectChanges();
      const compiled = fixture.debugElement.nativeElement;
      expect(compiled.textContent).toContain('error');
    });
  });

  it('should call bootstrap run service once bootstrapApplication is called.',
     () => {
       const bootstrapService: BootstrapService = TestBed.get(BootstrapService);
       spyOn(bootstrapService, 'run');
       fakeAsync(() => {
         bootstrap.bootstrapApplication();
         expect(bootstrapService.run).toHaveBeenCalled();
       });
     });

  it('should provide details about failed tasks', () => {
    const bootstrapService: BootstrapService = TestBed.get(BootstrapService);
    const failureDetails = 'failure details';
    spyOn(bootstrapService, 'getStatus').and.returnValue(of({
      tasks: [
        {
          name: 'task1',
          success: false,
          timestamp: (new Date().valueOf()),
          details: failureDetails
        },
      ]
    }));
    fakeAsync(() => {
      bootstrap.bootstrapApplication();
      fixture.detectChanges();
      const compiled = fixture.debugElement.nativeElement;
      expect(compiled.textContent).toContain(failureDetails);
    });
  });

  it('should show the task description when possible', () => {
    const bootstrapService: BootstrapService = TestBed.get(BootstrapService);
    const taskDescription = 'Literally describes the task!';
    spyOn(bootstrapService, 'getStatus').and.returnValue(of({
      tasks: [
        {name: 'task1', description: taskDescription},
      ]
    }));
    fakeAsync(() => {
      bootstrap.bootstrapApplication();
      fixture.detectChanges();
      const compiled = fixture.debugElement.nativeElement;
      expect(compiled.textContent).toContain(taskDescription);
    });
  });
});
