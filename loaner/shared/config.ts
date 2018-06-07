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

export interface EnvironmentsVariable {
  local?: string;
  dev: string;
  qa: string;
  prod: string;
}

/**
 * ########################################################################
 * Everything in this comment block must be configured before the app can be
 * built and deployed, see the developer docs for more detail.
 */

/**
 * Google Cloud Project ID for each environment on the appropriate line.
 *
 * These must match the Google Cloud Project ID's in the
 * //loaner/deployments/deploy.sh file for DEV, QA, and PROD respectively.
 */
export const DEV = 'dev-app-engine-project';
export const QA = 'qa-app-engine-project';
export const PROD = 'prod-app-engine-project';

/** The url for the Google Cloud Endpoints API for your application. */
export const WEB_APP_CLIENT_IDS: EnvironmentsVariable = {
  prod: '',
  qa: '',
  dev: '',
};

/** The url for the Google Cloud Endpoints API for your application. */
export const STANDARD_ENDPOINTS: EnvironmentsVariable = {
  prod: `https://endpoints-dot-${PROD}.appspot.com`,
  qa: `https://endpoints-dot-${QA}.appspot.com`,
  dev: `https://endpoints-dot-${DEV}.appspot.com`,
};

export const CHROME_ENDPOINTS: EnvironmentsVariable = {
  prod: `https://chrome-dot-${PROD}.appspot.com`,
  qa: `https://chrome-dot-${QA}.appspot.com`,
  dev: `https://chrome-dot-${DEV}.appspot.com`,
};

/** ######################################################################## */

/**
 * Service for configuration values that are shared between the web app and
 * chrome app.
 */
@Injectable()
export class ConfigService {
  // Frontend specific variables
  webClientId: string;
  ON_PROD = this.hasOrigin(PROD);
  ON_DEV = this.hasOrigin(DEV);
  ON_QA = this.hasOrigin(QA);
  ON_LOCAL = this.hasOrigin('localhost|127\.0\.0\.1');
  IS_FRONTEND = this.ON_LOCAL || this.ON_DEV || this.ON_QA || this.ON_PROD;

  // Chrome App specific variables
  CHROME_DEV_MODE = false;
  DEV_DEVICE_ID = 'sup3r-s3cr3t-d3v1c3-1d';
  LOGGING = false;

  // Shared variables
  analyticsEnabled = false;
  analyticsId = '';
  apiPath = '/_ah/api';
  devTrack: boolean;
  private standardEndpoint: string;
  private chromeEndpoint: string;

  constructor() {
    this.calculateApiUrls();
  }

  /** Decides which API URLs should be used. */
  calculateApiUrls() {
    if ((!this.IS_FRONTEND && !this.CHROME_DEV_MODE) || this.ON_PROD) {
      this.webClientId = WEB_APP_CLIENT_IDS.prod;
      this.devTrack = false;
      this.chromeEndpoint = CHROME_ENDPOINTS.prod;
      this.standardEndpoint = STANDARD_ENDPOINTS.prod;
    } else if (this.ON_QA) {
      this.webClientId = WEB_APP_CLIENT_IDS.qa;
      this.devTrack = false;
      this.chromeEndpoint = CHROME_ENDPOINTS.qa;
      this.standardEndpoint = STANDARD_ENDPOINTS.qa;
    } else if ((!this.IS_FRONTEND && this.CHROME_DEV_MODE) || this.ON_DEV) {
      this.webClientId = WEB_APP_CLIENT_IDS.dev;
      this.chromeEndpoint = CHROME_ENDPOINTS.dev;
      this.standardEndpoint = STANDARD_ENDPOINTS.dev;
    } else {
      this.webClientId = WEB_APP_CLIENT_IDS.dev;
      this.standardEndpoint = 'http://localhost:8081';
      this.chromeEndpoint = 'http://localhost:8082';
    }
  }

  /** Checks wether a specific string is at the window.location.origin. */
  private hasOrigin(origin: string): boolean {
    const re = new RegExp(origin, 'g');
    return Boolean(
        window && window.location && window.location.origin.match(re));
  }

  /** Add's the proper suffix to the Chrome URL and returns the URL. */
  get chromeApiUrl(): string {
    return `${this.chromeEndpoint}${this.apiPath}`;
  }

  /** Add's the proper suffix to the Endpoints URL and returns the URL. */
  get endpointsApiUrl(): string {
    return `${this.standardEndpoint}${this.apiPath}`;
  }
}

/** Name of your Grab n Go program. */
export const PROGRAM_NAME = `Grab n Go`;

/** Interface for the heartbeat configuration parameters */
export interface HeartbeatConfiguration {
  duration: number;
  name: string;
  url: string;
}

/** Configurable heartbeat parameters. */
export const HEARTBEAT: HeartbeatConfiguration = {
  /** Heartbeat duration in minutes */
  duration: 1,
  /** Name of the heartbeat chrome alarm */
  name: 'heartbeat',
  /** URL for the heartbeat api endpoint */
  url: '/loaner/v1/chrome/heartbeat?device_id=',
};


/** Text to be placed on the Manage/Troubleshoot page. */
export const TROUBLESHOOTING_INFORMATION =
'Contact your IT department for assistance.';
/** Phone number of IT; Placed on Manage/Troubleshoot page. */
export const IT_CONTACT_PHONE = '555 55 555';
/** Website of IT; Placed on Manage/Troubleshoot page. */
export const IT_CONTACT_WEBSITE =
'https://support.google.com';
/** Email of IT; Placed on Manage/troubleshoot page. */
export const IT_CONTACT_EMAIL = '';
/** Failure message after 3 failure prompts occur. */
export const FAILURE_MESSAGE = `Since this has failed a couple of times the
application will now quit. If the issue persists contact your
administrator.`;

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
