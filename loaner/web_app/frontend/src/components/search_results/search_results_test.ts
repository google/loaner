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

import {HttpClientModule} from '@angular/common/http';
import {ComponentFixture, ComponentFixtureAutoDetect, fakeAsync, flushMicrotasks, TestBed, tick} from '@angular/core/testing';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {RouterTestingModule} from '@angular/router/testing';

import {DeviceService} from '../../services/device';
import {SearchService} from '../../services/search';
import {ShelfService} from '../../services/shelf';
import {LoanerSnackBar} from '../../services/snackbar';
import {DEVICE_1, DEVICE_2, DeviceServiceMock, ShelfServiceMock} from '../../testing/mocks';

import {SearchResultsComponent, SearchResultsModule} from './index';

describe('SearchResultsComponent', () => {
  let fixture: ComponentFixture<SearchResultsComponent>;
  let searchResults: SearchResultsComponent;

  beforeEach(fakeAsync(() => {
    TestBed
        .configureTestingModule({
          imports: [
            HttpClientModule,
            RouterTestingModule,
            SearchResultsModule,
            BrowserAnimationsModule,
          ],
          providers: [
            {provide: ComponentFixtureAutoDetect, useValue: true},
            {provide: DeviceService, useClass: DeviceServiceMock},
            {provide: ShelfService, useClass: ShelfServiceMock},
            LoanerSnackBar,
            SearchService,
          ],
        })
        .compileComponents();

    flushMicrotasks();

    fixture = TestBed.createComponent(SearchResultsComponent);
    searchResults = fixture.debugElement.componentInstance;

    tick(1000);
  }));

  it('should create the SearchResults', () => {
    expect(searchResults).toBeTruthy();
  });

  it('should retrieve and display the mock devices.', () => {
    searchResults.model = 'device';
    searchResults.query = 'chromebook';
    searchResults.search(searchResults.model, searchResults.query);
    fixture.detectChanges();

    expect(searchResults.results).toContain(DEVICE_1);
    expect(searchResults.results).toContain(DEVICE_2);
    expect(fixture.nativeElement.querySelectorAll('mat-list-item')[0].innerText)
        .toContain('321653');
    expect(fixture.nativeElement.querySelectorAll('mat-list-item')[1].innerText)
        .toContain('236135');
    expect(searchResults.resultsLength)
        .toEqual(TestBed.get(DeviceService).dataChange.getValue().length);
  });

  it('should retrieve and display the mock shelfs.', () => {
    searchResults.model = 'shelf';
    searchResults.query = 'Friendly';
    searchResults.search(searchResults.model, searchResults.query);
    fixture.detectChanges();

    expect(fixture.nativeElement.querySelectorAll('mat-list-item')[0].innerText)
        .toContain('Friendly name 1');
    expect(fixture.nativeElement.querySelectorAll('mat-list-item')[1].innerText)
        .toContain('Friendly name 2');
    expect(searchResults.resultsLength).toEqual(5);
  });
});
