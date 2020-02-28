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

/**
 * Waits for the window to load and then runs the update function to populate
 * debug values.
 */
window.onload = () => update();

/** Updates the debug view with all of the necessary debug values. */
function update() {
  // Alarms
  const alarmsElement = document.getElementById('alarms');
  chrome.alarms.getAll(alarms => {
    if (alarmsElement) {
      alarmsElement.textContent = JSON.stringify(alarms);
    }
  });

  // Loaner Storage Status
  const enrollmentElement = document.getElementById('enrollment');
  chrome.storage.local.get(['loanerStatus'], status => {
    if (enrollmentElement) {
      enrollmentElement.textContent = JSON.stringify(status);
    }
  });

  // OAuth Token
  const oauthElement = document.getElementById('oauth');
  chrome.identity.getAuthToken(token => {
    if (oauthElement) {
      oauthElement.textContent =
          token ? 'Defined' : 'THERE IS NO TOKEN DEFINED.';
    }
  });

  // Device ID
  const deviceElement = document.getElementById('device');
  if (deviceElement) {
    if (chrome.enterprise) {
      chrome.enterprise.deviceAttributes.getDirectoryDeviceId(
          id => deviceElement.textContent = id);
    } else {
      deviceElement.textContent = 'chrome.enterprise API is unavailable';
    }
  }

  // App Version
  const appVersionElement = document.getElementById('version');
  if (appVersionElement) {
    appVersionElement.textContent = chrome.runtime.getManifest().version;
  }
  // Public Key
  const keyElement = document.getElementById('key');
  if (keyElement) {
    keyElement.textContent = chrome.runtime.getManifest().key;
  }

  // Client ID
  const clientIdElement = document.getElementById('client-id');
  if (clientIdElement) {
    clientIdElement.textContent = chrome.runtime.getManifest().oauth2.client_id;
  }

  // Network Connection
  const networkElement = document.getElementById('network');
  if (networkElement) {
    networkElement.textContent = navigator.onLine ?
        'There is a network connection.' :
        'There is NO network connection. Please connect to a WiFi network.';
  }

}

/** Updates the content when the refresh button is clicked. */
document.getElementById('refresh').onclick = () => update();
