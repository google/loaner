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

import {Component} from '@angular/core';
import {MatDialogRef} from '@angular/material';

import {AnimationMenuService} from '../../services/animation_menu_service';

/**
 * References the content to go into the animation menu.
 * Also handles the dialog closing.
 */
@Component({
  host: {
    'class': 'mat-typography',
  },
  selector: 'animation-menu',
  styleUrls: ['./animation_menu.scss'],
  templateUrl: './animation_menu.ng.html',
})
export class AnimationMenuComponent {
  playbackRate!: number;

  constructor(
      private animationService: AnimationMenuService,
      public dialogRef: MatDialogRef<AnimationMenuComponent>) {
    this.animationService.getAnimationSpeed().subscribe(
        speed => this.playbackRate = speed);
  }

  closeDialog() {
    this.animationService.setAnimationSpeed(this.playbackRate);
    this.dialogRef.close();
  }
}
