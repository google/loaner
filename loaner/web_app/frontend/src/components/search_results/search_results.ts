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
import {Component, OnInit} from '@angular/core';
import {ActivatedRoute, Router} from '@angular/router';

import {Device, DeviceApiParams} from '../../models/device';
import {Shelf, ShelfApiParams} from '../../models/shelf';
import {DeviceService} from '../../services/device';
import {ShelfService} from '../../services/shelf';
import {LoanerSnackBar} from '../../services/snackbar';

/**
 * Component that renders the search results on the frontend.
 */
@Component({
  selector: 'loaner-search-results',
  styleUrls: ['search_results.scss'],
  templateUrl: 'search_results.html',
})
export class SearchResultsComponent implements OnInit {
  model: string;
  query: string;
  results: Device[]|Shelf[];

  get resultsLength(): number {
    return this.results ? this.results.length : 0;
  }

  constructor(
      private readonly deviceService: DeviceService,
      private readonly location: Location,
      private readonly route: ActivatedRoute, private readonly router: Router,
      private readonly shelfService: ShelfService,
      private readonly snackBar: LoanerSnackBar) {}

  ngOnInit() {
    this.route.params.subscribe(params => {
      if (params.model && params.query) {
        this.model = params.model;
        this.query = params.query;
        this.search(params.model, params.query);
      } else if (!params.model) {
        this.snackBar.open(`You haven't search for anything!`);
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
    } else {
      throw new TypeError(`Unsupported search type ${model}`);
    }
  }

  /**
   * Searches for a given device.
   * @param queryString Represents the string to search for in devices.
   */
  private searchForDevice(queryString: string) {
    const request: DeviceApiParams = {
      query: {
        query_string: queryString,
      },
    };
    this.deviceService.list(request).subscribe(devices => {
      if (devices.length === 1 && devices[0].id) {
        this.router.navigate([`/device/${devices[0].id}`]);
      } else {
        this.results = devices;
        this.location.replaceState(`/search/device/${queryString}`);
      }
    });
  }

  /**
   * Searches for a given shelf.
   * @param queryString Represents the string to search for in shelves.
   */
  private searchForShelf(queryString: string) {
    const request: ShelfApiParams = {
      query: {
        query_string: queryString,
      }
    };
    this.shelfService.list(request).subscribe(shelves => {
      if (shelves.length === 1 && shelves[0].location) {
        this.router.navigate([`/shelf/${shelves[0].location}/details`]);
      } else {
        this.results = shelves;
        this.location.replaceState(`/search/shelf/${queryString}`);
      }
    });
  }

  /** Goes back to the previous view. */
  back() {
    this.location.back();
  }
}
