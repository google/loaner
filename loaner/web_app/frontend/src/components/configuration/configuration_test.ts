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
import {FormsModule} from '@angular/forms';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {RouterTestingModule} from '@angular/router/testing';

import {ConfigService} from '../../services/config';
import {ConfigServiceMock} from '../../testing/mocks';

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
            'input[name="responsible_for_audit_string"]');
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

  it('calls the config service update method when submitted', () => {
    fixture.detectChanges();
    const configService: ConfigService = TestBed.get(ConfigService);
    spyOn(configService, 'update');
    // make a change to unlock the submit button
    configuration.config.supportContact += 'test!';
    fixture.detectChanges();
    fakeAsync(() => {
      const submitButton = fixture.debugElement.nativeElement.querySelector(
          'form button[type="submit"]');
      submitButton.click();
      fixture.detectChanges();
      expect(configService.update).toHaveBeenCalled();
    });
  });

  it('calls the config update service for each changed value', () => {
    fixture.detectChanges();
    const configService: ConfigService = TestBed.get(ConfigService);
    spyOn(configService, 'update');
    // make a change to unlock the submit button
    configuration.config.supportContact += 'test!';
    configuration.config.shelfAuditInterval = 48;
    fixture.detectChanges();
    fakeAsync(() => {
      const submitButton = fixture.debugElement.nativeElement.querySelector(
          'form button[type="submit"]');
      submitButton.click();
      fixture.detectChanges();
      expect(configService.update).toHaveBeenCalledTimes(2);
    });
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
});
