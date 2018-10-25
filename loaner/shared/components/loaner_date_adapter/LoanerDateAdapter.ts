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
 * Loaner date adapter is used in place of the default date adapter to show
 * date picker dates in a <full month> <date>, <year> format.
 */


import {Injectable} from '@angular/core';
import {NativeDateAdapter} from '@angular/material/core';

/**
 * Custom date adapter.
 */
@Injectable()
export class LoanerDateAdapter extends NativeDateAdapter {
  private readonly monthNames: string[] = [
    'January',
    'February',
    'March',
    'April',
    'May',
    'June',
    'July',
    'August',
    'September',
    'October',
    'November',
    'December',
  ];
  format(date: Date, displayFormat: {}): string {
    return `${this.monthNames[date.getUTCMonth()]} ${date.getUTCDate()}, ${
        date.getUTCFullYear()}`;
  }
}
