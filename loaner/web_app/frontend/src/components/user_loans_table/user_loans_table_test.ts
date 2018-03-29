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

import {ComponentFixture, ComponentFixtureAutoDetect, fakeAsync, flushMicrotasks, TestBed,} from '@angular/core/testing';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {RouterTestingModule} from '@angular/router/testing';
import {DeviceService} from '../../services/device';
import {DeviceServiceMock} from '../../testing/mocks';

import {UserLoansTable, UserLoansTableModule} from '.';

describe('UserLoansTableComponent', () => {
  let fixture: ComponentFixture<UserLoansTable>;
  let userLoansTable: UserLoansTable;

  beforeEach(fakeAsync(() => {
    TestBed
        .configureTestingModule({
          imports: [
            RouterTestingModule,
            UserLoansTableModule,
            BrowserAnimationsModule,
          ],
          providers: [
            {provide: ComponentFixtureAutoDetect, useValue: true},
            {provide: DeviceService, useClass: DeviceServiceMock},
          ],
        })
        .compileComponents();

    flushMicrotasks();

    fixture = TestBed.createComponent(UserLoansTable);
    userLoansTable = fixture.debugElement.componentInstance;
  }));

  it('should create the userLoansTable', () => {
    expect(userLoansTable).toBeTruthy();
  });

  it('should render card title in a .mat-card-title',
     () => {
       fixture.detectChanges();
       const compiled = fixture.debugElement.nativeElement;
       expect(compiled.querySelector('.mat-card-title').textContent)
           .toContain('Returned Loans History');
     });

  it('should render title field "Identifier" inside .mat-header-row ',
     () => {
       fixture.detectChanges();
       const compiled = fixture.debugElement.nativeElement;
       expect(compiled.querySelector('.mat-header-row').textContent)
           .toContain('Identifier');
     });

  it('should render title field "Picked up" inside .mat-header-row ',
     () => {
       fixture.detectChanges();
       const compiled = fixture.debugElement.nativeElement;
       expect(compiled.querySelector('.mat-header-row').textContent)
           .toContain('Picked up');
     });

  it('should render title field "Returned" inside .mat-header-row ',
     () => {
       fixture.detectChanges();
       const compiled = fixture.debugElement.nativeElement;
       expect(compiled.querySelector('.mat-header-row').textContent)
           .toContain('Returned On');
     });
});
