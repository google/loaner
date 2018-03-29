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

import {Directive, ElementRef, HostListener} from '@angular/core';

/**
 * Directive to strip whitespaces from input fields
 */
@Directive({selector: '[loaner-remove-whitespaces], [loanerRemoveWhitespaces]'})
export class RemoveWhitespaces {
  input: HTMLInputElement;

  constructor(readonly el: ElementRef) {
    this.input = el.nativeElement;
  }

  @HostListener('keyup')
  inputKeyUp() {
    this.removeWhitespaces();
  }

  @HostListener('change')
  inputChange() {
    this.removeWhitespaces();
  }

  private removeWhitespaces() {
    this.input.value = this.input.value.replace(/\s/g, '');
  }
}
