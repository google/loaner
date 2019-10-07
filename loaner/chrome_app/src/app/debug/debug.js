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
  chrome.alarms.getAll(
      alarms => document.getElementById('alarms').textContent =
          JSON.stringify(alarms));

  // Loaner Storage Status
  chrome.storage.local.get(
      ['loanerStatus'],
      status => document.getElementById('enrollment').textContent =
          JSON.stringify(status));

  // OAuth Token
  chrome.identity.getAuthToken(token => {
    document.getElementById('oauth').textContent =
        token ? 'Defined' : 'THERE IS NO TOKEN DEFINED.';
  });

  // Device ID
  if (chrome.enterprise) {
    chrome.enterprise.deviceAttributes.getDirectoryDeviceId(
        id => document.getElementById('device').textContent = id);
  } else {
    document.getElementById('device').textContent =
        'chrome.enterprise API is unavailable';
  }

  // App Version
  document.getElementById('version').textContent =
      chrome.runtime.getManifest().version;

  // Public Key
  document.getElementById('key').textContent = chrome.runtime.getManifest().key;

  // Client ID
  document.getElementById('clientId').textContent =
      chrome.runtime.getManifest().oauth2.client_id;

  // Network Connection
  document.getElementById('network').textContent = navigator.onLine ?
      'There is a network connection.' :
      'There is NO network connection. Please connect to a WiFi network.';

}

/** Updates the content when the refresh button is clicked. */
document.getElementById('refresh').onclick = () => update();
