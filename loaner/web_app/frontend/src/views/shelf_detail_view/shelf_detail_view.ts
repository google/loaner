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

import {LoaderView} from '../../../../../shared/components/loader';
import {CONFIG} from '../../app.config';
import {Shelf} from '../../models/shelf';
import {ShelfService} from '../../services/shelf';

@Component({
  preserveWhitespaces: true,
  selector: 'loaner-shelf-detail-view',
  styleUrls: ['shelf_detail_view.scss'],
  templateUrl: 'shelf_detail_view.ng.html',

})
export class ShelfDetailView extends LoaderView implements OnInit {
  /** Title for the component. */
  readonly title = `Shelf Details - ${CONFIG.appName}`;
  shelf!: Shelf;

  constructor(
      private readonly shelfService: ShelfService,
      private readonly route: ActivatedRoute, private titleService: Title) {
    super(false);
  }

  ngOnInit() {
    this.titleService.setTitle(this.title);
    this.route.params.subscribe((params) => {
      this.shelfService.getShelf(params.id).subscribe((shelf: Shelf) => {
        this.shelf = shelf;
      });
    });
  }
}
