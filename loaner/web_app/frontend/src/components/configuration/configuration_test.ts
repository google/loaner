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
import {FormsModule} from '@angular/forms';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {RouterTestingModule} from '@angular/router/testing';
import {of} from 'rxjs';

import {ConfigService} from '../../services/config';
import {SearchService} from '../../services/search';
import {ConfigServiceMock, SearchServiceMock} from '../../testing/mocks';

import {Configuration, ConfigurationModule} from '.';

describe('ConfigurationComponent', () => {
  let fixture: ComponentFixture<Configuration>;
  let configuration: Configuration;

  beforeEach(fakeAsync(() => {
    TestBed
        .configureTestingModule({
          imports: [
            ConfigurationModule,
            FormsModule,
            BrowserAnimationsModule,
            RouterTestingModule,
          ],
          providers: [
            {provide: ConfigService, useClass: ConfigServiceMock},
            {provide: SearchService, useClass: SearchServiceMock},
          ],
        })
        .compileComponents();

    flushMicrotasks();

    fixture = TestBed.createComponent(Configuration);
    configuration = fixture.debugElement.componentInstance;
  }));

  it('creates the Configuration', () => {
    expect(configuration).toBeDefined();
  });

  it('calls config service to get config', fakeAsync(() => {
       const configService: ConfigService = TestBed.get(ConfigService);
       spyOn(configService, 'list').and.callThrough();
       fixture.detectChanges();
       expect(configService.list).toHaveBeenCalledTimes(1);
     }));

  it('renders a known boolean config', () => {
    fixture.detectChanges();
    const bootstrapStartedMatCheckboxElement =
        fixture.debugElement.nativeElement.querySelector(
            'mat-checkbox[name="bootstrap_started_boolean"]');
    expect(bootstrapStartedMatCheckboxElement).toBeDefined();
  });

  it('renders a known string (email) config', () => {
    fixture.detectChanges();
    const groupResponsibleForAuditInput =
        fixture.debugElement.nativeElement.querySelector(
            'input[name="responsible_for_audit_list"]');
    expect(groupResponsibleForAuditInput).toBeDefined();
    expect(groupResponsibleForAuditInput.type).toBe('email');
  });

  it('renders a known string config', () => {
    fixture.detectChanges();
    const bannerImageInput = fixture.debugElement.nativeElement.querySelector(
        'input[name="img_banner_primary_string"]');
    expect(bannerImageInput).toBeDefined();
    expect(bannerImageInput.type).toBe('text');
  });

  it('renders a known integer config', () => {
    fixture.detectChanges();
    const shelfAuditIntervalInput =
        fixture.debugElement.nativeElement.querySelector(
            'input[name="shelf_audit_interval_number"]');
    expect(shelfAuditIntervalInput).toBeDefined();
    expect(shelfAuditIntervalInput.type).toBe('number');
  });

  it('renders a known list config', () => {
    fixture.detectChanges();
    const auditEmailRecipientsListElement =
        fixture.debugElement.nativeElement.querySelector(
            'input[name="shelf_audit_email_to_list"]');
    expect(auditEmailRecipientsListElement).toBeDefined();
  });

  it('converts a csv string to an array', () => {
    fixture.detectChanges();
    const expected = ['a', 'b', 'c'];
    const commaOnlyValue = configuration.csvToArray('a, b, c');
    expect(commaOnlyValue).toEqual(expected);

    const commaNewlineValue = configuration.csvToArray('a,\nb,\nc\n');
    expect(commaNewlineValue).toEqual(expected);
  });

  it('converts an array to a csv', () => {
    fixture.detectChanges();
    const expected = 'a,\nb,\nc,\n';
    const listValue = ['a', 'b', 'c'];
    expect(configuration.arrayToCsv(listValue)).toEqual(expected);
  });

  it('unlocks the submit button when any input value is changed',
     fakeAsync(() => {
       fixture.detectChanges();
       const compiled = fixture.debugElement.nativeElement;
       const submitButtonBeforeChange =
           compiled.querySelector('button[type="submit"]');
       expect(submitButtonBeforeChange).toBeDefined();
       expect(
           (submitButtonBeforeChange as HTMLElement).getAttribute('disabled'))
           .toBeDefined();
       const supportContactInput =
           compiled.querySelector('input[name="support_contact_string"]');
       (supportContactInput as HTMLInputElement).value =
           'support_contact_test@localhost';
       (supportContactInput as HTMLInputElement)
           .dispatchEvent(new Event('input'));
       fixture.detectChanges();
       const submitButtonAfterChange =
           compiled.querySelector('button[type="submit"]');
       expect(submitButtonAfterChange).toBeDefined();
       expect(submitButtonAfterChange.getAttribute('disabled')).toBeFalsy();
     }));

  it('calls config service after updating an input and triggering submit',
     fakeAsync(() => {
       fixture.detectChanges();
       const compiled = fixture.debugElement.nativeElement;
       const configService: ConfigService = TestBed.get(ConfigService);
       spyOn(configService, 'updateAll').and.returnValue(of());
       const supportContactInput =
           compiled.querySelector('input[name="support_contact_string"]');
       expect(supportContactInput).toBeDefined();
       supportContactInput.value = 'support_contact_test@localhost';
       supportContactInput.dispatchEvent(new Event('input'));
       fixture.detectChanges();
       const formElement = compiled.querySelector('form');
       formElement.dispatchEvent(new Event('submit'));
       fixture.detectChanges();
       expect(configService.updateAll).toHaveBeenCalledTimes(1);
     }));

  it('calls reindex service when a reindex button is clicked', fakeAsync(() => {
       fixture.detectChanges();
       const compiled = fixture.debugElement.nativeElement;
       const searchService: SearchService = TestBed.get(SearchService);
       spyOn(searchService, 'reindex').and.returnValue(of());
       const reindexDevices =
           compiled.querySelector('button[name="reindex-devices"]');
       reindexDevices.click();
       expect(searchService.reindex)
           .toHaveBeenCalledWith(configuration.searchIndexType.Device);
       expect(searchService.reindex).toHaveBeenCalledTimes(1);
       const reindexShelves =
           compiled.querySelector('button[name="reindex-shelves"]');
       reindexShelves.click();
       expect(searchService.reindex)
           .toHaveBeenCalledWith(configuration.searchIndexType.Shelf);
       expect(searchService.reindex).toHaveBeenCalledTimes(2);
       const reindexUsers =
           compiled.querySelector('button[name="reindex-users"]');
       reindexUsers.click();
       expect(searchService.reindex)
           .toHaveBeenCalledWith(configuration.searchIndexType.User);
       expect(searchService.reindex).toHaveBeenCalledTimes(3);
     }));

  it('calls clearIndex service when a clear index button is clicked',
     fakeAsync(() => {
       fixture.detectChanges();
       const compiled = fixture.debugElement.nativeElement;
       const searchService: SearchService = TestBed.get(SearchService);
       spyOn(searchService, 'clearIndex').and.returnValue(of());
       const clearIndexDevices =
           compiled.querySelector('button[name="clear-index-devices"]');
       clearIndexDevices.click();
       expect(searchService.clearIndex)
           .toHaveBeenCalledWith(configuration.searchIndexType.Device);
       expect(searchService.clearIndex).toHaveBeenCalledTimes(1);
       const clearIndexShelves =
           compiled.querySelector('button[name="clear-index-shelves"]');
       clearIndexShelves.click();
       expect(searchService.clearIndex)
           .toHaveBeenCalledWith(configuration.searchIndexType.Shelf);
       expect(searchService.clearIndex).toHaveBeenCalledTimes(2);
       const clearIndexUsers =
           compiled.querySelector('button[name="clear-index-users"]');
       clearIndexUsers.click();
       expect(searchService.clearIndex)
           .toHaveBeenCalledWith(configuration.searchIndexType.User);
       expect(searchService.clearIndex).toHaveBeenCalledTimes(3);
     }));
});
