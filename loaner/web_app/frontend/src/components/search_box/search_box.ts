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

import {Component, ElementRef, OnInit, SecurityContext, ViewChild} from '@angular/core';
import {MatAutocompleteTrigger, MatDialog, MatDialogRef, MatOptionSelectionChange} from '@angular/material';
import {DomSanitizer} from '@angular/platform-browser';
import {Router} from '@angular/router';

import {CONFIG} from '../../app.config';
import * as marked from 'marked';

import {SearchService} from '../../services/search';
import {LoanerSnackBar} from '../../services/snackbar';
import {UserService} from '../../services/user';

export type SearchModel = 'device'|'shelf'|'user';

export declare interface SearchType {
  model: SearchModel;
  name: string;
}

/**
 * Component that renders the top search box on the frontend.
 */
@Component({
  selector: 'loaner-search-box',
  styleUrls: ['search_box.scss'],
  templateUrl: 'search_box.ng.html',
})
export class SearchBox implements OnInit {
  isFocused!: boolean;
  /* Defines the default search options. */
  defaultSearchType: SearchType[] = [
    {
      model: 'device',
      name: 'Device',
    },
    {
      model: 'shelf',
      name: 'Shelf',
    },
  ];
  /* Defines the priveleged search options. */
  privilegedSearchType: SearchType[] = [
    ...this.defaultSearchType,
    {
      model: 'user',
      name: 'User',
    },
  ];
  searchType!: SearchType[];
  searchText!: string;
  @ViewChild('searchBox') searchInputElement!: ElementRef;
  @ViewChild(MatAutocompleteTrigger)
  autocompleteTrigger!: MatAutocompleteTrigger;


  constructor(
      private readonly router: Router,
      private readonly searchService: SearchService,
      private readonly snackBar: LoanerSnackBar,
      private readonly userService: UserService,
      public dialog: MatDialog,
  ) {}

  ngOnInit() {
    this.searchService.searchText.subscribe(query => this.searchText = query);
    this.userService.whenUserLoaded().subscribe(user => {
      if (user.hasPermission(CONFIG.appPermissions.ADMINISTRATE_LOAN)) {
        this.searchType = this.privilegedSearchType;
      } else {
        this.searchType = this.defaultSearchType;
      }
    });
  }

  /**
   * Forwards the search request to the results component.
   * @param model represents the model (device/shelf/user) to search through.
   */
  search(model: string) {
    if (!this.searchText) {
      this.snackBar.open(`You haven't searched for anything!`);
    } else {
      this.navigateToSearchRoute(model);
    }
  }

  /** Navigates to specified search results with a model in the route. */
  private navigateToSearchRoute(searchRoute: string) {
    this.router.navigate(
        [`/search/${searchRoute}/`, this.searchText],
        {skipLocationChange: true});
    this.blurInput();
  }

  /**
   * Updates the search text on the search box service.
   * @param query the query to be updated for the search text.
   */
  updateSearchText(query: string) {
    this.searchService.changeSearchText(query);
  }

  /**
   * Represents the action to take when a search type has been selected from
   * the autocomplete selection.
   * @param event represents the onSelectionChanges event.
   * @param model represents the type of search to be executed.
   */
  searchTypeSelected(event: MatOptionSelectionChange, model: string) {
    if (event.isUserInput) this.search(model);
  }

  /** Blurs the selected input and also the autocomplete. */
  blurInput() {
    if (this.searchInputElement) this.searchInputElement.nativeElement.blur();
    if (this.autocompleteTrigger) this.autocompleteTrigger.closePanel();
  }

  /** Opens the helper dialog for using the search box. */
  openHelper() {
    this.dialog.open(SearchHelper);
  }
}


@Component({
  selector: 'loaner-search-helper',
  styleUrls: ['search_box.scss'],
  templateUrl: 'search_box_helper.ng.html',
})
export class SearchHelper implements OnInit {
  sanitizedHelperContent!: string|null;

  constructor(
      private dialogRef: MatDialogRef<SearchHelper>,
      private readonly sanitizer: DomSanitizer,
      private readonly searchService: SearchService,
  ) {}

  ngOnInit() {
    this.searchService.getHelp().subscribe(response => {
      this.sanitizedHelperContent =
          this.sanitizer.sanitize(SecurityContext.HTML, marked(response));
    });
  }

  /** Closes the helper dialog. */
  closeDialog() {
    this.dialogRef.close();
  }
}
