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

/// <reference types="chrome/chrome-app" />

import {take} from 'rxjs/operators';

import {HEARTBEAT, PROGRAM_NAME} from '../../../../shared/config';
import {Storage} from '../shared/storage/storage';

import * as Heartbeat from './heartbeat';

const APP_WIDTH = 700;
const APP_HEIGHT = 570;

/**
 * On launch of the application check the source and open the management
 * application. This also does a check to see if an internet connection is
 * active. If not, it will generate a Chrome notification stating the failure.
 */
chrome.app.runtime.onLaunched.addListener((launchData) => {
  if (launchData.source === 'management_api' ||
      launchData.source === 'app_launcher' ||
      launchData.source === 'system_tray' ||
      launchData.source === 'new_tab_page') {
    if (navigator.onLine) {
      launchManage();
    } else {
      const offlineNotification = 'You have no internet connection so the ' +
          PROGRAM_NAME + ' app is unavailable.';
      const notificationID = 'noInternet-management';
      const options: ChromeNotificationOptions = {
        iconUrl: 'assets/icons/gng128.png',
        message: offlineNotification,
        requireInteraction: true,
        title: `You're offline!`,
        type: 'basic',
      };

      chrome.notifications.create(notificationID, options);
    }
  }
});

/**
 * On installed of the application start the onboarding process.
 */
chrome.runtime.onInstalled.addListener(() => {
  onboardUser();
});

/**
 * On installed of the application start the onboarding process.
 */
chrome.runtime.onStartup.addListener(() => {
  onboardUser();
});

/**
 * Launches the GnG Management application.
 */
function launchManage() {
  checkEnrollmentStatus().then((status) => {
    if (status) {
      const options: ChromeWindowOptions = {
        bounds: {
          height: APP_HEIGHT,
          width: APP_WIDTH,
        },
        id: 'manage',
        resizable: false,
      };
      chrome.app.window.create('manage.html', (options));
    }
  });
}

/**
 * Launches the GnG Offboarding flow.
 */
function launchOffboardingFlow() {
  checkEnrollmentStatus().then((status) => {
    if (status) {
      const options: ChromeWindowOptions = {
        bounds: {
          height: APP_HEIGHT,
          width: APP_WIDTH,
        },
        id: 'offboarding',
        resizable: false,
      };
      chrome.app.window.create('offboarding.html', (options));
    }
  });
}

/**
 * Relaunches the Onboarding flow if onboarding is not completed.
 */
function relaunchOnboarding() {
  checkOnboardingStatus().then(
      (status) => {
        const internetStatus = checkInternetConnectivity();
        if (status === 'incomplete' && internetStatus) {
          launchOnboardingFlow();
        }
      },
      (error) => {
        console.error(error);
      });
}

/**
 * Launches the GnG Onboarding application once installed.
 */
function launchOnboardingFlow() {
  const options: ChromeWindowOptions = {
    bounds: {
      height: APP_HEIGHT,
      width: APP_WIDTH,
    },
    alwaysOnTop: true,
    frame: 'none',
    id: 'onboarding',
    resizable: false,
  };

  chrome.app.window.create('onboarding.html', (options), (win) => {
    win.onClosed.addListener(relaunchOnboarding);
    // If offline, report offline.
    window.addEventListener('offline', reportOffline);
  });
}

/**
 * If the computer is online, launch the onboarding flow.
 */
function reportOnline() {
  checkOnboardingStatus().then((status) => {
    if (status === 'incomplete') {
      launchOnboardingFlow();
    }
  });
}

/**
 * Closes the onboarding flow and shows a notification stating the user is
 * offline.
 */
function reportOffline() {
  chrome.app.window.get('onboarding').close();
  const offlineNotification = 'Oh no! You have no internet connection. ' +
      'As soon as you have internet once again, we\'ll launch the onboarding ' +
      'process.';
  const notificationID = 'noInternet-onboarding';
  const options: ChromeNotificationOptions = {
    iconUrl: 'assets/icons/gng128.png',
    message: offlineNotification,
    requireInteraction: true,
    title: `You're offline!`,
    type: 'basic',
  };

  chrome.notifications.create(notificationID, options);
}

