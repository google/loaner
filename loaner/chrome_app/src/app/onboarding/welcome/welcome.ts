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

import {Component, ElementRef, OnInit, ViewChild} from '@angular/core';
import {MatDialog} from '@angular/material';

import {AnimationMenuComponent} from '../../../../../shared/components/animation_menu';
import {PROGRAM_NAME, WELCOME_ANIMATATION_ALT_TEXT, WELCOME_ANIMATION_ENABLED, WELCOME_ANIMATION_URL} from '../../../../../shared/config';
import {AnimationMenuService} from '../../../../../shared/services/animation_menu_service';

@Component({
  host: {'class': 'mat-typography'},
  selector: 'welcome',
  styleUrls: ['./welcome.scss'],
  templateUrl: './welcome.ng.html',
})
export class WelcomeComponent implements OnInit {
  @ViewChild('welcomeAnimation') animationElement!: ElementRef;

  playbackRate!: number;
  programName: string = PROGRAM_NAME;
  welcomeAnimationEnabled: boolean = WELCOME_ANIMATION_ENABLED;
  welcomeAnimationAltText: string = WELCOME_ANIMATATION_ALT_TEXT;
  welcomeAnimationURL: string = WELCOME_ANIMATION_URL;
  welcomePlaying = true;

  constructor(
      private animationService: AnimationMenuService,
      readonly dialog: MatDialog) {}

  ngOnInit() {
    if (WELCOME_ANIMATION_ENABLED) {
      this.animationService.getAnimationSpeed().subscribe((speed: number) => {
        this.playbackRate = speed / 100;
      });
    }
  }

  /** Plays or pauses the animation */
  playPauseAnimation() {
    if (this.welcomeAnimationEnabled && this.animationElement) {
      if (this.welcomePlaying) {
        this.animationElement.nativeElement.pause();
        this.welcomePlaying = false;
      } else {
        this.animationElement.nativeElement.play();
        this.welcomePlaying = true;
      }
    }
  }

  /** Reloads the animation */
  reloadAnimation() {
    if (this.welcomeAnimationEnabled && this.animationElement) {
      this.animationElement.nativeElement.load();
      this.animationElement.nativeElement.playbackRate = this.playbackRate;
    }
  }

  /** Opens the animation menu and adjusts the animation settings on close. */
  openAnimationMenu() {
    if (this.welcomeAnimationEnabled && this.animationElement) {
      this.dialog.open(AnimationMenuComponent);
    }
  }
}
