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
import {BehaviorSubject, Observable} from 'rxjs';

/** Service to interact with the animation menu between components. */
@Injectable()
export class AnimationMenuService {
  playbackRate = new BehaviorSubject<number>(100);

  /** Gets the animation speed from Chrome Storage. */
  constructor() {
    chrome.storage.sync.get(
        'animationSpeed', (result: {[key: string]: number}) => {
          if (result.animationSpeed != null) {
            this.setAnimationSpeed(result.animationSpeed);
          } else {
            this.setAnimationSpeed(100);
          }
        });
  }

  /**
   * Set the animation speed in Chrome Storage.
   * @param value The value to store for animationSpeed in Chrome Storage.
   */
  setAnimationSpeed(value: number) {
    this.playbackRate.next(value);
    chrome.storage.sync.set({animationSpeed: value});
  }

  /** Gets the animation speed. */
  getAnimationSpeed(): Observable<number> {
    return this.playbackRate.asObservable();
  }
}
