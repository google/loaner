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

/** Represents the runtime requests that are made via Chrome Messages. */
declare interface RuntimeRequest {
  close?: boolean;
  currentViewName?: string;
  keepOpen?: boolean;
  onboardingComplete?: boolean;
  open?: boolean;
  view?: string;
}
