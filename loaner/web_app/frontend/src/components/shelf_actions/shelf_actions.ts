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
import {FormControl, Validators} from '@angular/forms';
import {ActivatedRoute, Router} from '@angular/router';

import {ConfigResponse, ConfigType} from '../../models/config';
import {Shelf} from '../../models/shelf';
import {ConfigService} from '../../services/config';
import {ShelfService} from '../../services/shelf';

/**
 * Component that renders the Shelf Actions Card template on the frontend.
 */
@Component({
  preserveWhitespaces: true,
  selector: 'loaner-shelf-actions',
  styleUrls: ['shelf_actions.scss'],
  templateUrl: 'shelf_actions.html',
})
export class ShelfActionsCard implements OnInit {
  /** Shelf that will be displayed in the template and created. */
  shelf = new Shelf();
  /** A bool indicating of a shelf already exists. */
  editing: boolean;
  /** List of possible teams that are responsible for a shelf. */
  responsiblesForAuditList: string[];
  /** Controls the capacity input for validation. */
  capacityFormControl = new FormControl('', [
    Validators.min(1),
  ]);

  constructor(
      private readonly configService: ConfigService,
      private readonly shelfService: ShelfService,
      private readonly router: Router, private readonly route: ActivatedRoute) {
  }

  ngOnInit() {
    this.route.params.subscribe((params) => {
      if (params.id) {
        this.shelfService.getShelf(params.id).subscribe((shelf: Shelf) => {
          if (!this.shelf) {
            this.backToShelves();
          }
          this.shelf = shelf;
          this.editing = true;
        });
      } else {
        this.editing = false;
      }
    });
    this.configService.getConfig('responsible_for_audit', ConfigType.LIST)
        .subscribe(
            (response: ConfigResponse) => {
              this.responsiblesForAuditList = response['list_value'] || [];
            },
        );
  }

  /** Creates a new shelf based on the input fields on the template. */
  create() {
    this.shelfService.create(this.shelf);
    this.shelf = new Shelf();
    this.backToShelves();
  }

  /**
   * Updates the current existing shelf based on the input field on the
   * template.
   */
  update() {
    this.shelfService.update(this.shelf);
    this.backToShelfDetails();
  }

  /** Navigates to the shelves page.. */
  backToShelves() {
    this.router.navigate(['/shelves']);
  }

  /** Navigates to the shelf details page. */
  backToShelfDetails() {
    this.router.navigate([`/shelf/${this.shelf.location}/details`]);
  }
}
