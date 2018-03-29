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

import {ComponentFixture, TestBed} from '@angular/core/testing';
import {MatDialogRef} from '@angular/material';

import {LostDialogComponent, LostModule} from './index';

/** Mock material DialogRef. */
class MatDialogRefMock {}

describe('LostDialogComponent', () => {
  let compiled: HTMLElement;
  let component: LostDialogComponent;
  let fixture: ComponentFixture<LostDialogComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [
        LostModule,
      ],
      providers: [{
        provide: MatDialogRef,
        useClass: MatDialogRefMock,
      }],
    });
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(LostDialogComponent);
    compiled = fixture.debugElement.nativeElement;
    component = fixture.debugElement.componentInstance;
    component.ready();
    fixture.detectChanges();
  });

  it('creates dialog component', () => {
    expect(component).toBeDefined();
  });

  it('renders the yes button', () => {
    fixture.detectChanges();
    expect(compiled.querySelector('#yes')!.textContent).toContain('Yes');
  });

  it('renders the cancel button', () => {
    fixture.detectChanges();
    expect(compiled.querySelector('#cancel')!.textContent).toContain('Cancel');
  });

  it('shows the correct title', () => {
    fixture.detectChanges();
    expect(compiled.querySelector('.mat-dialog-title')!.textContent)
        .toBe('Oh no!');
  });

  it('shows and hide the loader', () => {
    component.waiting();
    fixture.detectChanges();
    expect(compiled.querySelector('loader')).toBeDefined();
    component.ready();
    fixture.detectChanges();
    expect(compiled.querySelector('loader')).toBeNull();
  });

  it('renders the close button', () => {
    component.toBeSubmitted = false;
    component.ready();
    fixture.detectChanges();
    expect(compiled.querySelector('#close')!.textContent).toContain('Close');
  });
});
