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

export enum ConfigType {
  STRING = 'STRING',
  INTEGER = 'INTEGER',
  BOOLEAN = 'BOOLEAN',
  LIST = 'LIST',
}

export declare interface GetConfigRequest {
  name: string;
  config_type: ConfigType;
}

export declare interface ConfigResponse {
  name: string;
  config_type: ConfigType;
  string_value?: string;
  integer_value?: number;
  boolean_value?: boolean;
  list_value?: string[];
}

export declare interface ListConfigsResponse {
  configs: ConfigResponse[];
}

export declare interface UpdateConfigRequest {
  name: string;
  config_type: ConfigType;
  string_value?: string;
  integer_value?: number;
  boolean_value?: boolean;
  list_value?: string[];
}
