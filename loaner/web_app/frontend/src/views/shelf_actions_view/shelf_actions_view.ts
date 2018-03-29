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

import {Component, OnInit} from '@angular/core';
import {Title} from '@angular/platform-browser';
import {ActivatedRoute} from '@angular/router';

import {CONFIG} from '../../app.config';

@Component({
  preserveWhitespaces: true,
  selector: 'loaner-shelf-actions-view',
  styleUrls: ['shelf_actions_view.scss'],
  templateUrl: 'shelf_actions_view.html',

})
export class ShelfActionsView implements OnInit {
  /** Titles for the component. */
  private readonly createShelfTitle = `Create Shelf - ${CONFIG.appName}`;
  private readonly updateShelfTitle = `Update Shelf - ${CONFIG.appName}`;

  constructor(
      private titleService: Title, private readonly route: ActivatedRoute) {}

  ngOnInit() {
    this.route.params.subscribe((params) => {
      if (params.id) {
        this.titleService.setTitle(this.updateShelfTitle);
      } else {
        this.titleService.setTitle(this.createShelfTitle);
      }
    });
  }
}
