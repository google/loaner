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
import {MatAutocompleteTrigger, MatOptionSelectionChange} from '@angular/material';
import {Router} from '@angular/router';

import {LoanerSnackBar} from '../../services/snackbar';

import {SearchBoxService} from './search_box.service';

export declare interface SearchType {
  model: string;
  name: string;
}

/**
 * Component that renders the top search box on the frontend.
 */
@Component({
  selector: 'loaner-search-box',
  styleUrls: ['search_box.scss'],
  templateUrl: 'search_box.html',
})
export class SearchBox implements OnInit {
  isFocused: boolean;
  searchType: SearchType[] = [
    {
      model: 'device',
      name: 'Device',
    },
    {
      model: 'shelf',
      name: 'Shelf',
    }
  ];
  searchText: string;
  @ViewChild('searchBox') searchInputElement: ElementRef;
  @ViewChild(MatAutocompleteTrigger)
  autocompleteTrigger: MatAutocompleteTrigger;


  constructor(
      private router: Router, private searchBoxService: SearchBoxService,
      private readonly snackBar: LoanerSnackBar) {}

  ngOnInit() {
    this.searchBoxService.searchText.subscribe(
        query => this.searchText = query);
  }

  /**
   * Forwards the search request to the results component.
   * @param model represents the model (device/shelf) to search through.
   */
  search(model: string) {
    if (!this.searchText) {
      this.snackBar.open(`You haven't searched for anything!`);
    } else if (model === 'device' && this.searchText) {
      this.router.navigate(
          ['/search/device/', this.searchText], {skipLocationChange: true});
      this.blurInput();
    } else if (model === 'shelf' && this.searchText) {
      this.router.navigate(
          ['/search/shelf/', this.searchText], {skipLocationChange: true});
      this.blurInput();
    }
  }

  /**
   * Updates the search text on the search box service.
   * @param query the query to be updated for the search text.
   */
  updateSearchText(query: string) {
    this.searchBoxService.changeSearchText(query);
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
}
