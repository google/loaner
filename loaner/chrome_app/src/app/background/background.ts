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

import {Observable, of} from 'rxjs';
import {switchMap, take} from 'rxjs/operators';

import {HEARTBEAT, PROGRAM_NAME} from '../../../../shared/config';
import {Storage} from '../shared/storage/storage';

import * as Heartbeat from './heartbeat';

const APP_WIDTH = 700;
const APP_HEIGHT = 570;

/** Represents an enrolled and onboarded device. */
const ENROLLED_AND_ONBOARDED: LoanerStorage = {
  enrolled: true,
  onboardingComplete: true,
};

/** Represents an enrolled and not onboarded device. */
const ENROLLED_AND_NOT_ONBOARDED: LoanerStorage = {
  enrolled: true,
  onboardingComplete: false,
};

/** Represent the name of the local storage key name. */
const LOANER_STATUS_NAME = 'loanerStatus';

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
      createNotification(
          'noInternet-management', offlineNotification, 'You\'re offline');
    }
  }
});

/** On installation/update of the application start the onboarding process. */
chrome.runtime.onInstalled.addListener(prepareToOnboardUser);

/** On startup of the Chromebook start the onboarding process. */
chrome.runtime.onStartup.addListener(prepareToOnboardUser);

/**
 * This function adds a listener which waits for the user profile to be
 * available to the chrome.identity API.
 */
function prepareToOnboardUser() {
  // First attempt occurs regardless of sign in.
  onboardUser();
  // Second attempt only occurs if the sign in changes.
  chrome.identity.onSignInChanged.addListener(() => onboardUser());
}

/**
 * Launches the GnG Management application.
 */
function launchManage() {
  checkLoanerStatus().subscribe(
      status => {
        if (status.enrolled && status.onboardingComplete) {
          const options: chrome.app.CreateWindowOptions = {
            bounds: {
              height: APP_HEIGHT,
              width: APP_WIDTH,
            },
            id: 'manage',
            resizable: false,
          };
          chrome.app.window.create('manage.html', (options));
        } else if (!status.enrolled) {
          const notEnrolledNotification = 'This device is not enrolled in ' +
              'the ' + PROGRAM_NAME + ' program. Please contact your ' +
              'administrator.';
          createNotification(
              'notEnrolled', notEnrolledNotification,
              'This device is not enrolled');
          console.error('Enrollment status: ', status.enrolled);
        } else if (!status.onboardingComplete) {
          const notOnboardedNotification = 'Please try again after ' +
              'completing the onboarding process.';
          createNotification(
              'notOnboarded', notOnboardedNotification,
              'Please complete the onboarding process first');
          console.error(
              'Onboarding complete status: ', status.onboardingComplete);
        }
      },
      (error: {}) => {
        console.error(error);
      });
}

/**
 * Makes a fresh heartbeat to populate the storage values if they are undefined.
 */
function manageValueUpdater(): Observable<LoanerStorage> {
  // Adds a warning and notification that the values are being updated.
  console.warn('Attempting to update the local storage values.');
  const waitNotification = 'We are checking this devices current status.';
  createNotification('pleaseWait', waitNotification, 'Please wait');
  return new Observable(observer => {
    Heartbeat.sendHeartbeat().subscribe(
        deviceInfo => {
          if (deviceInfo.is_enrolled && !deviceInfo.start_assignment) {
            observer.next(ENROLLED_AND_ONBOARDED);
          } else if (deviceInfo.is_enrolled && deviceInfo.start_assignment) {
            onboarding(
                deviceInfo.is_enrolled, deviceInfo.start_assignment, false,
                deviceInfo.silent_onboarding);
            observer.next(ENROLLED_AND_NOT_ONBOARDED);
          } else if (!deviceInfo.is_enrolled) {
            disableApp();
            throw new Error(
                'Device is not enrolled in the app. Disabling app.');
          } else {
            throw new Error(
                'An unknown error has occurred, contact your administrator');
          }
        },
        error => {
          const unhandledNotification =
              'Oh no! We were unable to retrieve the devices current state.';
          createNotification(
              'unhandledError', unhandledNotification, 'Something happened');
          console.error(error);
        });
  });
}

/**
 * Creates a notification for the user based on criteria that is passed in.
 * @param notificationID represents a unique name for the notification.
 * @param message the message to be passed into the notification.
 * @param title the title of the notification.
 * @param type string that defines what type of notification to be.
 */
function createNotification(
    notificationID: string, message: string, title: string, type = 'basic') {
  const options: chrome.notifications.NotificationOptions = {
    iconUrl: 'assets/icons/gng128.png',
    message: `${message}`,
    requireInteraction: true,
    title: `${title}`,
    type: 'basic',
  };

  chrome.notifications.create(notificationID, options);
}

/**
 * Launches the GnG Offboarding flow.
 */
