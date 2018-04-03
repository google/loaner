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

/** Represents the options for a Chrome App Window. */
declare interface ChromeWindowOptions {
  alwaysOnTop?: boolean;
  bounds: {height: number; width: number;};
  frame?: string;
  id: string;
  resizable?: boolean;
}

/** Represents the options for a Chrome Notification. */
declare interface ChromeNotificationOptions {
  iconUrl: string;
  message: string;
  requireInteraction: boolean;
  title: string;
  type: string;
}

/** Represents the damaged reason for the HTTP request. */
declare interface DamagedReasonRequest {
  damaged_reason?: string;
  device: {chrome_device_id: string};
}

/** Represents the request that is made for requesting device info. */
declare interface DeviceInfoRequest {
  chrome_device_id: string;
}

/** Represents the HTTP response with device info. */
declare interface DeviceInfoResponse {
  assigned_user?: string;
  assignment_date?: Date;
  current_ou?: string;
  damaged?: boolean;
  damaged_reason?: string;
  device_model?: string;
  due_date?: Date;
  enrolled?: boolean;
  guest_enabled?: boolean;
  guest_permitted?: boolean;
  last_heartbeat?: Date;
  last_known_healthy?: Date;
  locked?: boolean;
  lost?: boolean;
  mark_pending_return_date?: Date;
  max_extend_date?: Date;
  ou_changed_date?: Date;
  return_date?: Date;
}

/** Represents the loan extension for the HTTP request. */
declare interface ExtendRequest {
  device: {chrome_device_id: string};
  extend_date: string;
}

/** Represents the request that is made for enabling guest mode. */
declare interface GuestModeRequest {
  chrome_device_id: string;
}

/** Interface for the heartbeat configuration parameters. */
declare interface HeartbeatConfiguration {
  duration: number;
  name: string;
  url: string;
}

/** Response type from the heartbeat endpoint. */
declare interface HeartbeatResponse {
  is_enrolled: boolean;
  start_assignment: boolean;
}

/** Represents the response we receive upon getting loan information. */
declare interface LoanResponse {
  due_date: Date;
  max_extend_date: Date;
  given_name: string;
  guest_enabled: boolean;
  guest_permitted: boolean;
}

/** Represents the information we request for loan info. */
declare interface LoanRequest {
  device_id: string;
  need_name?: boolean;
}

/** Represents the return request */
declare interface ReturnRequest {
  chrome_device_id: string;
}

/** Represents the request that is made for resuming a loan. */
declare interface ResumeLoanRequest {
  chrome_device_id: string;
}

/** Represents the runtime requests that are made via Chrome Messages. */
declare interface RuntimeRequest {
  close?: boolean;
  currentViewName?: string;
  keepOpen?: boolean;
  onboardingComplete?: boolean;
  open?: boolean;
  view?: string;
}
