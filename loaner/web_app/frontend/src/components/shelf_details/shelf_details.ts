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

import {Location} from '@angular/common';
import {Component, Input, OnInit} from '@angular/core';
import {Router} from '@angular/router';

import {APPLICATION_PERMISSIONS} from '../../app.config';

import {Shelf} from '../../models/shelf';
import {Dialog} from '../../services/dialog';
import {ShelfService} from '../../services/shelf';
import {UserService} from '../../services/user';

/**
 * Component that renders the Shelf Details template on the frontend.
 */
@Component({
  preserveWhitespaces: true,
  selector: 'loaner-shelf-details',
  styleUrls: ['shelf_details.scss'],
  templateUrl: 'shelf_details.ng.html',
})
export class ShelfDetails implements OnInit {
  /** Shelf that will have the details displayed in the template. */
  @Input() shelf!: Shelf;

  showAdvancedOptions = false;
  showQuickAudit = false;

  constructor(
      private readonly dialogBox: Dialog,
      private readonly location: Location,
      private readonly router: Router,
      private readonly shelfService: ShelfService,
      private readonly userService: UserService,
  ) {}

  ngOnInit() {
    if (!this.shelf) {
      this.back();
    }
    this.userService.whenUserLoaded().subscribe(user => {
      if (user.superadmin) {
        this.showAdvancedOptions = true;
      } else {
        this.showQuickAudit =
            user.hasAnyPermission(APPLICATION_PERMISSIONS.AUDIT_SHELF);
      }
    });
  }

  /**
   * Route to action update to enable form and skip location history to avoid
   * back looping between shelf details and shelf update.
   */
  edit() {
    this.router.navigate(
        ['shelf', this.shelf.location, 'update'], {skipLocationChange: true});
  }

  /** Dialog for removing a shelf. */
  openDisableDialog() {
    /** Title for shelf dialog box. */
    const dialogTitle = 'Remove shelf';
    /** Content for shelf dialog box. */
    const dialogContent = 'Are you sure do you want to remove this shelf?';
    this.dialogBox.confirm(dialogTitle, dialogContent).subscribe(result => {
      if (result) {
        this.shelfService.disable(this.shelf);
        this.back();
      }
    });
  }

  /** Navigates to the previous expected page. */
  back() {
    this.location.back();
  }
}