function launchOffboardingFlow() {
  checkLoanerStatus().subscribe(status => {
    if (status.enrolled && status.onboardingComplete) {
      const options: chrome.app.CreateWindowOptions = {
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
  checkLoanerStatus().subscribe(status => {
    if (!status.onboardingComplete) {
      launchOnboardingFlow();
    }
  });
}

/**
 * Launches the GnG Onboarding application once installed.
 */
function launchOnboardingFlow() {
  const options: chrome.app.CreateWindowOptions = {
    bounds: {
      height: APP_HEIGHT,
      width: APP_WIDTH,
    },
    alwaysOnTop: true,
    frame: 'none',
    id: 'onboarding',
    resizable: false,
  };

  chrome.app.window.create(
      'onboarding.html', options, (win: chrome.app.AppWindow) => {
        win.onClosed.addListener(relaunchOnboarding);
      });
}

/**
 * Ensure that the app has the most recent version of the Chrome App.
 * If the app doesn't, this will restart the Chrome App.
 */
chrome.runtime.onUpdateAvailable.addListener(() => {
  console.info('Update available. Installing!');
  chrome.runtime.reload();
});

/**
 * Listen for completion of onboarding flow.
 * Additionally, listens for view requests at the end of the onboarding flow.
 */
chrome.runtime.onMessage.addListener(
    (request: RuntimeRequest, sender, sendResponse) => {
      const storage = new Storage();
      if (request.onboardingComplete) {
        storage.local.set(LOANER_STATUS_NAME, ENROLLED_AND_ONBOARDED);
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
 * Checks the current loaner status by querying local storage.
 */
function checkLoanerStatus(): Observable<LoanerStorage> {
  const storage = new Storage();
  return storage.local.getLoanerStorage(LOANER_STATUS_NAME)
      .pipe(
          take(1),
          switchMap(status => status ? of(status) : manageValueUpdater()));
}

/**
 * Destroys the app and prevents it from ever opening again if the device isn't
 * part of the loaner program.
 */
function disableApp() {
  const storage = new Storage();
  const disabledStatus: LoanerStorage = {
    enrolled: false,
    onboardingComplete: false,
  };
  storage.local.set(LOANER_STATUS_NAME, disabledStatus);
  chrome.alarms.clearAll();
}

function enableHeartbeat() {
  Heartbeat.setHeartbeatInterval();
  Heartbeat.setHeartbeatAlarmListener();
}

/**
 * Checks to see if the heartbeat exists.
 */
function checkForHeartbeatAlarm(): Observable<boolean> {
  return new Observable(observer => {
    chrome.alarms.get(HEARTBEAT.name, (result) => {
      if (result) {
        // To prevent duplicate or missing listeners, we destory and re-create
        // the listener for the heartbeat.
        Heartbeat.removeHeartbeatListener();
        Heartbeat.setHeartbeatAlarmListener();
        observer.next(true);
      } else {
        observer.next(false);
      }
    });
  });
}

/** Onboards users and checks for device enrollment on login and startup. */
function onboardUser() {
  let device: HeartbeatResponse;
  Heartbeat.sendHeartbeat()
      .pipe(switchMap(deviceInfo => {
        // Take the device info received from sendHeartbeat and populate device.
        device = deviceInfo;
        return checkForHeartbeatAlarm();
      }))
      .subscribe(
          response => {
            onboarding(
                device.is_enrolled, device.start_assignment, response,
                device.silent_onboarding);
          },
          error => {
            // Checks for the existence of the keep trying alarm.
            chrome.alarms.get('KEEP_TRYING', result => {
              if (result) {
                // Clears the KEEP_TRYING alarms if they exist.
                chrome.alarms.onAlarm.removeListener(keepTrying);
                chrome.alarms.clear('KEEP_TRYING');
              }
              // Creates the alarm.
              createKeepTryingAlarm();
            });
            console.error(error);
          });
}

/**
 * Used to check onboarding criteria. If a device is part of the program, it
 * launches the onboarding flow.
 * Since devices might wipe local storage, this repopulates local values.
 */
function onboarding(
    isEnrolled: boolean, startAssignment: boolean, heartbeatExists: boolean,
    silentOnboarding: boolean) {
  if (isEnrolled) {
    const storage = new Storage();
    if (!heartbeatExists) {
      enableHeartbeat();
    }
    if (startAssignment && !silentOnboarding) {
      storage.local.set(LOANER_STATUS_NAME, ENROLLED_AND_NOT_ONBOARDED);
      launchOnboardingFlow();
    } else {
      storage.local.set(LOANER_STATUS_NAME, ENROLLED_AND_ONBOARDED);
    }
    // If the device isn't enrolled in the program, disable the app locally.
  } else {
    disableApp();
  }
}

/**
 * Creates the alarm to keep trying to check if a device is enrolled and
 * assignable. Also generates the event listener for the alarm.
 */
function createKeepTryingAlarm() {
  chrome.alarms.create('KEEP_TRYING', {
    'periodInMinutes': 1,
  });
  chrome.alarms.onAlarm.addListener(keepTrying);
}

/**
 * Keeps trying to make a successful initial heartbeat. Used by the alarms
 * event listener.
 */
function keepTrying(alarm: chrome.alarms.Alarm) {
  let device: HeartbeatResponse;
  if (alarm.name === 'KEEP_TRYING') {
    Heartbeat.sendHeartbeat()
        .pipe(switchMap(deviceInfo => {
          // Take the device info received from sendHeartbeat and populate
          // device.
          device = deviceInfo;
          return checkForHeartbeatAlarm();
        }))
        .subscribe(
            response => {
              // Kicks off the onboarding process once again and then proceeds
              // to kill this alarm.
              onboarding(
                  device.is_enrolled, device.start_assignment, response,
                  device.silent_onboarding);
              chrome.alarms.onAlarm.removeListener(keepTrying);
              chrome.alarms.clear('KEEP_TRYING');
            },
            error => {
              console.error(error);
            });
  }
}
