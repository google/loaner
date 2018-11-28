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

/// <reference types="chrome-apps" />
import {Injectable} from '@angular/core';

export interface EnvironmentsVariable {
  local?: string;
  dev: string;
  qa: string;
  prod: string;
}

/** Defines the Chrome Modes for deployment. */
export enum CHROME_MODE {
  DEV,
  QA,
  PROD,
}

/** Represents the types of environments for the application. */
export enum ENVIRONMENTS {
  LOCAL,
  DEV,
  QA,
  PROD,
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
export const WEB_CLIENT_IDS: EnvironmentsVariable = {
  prod: `{PROD_WEB_ID}`,
  qa: `{QA_WEB_ID}`,
  dev: `{DEV_WEB_ID}`,
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

/**
 * Below are the public keys for the Chrome Applications that you're deploying.
 * This is how the Chrome App will target a specific track (prod, dev, or qa).
 *
 * This value can be retrieved from the Chrome Webstore developer dashboard
 * under the "More Info" button.
 * NOTE: Each key must be on a single-line!
 */
export const CHROME_PUBLIC_KEYS: EnvironmentsVariable = {
  prod: '{PROD_CHROME_KEY}',
  qa: '{QA_CHROME_KEY}',
  dev: '{DEV_CHROME_KEY}',
};

/** ######################################################################## */

/**
 * Service for configuration values that are shared between the web app and
 * chrome app.
 */
@Injectable()
export class ConfigService {
  // Frontend specific variables
  webClientId!: string;
  ON_PROD = this.hasOrigin(PROD);
  ON_DEV = this.hasOrigin(DEV);
  ON_QA = this.hasOrigin(QA);
  ON_LOCAL = this.hasOrigin('localhost|127\.0\.0\.1');
  IS_FRONTEND = this.ON_LOCAL || this.ON_DEV || this.ON_QA || this.ON_PROD;

  // Chrome App specific variables
  DEV_DEVICE_ID = 'sup3r-s3cr3t-d3v1c3-1d';
  LOGGING = false;
  get chromeMode() {
    try {
      const manifest = chrome.runtime.getManifest();
      switch (manifest.key) {
        case CHROME_PUBLIC_KEYS.prod: {
          return CHROME_MODE.PROD;
        }
        case CHROME_PUBLIC_KEYS.qa: {
          return CHROME_MODE.QA;
        }
        case CHROME_PUBLIC_KEYS.dev: {
          return CHROME_MODE.DEV;
        }
        default: {
          console.error(
              'The key defined in the manifest.json of the Chrome App is not recognized. Defaulting to dev.');
          return CHROME_MODE.DEV;
        }
      }
    } catch (e) {
      if (!this.IS_FRONTEND) {
        console.error('The chrome.runtime API isn\'t available.', e);
      }
      // Returns dev to deal with unhandled conditions and tests.
      return CHROME_MODE.DEV;
    }
  }

  /** Generates the web app URL for usage in the Chrome App. */
  get webAppUrl() {
    if (this.chromeMode === CHROME_MODE.PROD) {
      return `https://${PROD}.appspot.com`;
    } else if (this.chromeMode === CHROME_MODE.QA) {
      return `https://${QA}.appspot.com`;
    } else {
      return `https://${DEV}.appspot.com`;
    }
  }

  // Shared variables
  analyticsEnabled = false;
  analyticsId = '';
  apiPath = '/_ah/api';
  devTrack!: boolean;
  private standardEndpoint!: string;
  private chromeEndpoint!: string;

  // Checks what environment the app is running in.
  get appMode() {
    if (this.IS_FRONTEND) {
      if (this.ON_DEV) return ENVIRONMENTS.DEV;
      if (this.ON_LOCAL) return ENVIRONMENTS.LOCAL;
      if (this.ON_PROD) return ENVIRONMENTS.PROD;
      if (this.ON_QA) return ENVIRONMENTS.QA;
    } else {
      if (this.chromeMode === CHROME_MODE.DEV) return ENVIRONMENTS.DEV;
      if (this.chromeMode === CHROME_MODE.PROD) return ENVIRONMENTS.PROD;
      if (this.chromeMode === CHROME_MODE.QA) return ENVIRONMENTS.QA;
    }
    // If all of the checks above fail, failover to local by default.
    return ENVIRONMENTS.LOCAL;
  }

  constructor() {
    this.calculateApiUrls();
  }

  /** Decides which API URLs should be used. */
  calculateApiUrls() {
    if (this.appMode === ENVIRONMENTS.PROD) {
      this.webClientId = WEB_CLIENT_IDS.prod;
      this.devTrack = false;
      this.chromeEndpoint = CHROME_ENDPOINTS.prod;
      this.standardEndpoint = STANDARD_ENDPOINTS.prod;
    } else if (this.appMode === ENVIRONMENTS.QA) {
      this.webClientId = WEB_CLIENT_IDS.qa;
      this.devTrack = false;
      this.chromeEndpoint = CHROME_ENDPOINTS.qa;
      this.standardEndpoint = STANDARD_ENDPOINTS.qa;
    } else if (this.appMode === ENVIRONMENTS.DEV) {
      this.webClientId = WEB_CLIENT_IDS.dev;
      this.chromeEndpoint = CHROME_ENDPOINTS.dev;
      this.standardEndpoint = STANDARD_ENDPOINTS.dev;
    } else {
      this.webClientId = WEB_CLIENT_IDS.dev;
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
  duration: 10,
  /** Name of the heartbeat chrome alarm */
  name: 'heartbeat',
  /** URL for the heartbeat api endpoint */
  url: '/loaner/v1/chrome/heartbeat?device_id=',
};


/** Text to be placed on the Manage/Troubleshoot page. */
export const TROUBLESHOOTING_INFORMATION =
'Contact your IT department for assistance.';
/** Phone number of IT; Placed on Manage/Troubleshoot page. */
export const IT_CONTACT_PHONE = ['555 55 555'];
/** Website of IT; Placed on Manage/Troubleshoot page. */
export const IT_CONTACT_WEBSITE = 'https://support.google.com';
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

/** Welcome animation configuration */
export const WELCOME_ANIMATION_ENABLED = true;
export const WELCOME_ANIMATATION_ALT_TEXT = `An animation showing
 an overview of Grab n Go loaner device.`;
export const WELCOME_ANIMATION_URL = '../assets/animations/welcome.mp4';

/** Return animation configuration */
export const RETURN_ANIMATION_ENABLED = true;
export const RETURN_ANIMATION_ALT_TEXT = `An animation showing
 an overview of returning your Grab n Go loaner device.`;
export const RETURN_ANIMATION_URL = '../assets/animations/return.mp4';

/** Toolbar icon to be displayed on the top right of onboarding/offboarding. */
export const TOOLBAR_ICON_ENABLED = false;
export const TOOLBAR_ICON = {
  url: '../assets/icons/gng48.png',
  altText: 'GnG logo',
};
