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

import {Device} from '../../models/device';
import {ConfigService} from '../../services/config';
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
  @Input() action: Actions;
  /** Current state of the ActionBox component. */
  state: ExpansionState;
  /** Device model that will be added. */
  device = new Device();
  /** If asset tag should be used on this instace of the app. */
  useAssetTag = false;

  @ViewChild('mainIdentifier') mainIdentifier: ElementRef;
  @ViewChild('assetTag') assetTag: ElementRef;
  @ViewChild('actionForm') actionForm: NgForm;

  /** Emits a device when an action is ready to be taken. */
  @Output() takeAction = new EventEmitter<Device>();

  constructor(
      private readonly configService: ConfigService,
      private router: Router,
      private readonly snackBar: LoanerSnackBar,
  ) {}

  ngOnInit() {
    this.configService.getBooleanConfig('use_asset_tags')
        .subscribe(response => {
          this.state = 'expanded';
          this.useAssetTag = response;
        });

    fromEvent<KeyboardEvent>(document, 'keyup').subscribe(event => {
      if (event.key === 'Escape') {
        this.collapse();
      }
    });

    this.router.events.subscribe(event => {
      if (event instanceof NavigationEnd) {
        this.setUpInput();
      }
    });
  }

  ngAfterViewInit() {
    this.setUpInput();
  }

  get mainIdentifierName() {
    return this.useAssetTag ? 'Asset tag' : 'Serial Number';
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
    if (!this.device.serialNumber) {
      this.mainIdentifier.nativeElement.focus();
      this.snackBar.open('Serial Number is empty and it is required');
    } else if (this.useAssetTag && !this.device.assetTag) {
      this.assetTag.nativeElement.focus();
      this.snackBar.open('Asset tag is empty and it is required');
    } else {
      this.emitDevice();
    }
  }

  private takeUnenrollActions() {
    if (!this.device.unknownIdentifier) {
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
    this.mainIdentifier.nativeElement.focus();
    this.actionForm.resetForm();
  }

  /** Setup input field configuration */
  setUpInput() {
    if (this.actionForm) {
      setTimeout(() => {
        this.mainIdentifier.nativeElement.focus();
        this.mainIdentifier.nativeElement.select();
      }, 500);
      this.actionForm.resetForm();
    }
  }

  collapse() {
    this.state = 'collapsed';
  }

  animationDone(event: AnimationEvent) {
    if (event.toState === 'collapsed') {
      this.router.navigate(['devices']);
    }
  }
}