/**
 * Ensure that the app has the most recent version of the Chrome App.
 * If the app doesn't, this will restart the Chrome App.
 */
chrome.runtime.onUpdateAvailable.addListener(chrome.runtime.reload);

/**
 * Listen for completion of onboarding flow.
 * Additionally, listens for view requests at the end of the onboarding flow.
 */
chrome.runtime.onMessage.addListener(
    (request: RuntimeRequest, sender, sendResponse) => {
      const storage = new Storage();
      if (request.onboardingComplete === true) {
        storage.local.set('onboardingStatus', 'complete');
        window.removeEventListener('online', reportOnline);
        window.removeEventListener('offline', reportOffline);
      }

      /** Open the requested view */
      if (request.open && request.open != null) {
        if (request.view != null) {
          switch (request.view) {
            case 'manage':
              launchManage();
              break;
            case 'onboarding':
              launchOnboardingFlow();
              break;
            case 'offboarding':
              launchOffboardingFlow();
              break;
            default:
              // Do nothing
              break;
          }
          if (!request.keepOpen && request.currentViewName) {
            chrome.app.window.get(request.currentViewName).close();
          }
        }
      }

      /** Close the requested view */
      if (request.close && request.close != null) {
        if (request.view != null) {
          chrome.app.window.get(request.view).close();
        }
      }
    });

/**
 * Checks the current onboarding status by querying local storage.
 */
function checkOnboardingStatus(): Promise<string> {
  const storage = new Storage();

  return new Promise((resolve, reject) => {
    storage.local.get('onboardingStatus').pipe(take(1)).subscribe((status) => {
      if (status) {
        resolve(status);
      } else {
        reject('Unable to obtain onboarding status value.');
      }
    });
  });
}

/**
 * Checks the current enrollment status by querying local storage.
 */
function checkEnrollmentStatus(): Promise<string> {
  const storage = new Storage();
  return new Promise((resolve, reject) => {
    storage.local.get('loanerEnrollment').pipe(take(1)).subscribe((status) => {
      if (status) {
        resolve(status);
      } else {
        reject('Unable to obtain enrollment status value.');
      }
    });
  });
}

/** Check for internet connectivity. */
function checkInternetConnectivity(): boolean {
  return navigator.onLine;
}

/**
 * Destroys the app and prevents it from ever opening again if the device isn't
 * part of the loaner program.
 */
function disableApp() {
  const storage = new Storage();
  storage.local.set('loanerEnrollment', false);
  storage.local.set('onboardingStatus', 'complete');
  chrome.alarms.clearAll();
}

function enableHeartbeat() {
  Heartbeat.setHeartbeatInterval();
  Heartbeat.setHeartbeatAlarmListener();
}

function disableHeartbeat() {
  Heartbeat.disableHeartbeat();
}

/**
 * Checks to see if the heartbeat exists.
 */
function checkForHeartbeatAlarm(): Promise<boolean> {
  return new Promise((resolve, reject) => {
    chrome.alarms.get(HEARTBEAT.name, (result) => {
      if (result) {
        // To prevent duplicate or missing listeners, we destory and re-create
        // the listener for the heartbeat.
        Heartbeat.removeHeartbeatListener();
        Heartbeat.setHeartbeatAlarmListener();
        resolve(true);
      } else {
        resolve(false);
      }
    });
  });
}

/**
 * Onboards users and checks for device enrollment on login and startup.
 * Since devices might wipe local storage, this repopulates local values.
 */
function onboardUser() {
  const storage = new Storage();
  Heartbeat.sendHeartbeat().then(
      (device) => {
        if (device.is_enrolled) {
          checkForHeartbeatAlarm()
              .then((response) => {
                if (!response) {
                  enableHeartbeat();
                }
              })
              .then(() => {
                storage.local.set('loanerEnrollment', true);
                if (device.start_assignment) {
                  launchOnboardingFlow();
                  // If online, report online.
                  window.addEventListener('online', reportOnline);
                  storage.local.set('onboardingStatus', 'incomplete');
                } else {
                  storage.local.set('onboardingStatus', 'complete');
                }
              });
        } else {
          disableApp();
        }
      },
      (error) => {
        console.error(error);
      });
}
