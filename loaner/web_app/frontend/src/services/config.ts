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
   * Updates all provided config values on the backend.
   * @param configUpdates the list of config names (keys), and their associated
   *     type and value. Example:
   * [
   *   {key: 'allow_guest_mode', type: ConfigType.BOOLEAN, value: true},
   *   {key: 'loan_duration', type: ConfigType.INTEGER, value: 10},
   * ]
   */
  updateAll(configUpdates: config.ConfigUpdate[]) {
    const configUpdateRequestSingles: config.UpdateConfigRequestSingle[] =
        configUpdates.map(configUpdate => {
          const updateConfigRequestSingle: config.UpdateConfigRequestSingle = {
            name: configUpdate.key,
            config_type: configUpdate.type
          };
          switch (configUpdate.type) {
            case config.ConfigType.STRING: {
              updateConfigRequestSingle['string_value'] =
                  configUpdate.value as string;
              break;
            }
            case config.ConfigType.INTEGER: {
              updateConfigRequestSingle['integer_value'] =
                  configUpdate.value as number;
              break;
            }
            case config.ConfigType.BOOLEAN: {
              updateConfigRequestSingle['boolean_value'] =
                  configUpdate.value as boolean;
              break;
            }
            case config.ConfigType.LIST: {
              updateConfigRequestSingle['list_value'] =
                  configUpdate.value as string[];
              break;
            }
            default: {
              throw new TypeError(`Config type ${
                  config.ConfigType[configUpdate.type]} is not valid.`);
            }
          }
          return updateConfigRequestSingle;
        });

    // Send the request
    const updateConfigRequest: config.UpdateConfigRequest = {
      config: configUpdateRequestSingles,
    };
    this.post('update', updateConfigRequest).subscribe(() => {
      this.snackBar.open(`Config updated.`);
    });
  }
}
