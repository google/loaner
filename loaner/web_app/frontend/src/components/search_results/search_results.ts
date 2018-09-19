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
import {Component, OnDestroy, OnInit, ViewChild} from '@angular/core';
import {MatPaginator, PageEvent} from '@angular/material';
import {ActivatedRoute, Router} from '@angular/router';

import {Device, DeviceApiParams} from '../../models/device';
import {Shelf, ShelfApiParams} from '../../models/shelf';
import {DeviceService} from '../../services/device';
import {SearchService} from '../../services/search';
import {ShelfService} from '../../services/shelf';
import {LoanerSnackBar} from '../../services/snackbar';


/**
 * Component that renders the search results on the frontend.
 */
@Component({
  selector: 'loaner-search-results',
  styleUrls: ['search_results.scss'],
  templateUrl: 'search_results.ng.html',
})
export class SearchResultsComponent implements OnDestroy, OnInit {
  loading = true;
  model!: string;
  query!: string;
  results!: Device[]|Shelf[];

  /** Represents the total number of results received via search. */
  totalResults!: number;

  @ViewChild(MatPaginator) paginator!: MatPaginator;

  get resultsLength(): number {
    return this.results ? this.results.length : 0;
  }

  constructor(
      private readonly deviceService: DeviceService,
      private readonly location: Location,
      private readonly route: ActivatedRoute, private readonly router: Router,
      private readonly searchService: SearchService,
      private readonly shelfService: ShelfService,
      private readonly snackBar: LoanerSnackBar) {}

  ngOnInit() {
    this.route.params.subscribe(params => {
      if (params.model && params.query) {
        this.model = params.model;
        this.query = params.query;
        this.search(params.model, params.query);
      } else if (!params.model) {
        this.snackBar.open(`You haven't searched for anything!`);
        this.back();
      } else if (!params.query && params.model) {
        this.snackBar.open(`You haven't provided a query for your search!`);
        this.back();
      } else {
        this.snackBar.open(`Your search was invalid!`);
        this.back();
      }
    });
  }

  /**
   * Searches for a given model/query.
   * @param model Represents the type/model to search against
   * @param query Represents the string to search for in the id's model.
   */
  search(model: string, query: string) {
    if (model === 'device') {
      this.searchForDevice(query);
    } else if (model === 'shelf') {
      this.searchForShelf(query);
    } else if (model === 'user') {
      this.searchForDevice(query, true);
    } else {
      throw new TypeError(`Unsupported search type ${model}`);
    }
  }

  /**
   * Searches for a given device or user with assigned devices.
   * @param queryString Represents the string to search for in devices.
   * @param userSearch Indicates if the search type is for a user or not.
   */
  private searchForDevice(queryString: string, userSearch?: boolean) {
    const request = this.buildRequest(queryString, userSearch);
    this.deviceService.list(request).subscribe(response => {
      const devices = response.devices;
      this.totalResults = response.totalResults;
      if (userSearch && devices.length >= 1) {
        this.router.navigate(
            ['user'], {queryParams: {'user': devices[0].assignedUser}});
      } else if (devices.length === 1 && devices[0].identifier) {
        this.router.navigate(['/device', devices[0].identifier]);
      } else {
        this.results = devices;
        this.location.replaceState(`/search/${this.model}/${queryString}`);
      }
      this.loading = false;
    });
  }

  /**
   * Searches for a given shelf.
   * @param queryString Represents the string to search for in shelves.
   */
  private searchForShelf(queryString: string) {
    const request = this.buildRequest(queryString);
    this.shelfService.list(request).subscribe(response => {
      this.totalResults = response.totalResults;
      const shelves = response.shelves;
      if (shelves.length === 1 && shelves[0].location) {
        this.router.navigate(['/shelf', shelves[0].location, 'details']);
      } else {
        this.results = shelves;
        this.location.replaceState(`/search/shelf/${queryString}`);
      }
      this.loading = false;
    });
  }

  /**
   * Builds the request paramaters for making the request.
   * @param queryString represents the string to search for.
   * @param userSearch represents if the search is for a user.
   */
  private buildRequest(queryString: string, userSearch?: boolean):
      DeviceApiParams|ShelfApiParams {
    if (userSearch) {
      return {assigned_user: queryString};
    } else {
      return {
        query: {
          query_string: queryString,
        },
        // Sets the default page to 1 if paginator doesn't exist.
        page_number: this.paginator ? this.paginator.pageIndex + 1 : 1,
        // Defaults to 10 if the paginator doesn't exist.
        page_size: this.paginator ? this.paginator.pageSize : 10,
      };
    }
  }

  /**
   * Handles the change page events that the paginator emits.
   * @param event Represents the paginators emitted event.
   */
  changePage(event: PageEvent) {
    switch (this.model) {
      case 'device':
        this.searchForDevice(this.query);
        break;
      case 'shelf':
        this.searchForShelf(this.query);
        break;
      case 'user':
        this.searchForDevice(this.query, true);
        break;
      default:
        break;
    }
  }

  /** Goes back to the previous view. */
  back() {
    this.location.back();
  }

  ngOnDestroy() {
    this.searchService.changeSearchText('');
  }
}
