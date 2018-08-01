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

import {Directive, Input} from '@angular/core';
import {AbstractControl, NG_VALIDATORS, Validator} from '@angular/forms';

/**
 * Directive to set number minimum input value, see example:
 * <input name="field" loanerMinValidator="1" #control="ngModel"
 * [(ngModel)]="field"> If user input any value shorter than 1 the field is
 * maked as invalid.
 */
@Directive({
  selector: '[loaner-min-validator],[loanerMinValidator]',
  providers: [{provide: NG_VALIDATORS, useExisting: MinValidator, multi: true}]
})
export class MinValidator implements Validator {
  @Input() minValue = 1;
  validate(control: AbstractControl): {[key: string]: {}}|null {
    const value = control.value;
    return (value < this.minValue) ? {'minValue': true} : null;
  }
}
