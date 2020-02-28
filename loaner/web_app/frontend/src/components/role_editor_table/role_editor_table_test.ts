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
import {of} from 'rxjs';

import {Dialog} from '../../services/dialog';
import {RoleService} from '../../services/role';
import {RoleServiceMock, SET_OF_ROLES, TEST_ROLE_1, TEST_ROLE_2} from '../../testing/mocks';

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
        .toContain('View, create, edit, or delete existing roles');
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

  it('request to delete role after selecting a role to delete', () => {
    const roleService = TestBed.get(RoleService);
    const dialogService = TestBed.get(Dialog);
    const compiled = fixture.debugElement.nativeElement;
    const deleteSpy = spyOn(roleService, 'delete').and.callThrough();
    spyOn(roleService, 'list').and.returnValue(of(SET_OF_ROLES));
    spyOn(dialogService, 'confirm').and.returnValue(of(true));
    roleEditorTable.ngOnInit();
    const deleteRoleButtons =
        compiled.querySelectorAll('[aria-label="Delete role"]');

    console.error('Role 2 delete button: ', deleteRoleButtons[1]);

    deleteRoleButtons[1].click();

    expect(deleteSpy).not.toHaveBeenCalledWith(TEST_ROLE_1);
    expect(deleteSpy).toHaveBeenCalledWith(TEST_ROLE_2);
  });

  it('does not request to delete role if the dialog is declined', () => {
    const roleService = TestBed.get(RoleService);
    const dialogService = TestBed.get(Dialog);
    const deleteSpy = spyOn(roleService, 'delete').and.callThrough();
    spyOn(dialogService, 'confirm').and.returnValue(of(false));
    roleEditorTable.ngOnInit();

    expect(deleteSpy).not.toHaveBeenCalled();
  });
});
