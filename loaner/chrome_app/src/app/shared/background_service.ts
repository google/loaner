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

/**
 * Service for handling communication to the chrome app background script.
 */
@Injectable()
export class Background {
  /**
   * Sends a message to the background page that onboarding is complete.
   */
  onboardingComplete() {
    chrome.runtime.sendMessage({'onboardingComplete': true});
  }

  /**
   * Launches a specified view.
   * @param requestedView Name of the view.
   * @param shouldKeepOpen Determines whether to keep the current window open.
   */
  openView(requestedView: string, shouldKeepOpen = false) {
    const currentView = chrome.app.window.current().id;
    const message: RuntimeRequest = {
      currentViewName: currentView,
      keepOpen: shouldKeepOpen,
      open: true,
      view: requestedView,
    };
    chrome.runtime.sendMessage(message);
  }

  /**
   * Closes a given view.
   * @param requestedView Name of the view.
   */
  closeView(requestedView: string) {
    const message: RuntimeRequest = {
      close: true,
      view: requestedView,
    };
    chrome.runtime.sendMessage(message);
  }

  /**
   * Toggles whether a given window is always on top or not.
   * @param id Window's string based ID.
   * @param value Value of whether or not always on top should be true/false.
   */
  setAlwaysOnTop(id: string, value: boolean) {
    chrome.app.window.get(id).setAlwaysOnTop(value);
  }
}

/**
 * Mocks for background requests for testing purposes.
 */
@Injectable()
export class BackgroundMock implements Background {
  onboardingComplete() {
    console.info('Send message onboardingComplete: true');
  }

  openView(view: string, keepOpen = false) {
    console.info(
        `Send message {view: ${view}, open: true, keepOpen: ${keepOpen}}`);
  }

  closeView(view: string) {
    console.info(`Send message {view: ${view}, close: true}`);
  }

  setAlwaysOnTop(id: string, value: boolean) {
    console.info(`Set value of alwaysOnTop for the view: ${id} to ${value}`);
  }
}
