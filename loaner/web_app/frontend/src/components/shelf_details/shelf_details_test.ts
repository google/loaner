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

import {Component} from '@angular/core';
import {ComponentFixture, fakeAsync, flushMicrotasks, TestBed} from '@angular/core/testing';
import {By} from '@angular/platform-browser';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {RouterTestingModule} from '@angular/router/testing';
import {Observable, of} from 'rxjs';

import {Shelf} from '../../models/shelf';
import {Dialog} from '../../services/dialog';
import {ShelfService} from '../../services/shelf';
import {ShelfServiceMock} from '../../testing/mocks';
import {TEST_SHELF} from '../../testing/mocks';

import {ShelfDetails, ShelfDetailsModule} from '.';

@Component({
  preserveWhitespaces: true,
  template: '',
})
class DummyComponent {
}

describe('ShelfDetailsComponent', () => {
  let fixture: ComponentFixture<ShelfDetails>;
  let shelfDetails: ShelfDetails;

  beforeEach(fakeAsync(() => {
    TestBed
        .configureTestingModule({
          declarations: [DummyComponent],
          imports: [
            RouterTestingModule.withRoutes([
              {path: 'shelves', component: DummyComponent},
            ]),
            ShelfDetailsModule,
            BrowserAnimationsModule,
          ],
          providers: [
            {provide: ShelfService, useClass: ShelfServiceMock},
          ],
        })
        .compileComponents();

    flushMicrotasks();

    fixture = TestBed.createComponent(ShelfDetails);
    shelfDetails = fixture.debugElement.componentInstance;
    shelfDetails.shelf = TEST_SHELF;
  }));

  it('should create the ShelfDetails', () => {
    expect(shelfDetails).toBeDefined();
  });

  it('should render card title in a mat-card-title', () => {
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    expect(compiled.querySelector('.mat-card-title').textContent)
        .toContain('Shelf Details');
  });

  it('should render the location inside loaner-viewonly-label', () => {
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    expect(compiled.querySelector('.location').textContent)
        .toContain('Location');
  });

  it('should render the friendly location inside loaner-viewonly-label', () => {
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    expect(compiled.querySelector('.friendlyName').textContent)
        .toContain('Friendly Name');
  });

  it('should render the capacity inside loaner-viewonly-label', () => {
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    expect(compiled.querySelector('.capacity').textContent)
        .toContain('Capacity');
  });

  it('should render the latitude inside loaner-viewonly-label', () => {
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    expect(compiled.querySelector('.latitude').textContent)
        .toContain('Latitude');
  });

  it('should render the longitude inside loaner-viewonly-label', () => {
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    expect(compiled.querySelector('.longitude').textContent)
        .toContain('Longitude');
  });

  it('should render the altitude inside loaner-viewonly-label', () => {
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    expect(compiled.querySelector('.altitude').textContent)
        .toContain('Altitude');
  });

  it('should render the responsible inside loaner-viewonly-label', () => {
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    expect(compiled.querySelector('.responsible').textContent)
        .toContain('Responsible');
  });

  it('renders the shelf audit notifications inside loaner-viewonly-label',
     () => {
       fixture.detectChanges();
       const compiled = fixture.debugElement.nativeElement;
       expect(
           compiled
               .querySelector('loaner-viewonly-label.auditNotificationEnabled')
               .textContent)
           .toContain('Audit notification');
     });

  it('should call openDialog when button is clicked.',
     () => {
     });

  it('should call disable when delete a shelf.', () => {
    const shelfService: ShelfService = TestBed.get(ShelfService);
    spyOn(shelfService, 'disable');
    const dialog: Dialog = TestBed.get(Dialog);
    spyOn(dialog, 'confirm').and.returnValue(of(true));
    shelfDetails.openDisableDialog();

    fixture.detectChanges();

    expect(shelfService.disable).toHaveBeenCalled();
  });
});
