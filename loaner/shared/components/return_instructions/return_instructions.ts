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

import {Component, ElementRef, Input, OnInit, ViewChild} from '@angular/core';
import {MatDialog} from '@angular/material';

import {AnimationMenuService} from '../../services/animation_menu_service';
import {AnimationMenuComponent} from '../animation_menu';

export enum FlowsEnum {
  NONE,
  ONBOARDING,
  OFFBOARDING
}

@Component({
  host: {'class': 'mat-typography'},
  selector: 'loaner-return-instructions',
  styleUrls: ['./return_instructions.scss'],
  templateUrl: './return_instructions.ng.html',
})
export class LoanerReturnInstructions implements OnInit {
  @ViewChild('returnAnimation') animationElement!: ElementRef;

  flows = FlowsEnum;

  playbackRate = 1;
  @Input() programName!: string;
  @Input() animationEnabled!: boolean;
  @Input() animationAltText!: string;
  @Input() animationURL!: string;
  @Input() flow: FlowsEnum = FlowsEnum.NONE;
  @Input() chromeApp = false;
  returnPlaying = true;

  constructor(
      private animationService: AnimationMenuService,
      readonly dialog: MatDialog) {}

  ngOnInit() {
    this.animationService.getAnimationSpeed().subscribe((speed: number) => {
      this.playbackRate = speed / 100;
    });
    if (this.flow === this.flows.NONE) {
      throw new Error('The return instructions flow was never defined!');
    }
  }

  /** Plays or pauses the animation */
  playPauseAnimation() {
    if (this.animationEnabled && this.animationElement) {
      if (this.returnPlaying) {
        this.animationElement.nativeElement.pause();
        this.returnPlaying = false;
      } else {
        this.animationElement.nativeElement.play();
        this.returnPlaying = true;
      }
    }
  }

  /** Reloads the animation */
  reloadAnimation() {
    if (this.animationEnabled && this.animationElement) {
      this.animationElement.nativeElement.load();
      this.animationElement.nativeElement.playbackRate = this.playbackRate;
    }
  }

  /** Opens the animation menu and adjusts the animation settings on close. */
  openAnimationMenu() {
    if (this.animationEnabled && this.animationElement) {
      this.dialog.open(AnimationMenuComponent);
    }
  }
}
