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

import {animate, AnimationEvent, state, style, transition, trigger} from '@angular/animations';
import {AfterViewInit, Component, ElementRef, EventEmitter, Input, OnInit, Output, ViewChild} from '@angular/core';
import {NgForm} from '@angular/forms';
import {NavigationEnd, Router} from '@angular/router';
import {fromEvent} from 'rxjs';

import {DeviceIdentifierModeType} from '../../models/config';
import {Actions, Device} from '../../models/device';
import {ConfigService} from '../../services/config';
import {LoanerSnackBar} from '../../services/snackbar';

/** Possible states that the action box can have: expanded or collapsed. */
export type ExpansionState = 'expanded'|'collapsed';

@Component({
  preserveWhitespaces: true,
  selector: 'loaner-device-action-box',
  styleUrls: ['device_action_box.scss'],
  templateUrl: 'device_action_box.ng.html',
  animations: [
    trigger(
        'bodyExpansion',
        [
          state('collapsed', style({height: 0})),
          state('expanded', style({height: '210px'})),
          transition(
              '* => *',
              [
                animate('350ms ease-in-out'),
              ]),
        ]),
  ],
})
export class DeviceActionBox implements OnInit, AfterViewInit {
  /** Actions that can be taken on devices and displayed on the template. */
  actions = Actions;
  /** Current action that wil be taken on the device. */
  @Input() action!: Actions;
  /** Current state of the ActionBox component. */
  state!: ExpansionState;
  /** Device model that will be added. */
  device = new Device();
  /** Which device identifier mode the app is currently configured to use. */
  private deviceIdentifierMode?: DeviceIdentifierModeType;

  /** If asset tag should be used on this instace of the app. */
  get useAssetTag() {
    return this.deviceIdentifierMode === DeviceIdentifierModeType.ASSET_TAG ||
        this.deviceIdentifierMode === DeviceIdentifierModeType.BOTH_REQUIRED;
  }

  /** If serial number should be used on this instace of the app. */
  get useSerialNumber() {
    return this.deviceIdentifierMode ===
        DeviceIdentifierModeType.SERIAL_NUMBER ||
        this.deviceIdentifierMode === DeviceIdentifierModeType.BOTH_REQUIRED;
  }

  @ViewChild('mainIdentifier') mainIdentifier!: ElementRef;
  @ViewChild('serialNumber') serialNumber!: ElementRef;
  @ViewChild('assetTag') assetTag!: ElementRef;
  @ViewChild('actionForm') actionForm!: NgForm;

  /** Emits a device when an action is ready to be taken. */
  @Output() takeAction = new EventEmitter<Device>();

  constructor(
      private readonly configService: ConfigService,
      private readonly router: Router,
      private readonly snackBar: LoanerSnackBar,
  ) {}

  ngOnInit() {
    this.configService.getStringConfig('device_identifier_mode')
        .subscribe(response => {
          this.deviceIdentifierMode = response as DeviceIdentifierModeType;
          this.state = 'expanded';
        });


    fromEvent<KeyboardEvent>(document, 'keyup').subscribe(event => {
      if (event.key === 'Escape') {
        this.collapse();
      }
    });

    this.router.events.subscribe(event => {
      if (event instanceof NavigationEnd) {
        setTimeout(() => {
          this.setUpInput();
        });
      }
    });
  }

  ngAfterViewInit() {
    this.setUpInput();
  }

  /** Setup input field configuration */
  private setUpInput() {
    this.setUpMainIdentifier();
    if (this.actionForm) {
      setTimeout(() => {
        this.mainIdentifier.nativeElement.focus();
        this.mainIdentifier.nativeElement.select();
      }, 500);
      this.blurFromAnyInput();
      this.actionForm.resetForm();
    }
  }

  private setUpMainIdentifier() {
    if (this.action === Actions.ENROLL) {
      if (this.useSerialNumber) {
        this.mainIdentifier = this.serialNumber;
      } else {
        this.mainIdentifier = this.assetTag;
      }
    }
  }

  get mainIdentifierName() {
    return this.useAssetTag ? 'Asset tag' : 'Serial Number';
  }

  private blurFromAnyInput() {
    if (this.serialNumber) {
      this.serialNumber.nativeElement.blur();
    }
    if (this.assetTag) {
      this.assetTag.nativeElement.blur();
    }
    if (this.mainIdentifier) {
      this.mainIdentifier.nativeElement.blur();
    }
  }

  /** Emits the takeAction event with the current device on the component. */
  takeActionOnDevice() {
    if (this.action === Actions.ENROLL) {
      this.takeEnrollActions();
    } else {
      this.takeUnenrollActions();
    }
  }

  private takeEnrollActions() {
    if (this.useSerialNumber && !this.device.serialNumber) {
      this.serialNumber.nativeElement.focus();
    } else if (this.useAssetTag && !this.device.assetTag) {
      this.assetTag.nativeElement.focus();
    } else {
      this.emitDevice();
    }
  }

  private takeUnenrollActions() {
    if (!this.device.identifier) {
      this.mainIdentifier.nativeElement.focus();
      this.snackBar.open(
          `${this.mainIdentifierName} is empty and it is required`);
    } else {
      this.emitDevice();
    }
  }

  private emitDevice() {
    this.takeAction.emit(this.device);
    this.device = new Device();
    this.setUpInput();
  }

  collapse() {
    this.state = 'collapsed';
  }

  animationDone(event: AnimationEvent) {
    if (event.toState === 'collapsed') {
      this.router.navigate(['devices']).then(res => {
        if (!res) {
          this.state = 'expanded';
          this.setUpInput();
        }
      });
    }
  }
}
