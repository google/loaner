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

import {Injectable} from '@angular/core';
import {Response} from '@angular/http';
import {Observable} from 'rxjs';
import {map} from 'rxjs/operators';

import * as config from '../models/config';

import {ApiService} from './api';

/** Class to connect to the backend's Config's Service API methods. */
@Injectable()
export class ConfigService extends ApiService {
  /** Implements ApiService's apiEndpoint requirement. */
  apiEndpoint = 'config';

  /**
   * Gets a string config from the backend.
   * @param name Config name to be retrieved from the backend.
   */
  getStringConfig(name: string): Observable<string> {
    return this.getConfig(name, config.ConfigType.STRING)
        .pipe(map(response => response.string_value!));
  }

  /**
   * Gets a number config from the backend.
   * @param name Config name to be retrieved from the backend.
   */
  getNumberConfig(name: string): Observable<number> {
    return this.getConfig(name, config.ConfigType.INTEGER)
        .pipe(map(response => response.integer_value!));
  }

  /**
   * Gets a boolean config from the backend.
   * @param name Config name to be retrieved from the backend.
   */
  getBooleanConfig(name: string): Observable<boolean> {
    return this.getConfig(name, config.ConfigType.BOOLEAN)
        .pipe(map(response => response.boolean_value!));
  }

  /**
   * Gets a list config from the backend.
   * @param name Config name to be retrieved from the backend.
   */
  getListConfig(name: string): Observable<string[]> {
    return this.getConfig(name, config.ConfigType.LIST)
        .pipe(map(response => response.list_value!));
  }

  /**
   * Get specific config setting from the backend.
   * @param name Config name to be retrieved from the backend.
   * @param configType The type of the requested setting that's being
   *     retrieved.
   */
  private getConfig(name: string, configType: config.ConfigType):
      Observable<config.ConfigResponse> {
    const request: config.GetConfigRequest = {
      'name': name,
      'config_type': configType,
    };
    return this.get<config.ConfigResponse>('get', request);
  }

  /** Gets the list of configs from the backend. */
  list(): Observable<config.ConfigResponse[]> {
    return this.get<config.ListConfigsResponse>('list').pipe(
        map(res => res['configs'] || []));
  }

  /**
   * Updates the given config setting with a new value.
   * @param name Setting id to be updated on the backend.
   * @param configType The type of the setting that's being updated.
   * @param value New value to be set in the up to date config setting.
   */
  update(
      name: string, configType: config.ConfigType,
      value: string|number|boolean|string[]) {
    const request: config.UpdateConfigRequest = {
      'name': name,
      'config_type': configType,
    };

    switch (configType) {
      case config.ConfigType.STRING: {
        request['string_value'] = value as string;
        break;
      }
      case config.ConfigType.INTEGER: {
        request['integer_value'] = value as number;
        break;
      }
      case config.ConfigType.BOOLEAN: {
        request['boolean_value'] = value as boolean;
        break;
      }
      case config.ConfigType.LIST: {
        request['list_value'] = value as string[];
        break;
      }
      default: {
        throw new TypeError(`Config type ${
            config.ConfigType
                [configType]} is not valid for updating config ${
            name}.`);
      }
    }

    this.post('update', request).subscribe(() => {
      this.snackBar.open(
          `Config ${name} updated with the value ${value}.`);
    });
  }
}
