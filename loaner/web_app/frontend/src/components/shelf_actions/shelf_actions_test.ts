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
import {ActivatedRoute} from '@angular/router';
import {RouterTestingModule} from '@angular/router/testing';

import {ConfigService} from '../../services/config';
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

  it('should create the ShelfActionsCard', () => {
    expect(componentInstance).toBeDefined();
  });

  it('should render proper mat-card-title when editing a shelf', () => {
    componentInstance.editing = true;
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    expect(compiled.querySelector('.mat-card-title').textContent)
        .toContain('Update shelf');
  });

  it('should have a disabled create button at beginning', () => {
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    const createButton = compiled.querySelector('button');
    expect(createButton).toBeTruthy();
  });

  it('should have a Location named input', () => {
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    const input = compiled.querySelector('input[name="location"]');
    expect(input).toBeTruthy();
    expect(input.getAttribute('required')).toBe('');
  });

  it('should have a Friendly Name named input', () => {
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    const input = compiled.querySelector('input[name="name"]');
    expect(input).toBeTruthy();
  });

  it('should have a Capacity named input', () => {
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    const input = compiled.querySelector('input[name="capacity"]');
    expect(input).toBeTruthy();
    expect(input.getAttribute('required')).toBe('');
    expect(input.getAttribute('min')).toBe('1');
  });

  it('should have a Latitude named input', () => {
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    const input = compiled.querySelector('input[name="latitude"]');
    expect(input).toBeTruthy();
  });

  it('should have a Longitude named input', () => {
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    const input = compiled.querySelector('input[name="longitude"]');
    expect(input).toBeTruthy();
  });

  it('should have a Altitude named input', () => {
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    const input = compiled.querySelector('input[name="altitude"]');
    expect(input).toBeTruthy();
  });

  it('should have a Responsible for Audit select', () => {
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    const input = compiled.querySelector('input[name="altitude"]');
    expect(input).toBeTruthy();
  });

  it('should call the shelf api when creating a shelf', () => {
    const shelfService: ShelfService = TestBed.get(ShelfService);
    spyOn(shelfService, 'create');

    fixture.detectChanges();

    componentInstance.shelf = TEST_SHELF;

    componentInstance.create();

    expect(shelfService.create).toHaveBeenCalledWith(TEST_SHELF);
    expect(componentInstance.shelf.name).toBe('');
  });

  it('should load a shelf with populated properties when updating.', () => {
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

  it('should call shelf api update when updating a shelf.', () => {
    const shelfService: ShelfService = TestBed.get(ShelfService);
    spyOn(shelfService, 'update');

    fixture.detectChanges();

    componentInstance.shelf = TEST_SHELF;
    componentInstance.currentLocation = TEST_SHELF.location;
    componentInstance.editing = true;
    componentInstance.update();
    expect(shelfService.update)
        .toHaveBeenCalledWith(TEST_SHELF.location, TEST_SHELF);
    expect(componentInstance.shelf.name).toBe('FAKE SHELF');
  });
});
