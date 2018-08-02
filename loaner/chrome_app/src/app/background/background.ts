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

import {Observable} from 'rxjs';
import {switchMap, take, tap} from 'rxjs/operators';

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
      createNotification(
          'noInternet-management', offlineNotification, 'You\'re offline');
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
  let enrollment: string;
  checkEnrollmentStatus()
      .pipe(switchMap(enrollmentStatus => {
        enrollment = enrollmentStatus;
        return checkOnboardingStatus();
      }))
      .subscribe(onboarding => {
        if (enrollment === 'true' && onboarding === 'complete') {
          const options: ChromeWindowOptions = {
            bounds: {
              height: APP_HEIGHT,
              width: APP_WIDTH,
            },
            id: 'manage',
            resizable: false,
          };
          chrome.app.window.create('manage.html', (options));
        } else if (enrollment !== 'true') {
          const notEnrolledNotification = 'This device is not enrolled in ' +
              'the ' + PROGRAM_NAME + ' program. Please contact your ' +
              'administrator.';
          createNotification(
              'notEnrolled', notEnrolledNotification,
              'This device is not enrolled');
          console.error('Enrollment status: ', enrollment);
        } else if (onboarding !== 'complete') {
          const notOnboardedNotification = 'Please try again after ' +
              'completing the onboarding process.';
          createNotification(
              'notOnboarded', notOnboardedNotification,
              'Please complete the onboarding process first');
          console.error('Onboarding status: ', onboarding);
        } else {
          const unhandledNotification = 'Oh no! Something unusual appears to ' +
              'have happened. Please contact your administrator for ' +
              'additional support.';
          createNotification(
              'unhandledError', unhandledNotification, 'Something happened');
          console.error('Enrollment status: ', enrollment);
          console.error('Onboarding status: ', onboarding);
        }
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
  const options: ChromeNotificationOptions = {
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
  checkEnrollmentStatus().subscribe(status => {
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
  checkOnboardingStatus().subscribe(
      status => {
        const internetStatus = checkInternetConnectivity();
        if (status === 'incomplete' && internetStatus) {
          launchOnboardingFlow();
        }
      },
      error => {
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
  checkOnboardingStatus().subscribe(status => {
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
  createNotification(
      'noInternet-onboarding', offlineNotification, 'You\'re offline!');
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
function checkOnboardingStatus(): Observable<string> {
  const storage = new Storage();
  return storage.local.get('onboardingStatus')
      .pipe(take(1), tap(status => {
              if (!status) {
                console.warn('Unable to obtain local onboarding status value.');
              }
            }));
}

/**
 * Checks the current enrollment status by querying local storage.
 */
function checkEnrollmentStatus(): Observable<string> {
  const storage = new Storage();
  return storage.local.get('loanerEnrollment')
      .pipe(take(1), tap(status => {
              if (!status) {
                console.warn('Unable to obtain local enrollment status value.');
              }
            }));
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
  storage.local.set('loanerEnrollment', 'false');
  storage.local.set('onboardingStatus', 'disabled');
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
            onboarding(device.is_enrolled, device.start_assignment, response);
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
    isEnrolled: boolean, startAssignment: boolean, heartbeatExists: boolean) {
  if (isEnrolled) {
    const storage = new Storage();
    if (!heartbeatExists) {
      enableHeartbeat();
    }
    storage.local.set('loanerEnrollment', 'true');
    if (startAssignment) {
      launchOnboardingFlow();
      // If online, report online.
      window.addEventListener('online', reportOnline);
      storage.local.set('onboardingStatus', 'incomplete');
    } else {
      storage.local.set('onboardingStatus', 'complete');
    }
    // If the device isn't enrolled in the program, disable the app
    // locally.
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
              onboarding(device.is_enrolled, device.start_assignment, response);
              chrome.alarms.onAlarm.removeListener(keepTrying);
              chrome.alarms.clear('KEEP_TRYING');
            },
            error => {
              console.error(error);
            });
  }
}
