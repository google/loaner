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

import {HttpClientTestingModule} from '@angular/common/http/testing';
import {ComponentFixture, TestBed} from '@angular/core/testing';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {RouterTestingModule} from '@angular/router/testing';
import {RoleService} from '../../services/role';
import {RoleServiceMock} from '../../testing/mocks';

import {RoleEditorTable, RoleEditorTableModule} from './index';

describe('RoleEditorTable', () => {
  let fixture: ComponentFixture<RoleEditorTable>;
  let roleEditorTable: RoleEditorTable;

  beforeEach(() => {
    TestBed
        .configureTestingModule({
          imports: [
            HttpClientTestingModule,
            RouterTestingModule,
            RoleEditorTableModule,
            BrowserAnimationsModule,
          ],
          providers: [
            {provide: RoleService, useClass: RoleServiceMock},
          ],
        })
        .compileComponents();

    fixture = TestBed.createComponent(RoleEditorTable);
    roleEditorTable = fixture.debugElement.componentInstance;

    fixture.detectChanges();
  });

  it('creates the RoleEditor', () => {
    expect(roleEditorTable).toBeDefined();
  });

  it('renders the default card title and subtitle', () => {
    const compiled = fixture.debugElement.nativeElement;
    expect(compiled.querySelector('.mat-card-title').innerText)
        .toContain('Role Editor');
    expect(compiled.querySelector('.mat-card-subtitle').innerText)
        .toContain('View, add, edit, or delete existing roles');
  });

  it('renders the title field "Name" inside .mat-header-row', () => {
    const compiled = fixture.debugElement.nativeElement;
    expect(compiled.querySelector('.mat-header-row').innerText)
        .toContain('Name');
  });

  it('renders the title field "Associated Group" inside .mat-header-row',
     () => {
       const compiled = fixture.debugElement.nativeElement;
       expect(compiled.querySelector('.mat-header-row').innerText)
           .toContain('Associated Group');
     });

  it('renders the title field "Permissions" inside .mat-header-row', () => {
    const compiled = fixture.debugElement.nativeElement;
    expect(compiled.querySelector('.mat-header-row').innerText)
        .toContain('Permissions');
  });
});
