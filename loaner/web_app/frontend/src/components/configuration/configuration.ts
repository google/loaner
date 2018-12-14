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

import {Component, OnInit, ViewChild} from '@angular/core';
import {NgForm} from '@angular/forms';
import {Router} from '@angular/router';

import {CONFIG} from '../../app.config';
import {Config, ConfigType, ConfigUpdate, DeviceIdentifierModeType, SearchIndexType} from '../../models/config';
import {ConfigService} from '../../services/config';
import {SearchService} from '../../services/search';

/**
 * Component that renders the Bootstrap flow of the application.
 */
@Component({
  selector: 'loaner-configuration',
  styleUrls: ['configuration.scss'],
  templateUrl: 'configuration.ng.html',
})
export class Configuration implements OnInit {
  config: Config = this.config;
  searchIndexType = SearchIndexType;
  deviceIdentifierModeType = DeviceIdentifierModeType;

  @ViewChild(NgForm) configurationForm: NgForm = this.configurationForm;

  shelfAuditEmailToList = '';

  constructor(
      readonly router: Router, private readonly configService: ConfigService,
      // tslint:disable-next-line:no-unused-variable used on template.
      private readonly searchService: SearchService) {}

  ngOnInit() {
    this.configService.list().subscribe(config => {
      this.config = new Config(config);
      this.shelfAuditEmailToList =
          this.arrayToCsv(this.config.shelfAuditEmailTo!);
    });
  }

  get appName() {
    return CONFIG.appName;
  }

  /**
   * Converts a string array to a comma-separated string (CSV).
   */
  arrayToCsv(array: string[]): string {
    let emailString = '';
    for (const email of array) {
      emailString += `${email.trim()},\n`;
    }
    return emailString;
  }

  /**
   * Converts a comma or newline separated string to an array.
   */
  csvToArray(csvString: string): string[] {
    let splitString = csvString.replace('\n', ',');
    splitString = splitString.replace(',,', ',');
    let stringArray = splitString.split(',');
    stringArray = stringArray.map(str => str.trim());
    return stringArray;
  }

  /** Updates the config service with dirty values in the form. */
  save(form: NgForm) {
    const updates: ConfigUpdate[] = [];
    for (const realKey of Object.keys(form.controls)) {
      const realValue = form.controls[realKey];
      let key: string = realKey;
      let value: string|number|boolean|string[] = realValue.value;
      if (realValue.dirty) {
        let type: ConfigType;
        if (key.endsWith('_number')) {
          type = ConfigType.INTEGER;
          key = key.replace('_number', '');
          value = value as number;
        } else if (key.endsWith('_string')) {
          type = ConfigType.STRING;
          key = key.replace('_string', '');
          value = value as string;
        } else if (key.endsWith('_boolean')) {
          type = ConfigType.BOOLEAN;
          key = key.replace('_boolean', '');
          value = value as boolean;
        } else if (key.endsWith('_list')) {
          type = ConfigType.LIST;
          key = key.replace('_list', '');
          value = this.csvToArray(value as string);
        } else {
          console.error('Failed to determine type of key', key);
          continue;
        }
        updates.push({
          key,
          type,
          value,
        });
      }
    }
    this.configService.updateAll(updates);
  }
}
