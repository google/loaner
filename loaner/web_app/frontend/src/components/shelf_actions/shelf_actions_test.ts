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

import {ComponentFixture, fakeAsync, flushMicrotasks, TestBed, tick} from '@angular/core/testing';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {ActivatedRoute} from '@angular/router';
import {RouterTestingModule} from '@angular/router/testing';
import {of} from 'rxjs';

import {ConfigService} from '../../services/config';
import {Dialog} from '../../services/dialog';
import {ShelfService} from '../../services/shelf';
import {ActivatedRouteMock, ConfigServiceMock, ShelfServiceMock, TEST_SHELF} from '../../testing/mocks';

import {ShelfActionsCard, ShelfActionsModule} from '.';

describe('ShelfActionsComponent', () => {
  let fixture: ComponentFixture<ShelfActionsCard>;
  let componentInstance: ShelfActionsCard;

  beforeEach(fakeAsync(() => {
    TestBed
        .configureTestingModule({
          imports: [
            RouterTestingModule,
            ShelfActionsModule,
            BrowserAnimationsModule,
          ],
          providers: [
            Dialog,
            {provide: ActivatedRoute, useClass: ActivatedRouteMock},
            {provide: ConfigService, useClass: ConfigServiceMock},
            {provide: ShelfService, useClass: ShelfServiceMock},
          ],
        })
        .compileComponents();

    flushMicrotasks();

    fixture = TestBed.createComponent(ShelfActionsCard);
    componentInstance = fixture.debugElement.componentInstance;
  }));

  it('creates the ShelfActionsCard', () => {
    expect(componentInstance).toBeDefined();
  });

  it('renders proper mat-card-title when editing a shelf', () => {
    componentInstance.editing = true;
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    expect(compiled.querySelector('.mat-card-title').textContent)
        .toContain('Update shelf');
  });

  it('has a disabled create button at beginning', () => {
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    const createButton = compiled.querySelector('button');
    expect(createButton).toBeTruthy();
  });

  it('has a Location named input', () => {
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    const input = compiled.querySelector('input[name="location"]');
    expect(input).toBeTruthy();
    expect(input.getAttribute('required')).toBe('');
  });

  it('has a Friendly Name named input', () => {
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    const input = compiled.querySelector('input[name="name"]');
    expect(input).toBeTruthy();
  });

  it('has a Capacity named input', () => {
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    const input = compiled.querySelector('input[name="capacity"]');
    expect(input).toBeTruthy();
    expect(input.getAttribute('required')).toBe('');
    expect(input.getAttribute('min')).toBe('1');
  });

  it('has a Latitude named input', () => {
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    const input = compiled.querySelector('input[name="latitude"]');
    expect(input).toBeTruthy();
  });

  it('has a Longitude named input', () => {
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    const input = compiled.querySelector('input[name="longitude"]');
    expect(input).toBeTruthy();
  });

  it('has a Altitude named input', () => {
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    const input = compiled.querySelector('input[name="altitude"]');
    expect(input).toBeTruthy();
  });

  it('has a Responsible for Audit select', () => {
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    const input = compiled.querySelector('input[name="altitude"]');
    expect(input).toBeTruthy();
  });

  it('has an Enable shelf audit notifications slide toggle', () => {
    componentInstance.editing = true;
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    const input =
        compiled.querySelector('input[name="auditNotificationEnabled"]');
    expect(input).toBeTruthy();
  });

  it('sets the audit notifications toggle to checked appropriately',
     fakeAsync(() => {
       componentInstance.editing = true;
       fixture.detectChanges();
       tick();
       componentInstance.shelf = TEST_SHELF;
       componentInstance.shelf.auditNotificationEnabled = true;
       fixture.detectChanges();
       tick();

       const compiled = fixture.debugElement.nativeElement;
       const slideToggleChecked = compiled.querySelector(
           'mat-slide-toggle[name="auditNotificationEnabled"].mat-checked');
       expect(slideToggleChecked).toBeTruthy();
     }));

  it('sets the audit notifications toggle to unchecked appropriately',
     fakeAsync(() => {
       componentInstance.editing = true;
       componentInstance.shelf = TEST_SHELF;
       componentInstance.shelf.auditNotificationEnabled = false;
       fixture.detectChanges();
       tick();

       const compiled = fixture.debugElement.nativeElement;
       const slideToggleUnchecked = compiled.querySelector(
           'mat-slide-toggle[name="auditNotificationEnabled"]');
       expect(slideToggleUnchecked).toBeTruthy();
       const slideToggleChecked = compiled.querySelector(
           'mat-slide-toggle[name="auditNotificationEnabled"].mat-checked');
       expect(slideToggleChecked).toBeFalsy();
     }));

  it('changes audit notifications on the model when toggled false to true',
     () => {
     });

  it('changes audit notifications on the model when toggled true to false',
     () => {
     });

  it('calls the shelf api when creating a shelf', () => {
    const shelfService: ShelfService = TestBed.get(ShelfService);
    spyOn(shelfService, 'create').and.callThrough();

    fixture.detectChanges();

    componentInstance.shelf = TEST_SHELF;

    componentInstance.create();

    expect(shelfService.create).toHaveBeenCalledWith(TEST_SHELF);
    expect(componentInstance.shelf.name).toBe('');
  });

  it('loads a shelf with populated properties when updating.', () => {
    componentInstance.editing = true;

    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    let input = compiled.querySelector('input[name="location"]');
    expect(input).toBeTruthy();
    expect(input.getAttribute('ng-reflect-model')).toBe('Location 1');

    input = compiled.querySelector('input[name="name"]');
    expect(input).toBeTruthy();
    expect(input.getAttribute('ng-reflect-model')).toBe('Friendly name 1');

    input = compiled.querySelector('input[name="capacity"]');
    expect(input).toBeTruthy();
    expect(input.getAttribute('ng-reflect-model')).toBe('10');
  });

  it('calls shelf api update and get new value when updating a shelf.', () => {
    const shelfService: ShelfService = TestBed.get(ShelfService);
    spyOn(shelfService, 'update').and.returnValue(of([TEST_SHELF]));
    spyOn(shelfService, 'getShelf').and.returnValue(of([TEST_SHELF]));

    componentInstance.shelf = TEST_SHELF;
    componentInstance.editing = true;
    componentInstance.update();

    fixture.detectChanges();
    expect(shelfService.update).toHaveBeenCalledWith(TEST_SHELF);
    expect(shelfService.getShelf).toHaveBeenCalledWith('Location 1');
  });
});
