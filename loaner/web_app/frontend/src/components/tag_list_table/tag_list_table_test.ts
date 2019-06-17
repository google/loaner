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
import {ComponentFixture, ComponentFixtureAutoDetect, discardPeriodicTasks, fakeAsync, TestBed, tick,} from '@angular/core/testing';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {RouterTestingModule} from '@angular/router/testing';
import {TagService} from '../../services/tag';
import {TagServiceMock} from '../../testing/mocks';

import {TagListTable, TagListTableModule} from './index';


describe('TagListTable', () => {
  let fixture: ComponentFixture<TagListTable>;
  let tagListTable: TagListTable;

  beforeEach(fakeAsync(() => {
    TestBed
        .configureTestingModule({
          imports: [
            HttpClientTestingModule,
            RouterTestingModule,
            TagListTableModule,
            BrowserAnimationsModule,
          ],
          providers: [
            {provide: ComponentFixtureAutoDetect, useValue: true},
            {provide: TagService, useClass: TagServiceMock},
          ],
        })
        .compileComponents();

    tick();
    fixture = TestBed.createComponent(TagListTable);
    tagListTable = fixture.debugElement.componentInstance;

    discardPeriodicTasks();
    fixture.detectChanges();
  }));

  it('creates the TagList', () => {
    expect(tagListTable).toBeDefined();
  });

  it('renders the default card title and subtitle', () => {
    const compiled = fixture.debugElement.nativeElement;
    expect(compiled.querySelector('.mat-card-title').innerText)
        .toContain('Tags');
    expect(compiled.querySelector('.mat-card-subtitle').innerText)
        .toContain('Create and edit tags');
  });

  it('renders the table header', () => {
    const compiled = fixture.debugElement.nativeElement;
    expect(compiled.querySelector('.mat-header-cell').innerText)
        .toContain('Status');
  });
});
