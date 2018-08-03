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

  it('calls config service to update with a single change', () => {
    fixture.whenStable().then(() => {
      const configService: ConfigService = TestBed.get(ConfigService);
      spyOn(configService, 'updateAll');
      fixture.detectChanges();
      configuration.config.supportContact += 'test!';
      fixture.detectChanges();
      tick(250);
      const compiled = fixture.debugElement.nativeElement;
      const supportContactElement =
          compiled.querySelector('input[name="support_contact_string"]') as
          HTMLInputElement;
      expect(supportContactElement.value).toContain('test!');
      supportContactElement.dispatchEvent(new Event('input'));

      const submitButton = compiled.querySelector('button[type="submit"]');
      submitButton.click();
      fixture.detectChanges();
      tick(250);
      expect(configService.updateAll).toHaveBeenCalledWith([{
        key: 'support_contact',
        type: 'string',
        value: (configuration.config.supportContact as string),
      }]);
      expect(configService.updateAll).toHaveBeenCalledTimes(1);
    });
  });

  it('calls config service to update with multiple changes', () => {
    fixture.whenStable().then(() => {
      const configService: ConfigService = TestBed.get(ConfigService);
      spyOn(configService, 'updateAll');
      fixture.detectChanges();
      configuration.config.supportContact += 'test!';
      configuration.config.auditInterval = 999;
      fixture.detectChanges();
      tick(250);
      const compiled = fixture.debugElement.nativeElement;
      // change #1
      const supportContactElement =
          compiled.querySelector('input[name="support_contact_string"]') as
          HTMLInputElement;
      expect(supportContactElement.value).toContain('test!');
      supportContactElement.dispatchEvent(new Event('input'));

      // change #2
      const auditIntervalElement =
          compiled.querySelector('input[name="audit_interval_number"]') as
          HTMLInputElement;
      expect(auditIntervalElement.value)
          .toBe(configuration.config.auditInterval.toString());
      auditIntervalElement.dispatchEvent(new Event('input'));

      const submitButton = compiled.querySelector('button[type="submit"]');
      submitButton.click();
      fixture.detectChanges();
      tick(250);
      expect(configService.updateAll).toHaveBeenCalledWith([
        {
          key: 'support_contact',
          type: 'string',
          value: (configuration.config.supportContact as string),
        },
        {
          key: 'audit_interval',
          type: 'number',
          value: (configuration.config.auditInterval),
        }
      ]);
      expect(configService.updateAll).toHaveBeenCalledTimes(1);
    });
  });
});
