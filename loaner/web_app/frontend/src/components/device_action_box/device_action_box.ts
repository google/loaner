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

import {animate, state, style, transition, trigger} from '@angular/animations';
import {Component, ElementRef, EventEmitter, Input, OnInit, Output, ViewChild} from '@angular/core';
import {NgForm} from '@angular/forms';
import {Router} from '@angular/router';

import {Device} from '../../models/device';
import {LoanerSnackBar} from '../../services/snackbar';

/** Possible actions that can be taken on devices in this component. */
export enum Actions {
  ENROLL = 'enroll',
  UNENROLL = 'unenroll',
}

/** Possible states that the action box can have: expanded or collapsed. */
export type ExpansionState = 'expanded'|'collapsed';

@Component({
  preserveWhitespaces: true,
  selector: 'loaner-device-action-box',
  styleUrls: ['device_action_box.scss'],
  templateUrl: 'device_action_box.html',
  animations: [
    trigger(
        'bodyExpansion',
        [
          state('collapsed', style({height: 0})),
          state('expanded', style({height: '170px'})),
          transition(
              '* => *',
              [
                animate('350ms ease-in-out'),
              ]),
        ]),
  ],
})
export class DeviceActionBox implements OnInit {
  /** Actions that can be taken on devices and displayed on the template. */
  actions = Actions;
  /** Current action that wil be taken on the device. */
  @Input() action: Actions;
  /** Current state of the ActionBox component. */
  state: ExpansionState = 'collapsed';
  /** Device model that will be added. */
  device = new Device();

  @ViewChild('serialNumber') serialNumber: ElementRef;
  @ViewChild('actionForm') actionForm: NgForm;

  /**
   * Function callback that will receive the device that the action was taken.
   */
  @Output() takeAction = new EventEmitter<Device>();

  constructor(
      private router: Router, private readonly snackBar: LoanerSnackBar) {}

  ngOnInit() {
    this.state = 'expanded';
  }

  ngOnChanges() {
    if (this.serialNumber) {
      this.setUpInput();
    }
  }

  ngAfterViewInit() {
    this.setUpInput();
  }

  /** Emits the takeAction event with the current device on the component. */
  takeActionOnDevice() {
    if (!this.device.serialNumber) {
      this.serialNumber.nativeElement.focus();
      this.snackBar.open('Serial Number is empty and it is required');
    } else {
      this.takeAction.emit(this.device);
      this.device = new Device();
      this.actionForm.resetForm();
      this.serialNumber.nativeElement.focus();
    }
  }

  /** Setup input field configuration */
  setUpInput() {
    if (this.actionForm) {
      this.actionForm.form.markAsPristine();
      this.actionForm.form.markAsUntouched();
      setTimeout(() => {
        this.serialNumber.nativeElement.focus();
        this.serialNumber.nativeElement.select();
      }, 500);
    }
  }

  collapse() {
    this.state = 'collapsed';
  }

  animationDone() {
    if (this.state === 'collapsed') {
      this.router.navigate(['devices']);
    }
  }
}
