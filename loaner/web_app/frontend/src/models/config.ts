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

export enum SearchIndexType {
  Device = 'device',
  Shelf = 'shelf',
  User = 'user',
}

/**
 * Device identifier supported modes, needs to match modes on
 * web_app/config_defaults.yaml
 */
export enum DeviceIdentifierModeType {
  ASSET_TAG = 'asset_tag',
  SERIAL_NUMBER = 'serial_number',
  BOTH_REQUIRED = 'both_required'
}

export declare interface GetConfigRequest {
  name: string;
  config_type: ConfigType;
}

export declare interface ConfigUpdate {
  key: string;
  type: ConfigType;
  value: string|number|boolean|string[];
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

export declare interface UpdateConfigRequestSingle {
  name: string;
  config_type: ConfigType;
  string_value?: string;
  integer_value?: number;
  boolean_value?: boolean;
  list_value?: string[];
}

export declare interface UpdateConfigRequest {
  config: UpdateConfigRequestSingle[];
}

export class Config {
  allowGuestMode?: boolean;
  anonymousSurveys?: boolean;
  auditInterval?: number;
  bootstrapCompleted?: boolean;
  bootstrapStarted?: boolean;
  datastoreVersion?: number;
  deviceIdentifierMode?: string;  // 'serial_number' could be enum
  guestModeTimeoutInHours?: number;
  imgBannerPrimary?: string;
  imgButtonManage?: string;
  loanDuration?: number;
  loanDurationEmail?: boolean;
  maximumLoanDuration?: number;
  orgUnitPrefix?: string;
  reminderDelay?: number;
  requireSurveys?: boolean;
  responsibleForAudit?: string[];
  returnGracePeriod?: number;
  syncRolesUserQuerySize?: number;
  shelfAudit?: boolean;
  shelfAuditEmail?: boolean;
  shelfAuditEmailTo?: string[];
  shelfAuditInterval?: number;  // in hours
  supportContact?: string;
  timeoutGuestMode?: boolean;
  unenrollOU?: string;
  silentOnboarding?: boolean;

  constructor(response: ConfigResponse[]) {
    // tslint:disable:no-unnecessary-type-assertion Fix after b/110225001
    this.allowGuestMode =
        response.find(a => a.name === 'allow_guest_mode')!.boolean_value as
        boolean;
    this.anonymousSurveys =
        response.find(a => a.name === 'anonymous_surveys')!.boolean_value as
        boolean;
    this.auditInterval =
        response.find(a => a.name === 'audit_interval')!.integer_value as
        number;
    this.bootstrapCompleted =
        response.find(a => a.name === 'bootstrap_completed')!.boolean_value as
        boolean;
    this.bootstrapStarted =
        response.find(a => a.name === 'bootstrap_started')!.boolean_value as
        boolean;
    this.datastoreVersion =
        response.find(a => a.name === 'datastore_version')!.integer_value as
        number;
    this.deviceIdentifierMode =
        response.find(a => a.name === 'device_identifier_mode')!.string_value as
        string;
    this.guestModeTimeoutInHours =
        response.find(
                    a => a.name ===
                        'guest_mode_timeout_in_hours')!.integer_value as number;
    this.imgBannerPrimary =
        response.find(a => a.name === 'img_banner_primary')!.string_value as
        string;
    this.imgButtonManage =
        response.find(a => a.name === 'img_button_manage')!.string_value as
        string;
    this.loanDuration =
        response.find(a => a.name === 'loan_duration')!.integer_value as number;
    this.loanDurationEmail =
        response.find(a => a.name === 'loan_duration_email')!.boolean_value as
        boolean;
    this.maximumLoanDuration =
        response.find(a => a.name === 'maximum_loan_duration')!.integer_value as
        number;
    this.orgUnitPrefix =
        response.find(a => a.name === 'org_unit_prefix')!.string_value as
        string;
    this.reminderDelay =
        response.find(a => a.name === 'reminder_delay')!.integer_value as
        number;
    this.requireSurveys =
        response.find(a => a.name === 'require_surveys')!.boolean_value as
        boolean;
    this.responsibleForAudit =
        response.find(a => a.name === 'responsible_for_audit')!.list_value as
        string[];
    this.returnGracePeriod =
        response.find(a => a.name === 'return_grace_period')!.integer_value as
        number;
    this.syncRolesUserQuerySize =
        response.find(
                    a => a.name ===
                        'sync_roles_user_query_size')!.integer_value as number;
    this.shelfAudit =
        response.find(a => a.name === 'shelf_audit')!.boolean_value as boolean;
    this.shelfAuditEmail =
        response.find(a => a.name === 'shelf_audit_email')!.boolean_value as
        boolean;
    this.shelfAuditEmailTo =
        response.find(a => a.name === 'shelf_audit_email_to')!.list_value as
            string[] ||
        [];
    this.shelfAuditInterval =
        response.find(a => a.name === 'shelf_audit_interval')!.integer_value as
        number;
    this.supportContact =
        response.find(a => a.name === 'support_contact')!.string_value as
        string;
    this.timeoutGuestMode =
        response.find(a => a.name === 'timeout_guest_mode')!.boolean_value as
        boolean;
    this.unenrollOU =
        response.find(a => a.name === 'unenroll_ou')!.string_value as string;
    this.silentOnboarding =
        response.find(a => a.name === 'silent_onboarding')!.boolean_value as
        boolean;
    // tslint:enable:no-unnecessary-type-assertion
  }
}
