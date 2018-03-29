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

/** Dev mode settings for testing purposes. */
export const DEV_MODE = false;
export const DEV_DEVICE_ID = 'sup3r-s3cr3t-d3v1c3-1d';
export const LOGGING = false;
export const TESTING = true;

/** Configurable heartbeat parameters. */
export const HEARTBEAT: HeartbeatConfiguration = {
  /** Heartbeat duration in minutes */
  duration: 1,
  /** Name of the heartbeat chrome alarm */
  name: 'heartbeat',
  /** URL for the heartbeat api endpoint */
  url: '/loaner/v1/chrome/heartbeat?device_id=',
};

/** Name of your Grab n Go program. */
export const PROGRAM_NAME = `Grab n Go`;


/**
 * IT contact information and text. Leave values blank if not needed
 * and they won't be populated on the Manage/Troubleshoot page.
 */
/** Text to be placed on the Manage/Troubleshoot page */
export const TROUBLESHOOTING_INFORMATION =
'Contact your IT department for assistance.';
/** Phone number of IT; Placed on Manage/Troubleshoot page */
export const IT_CONTACT_PHONE = '555 55 555';
/** Website of IT; Placed on Manage/Troubleshoot page */
export const IT_CONTACT_WEBSITE =
'https://support.google.com';
/** Email of IT; Placed on Manage/troubleshoot page */
export const IT_CONTACT_EMAIL = '';

/** This allows a background for the app to be set. */
export const BACKGROUND_LOGO_ENABLED = true;
export const BACKGROUND_LOGO = {
  url: '../assets/icons/gnglogo.png',
  altText: 'Grab n Go background logo',
};


/** Toolbar icon to be displayed on the top right of onboarding/offboarding. */
export const TOOLBAR_ICON_ENABLED = false;
export const TOOLBAR_ICON = {
  url: '../assets/icons/gng48.png',
  altText: 'GnG logo',
};

/**
 * Service that gives the URL for the appropriate API to make API calls.
 */
@Injectable()
export class APIService {
  devTrack = true;
  chromeEndpoint = {
    dev: 'https://chrome-dot-dev-app-engine-project.appspot.com/_ah/api',
    prod: 'https://chrome-dot-prod-app-engine-project.appspot.com/_ah/api',
  };
  standardEndpoint = {
    dev: 'https://endpoints-dot-dev-app-engine-project.appspot.com/_ah/api',
    prod: 'https://endpoints-dot-prod-app-engine-project.appspot.com/_ah/api'
  };

  constructor() {
    if (DEV_MODE) {
      this.devTrack = true;
    } else {
      this.devTrack = false;
    }
  }

  chrome(): string {
    if (this.devTrack) {
      return this.chromeEndpoint.dev;
    } else {
      return this.chromeEndpoint.prod;
    }
  }

  endpoints(): string {
    if (this.devTrack) {
      return this.standardEndpoint.dev;
    } else {
      return this.standardEndpoint.prod;
    }
  }
}
