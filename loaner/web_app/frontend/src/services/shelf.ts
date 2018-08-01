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

import {Injectable} from '@angular/core';
import {Observable} from 'rxjs';
import {map, tap} from 'rxjs/operators';

import {SearchExpression, SortDirection, translateSortDirectionToApi} from '../../../../shared/models/search';
import {ListShelfResponse, ListShelfResponseApiParams, Shelf, ShelfApiParams} from '../models/shelf';

import {ApiService} from './api';

function setupQueryFilters(
    filters: ShelfApiParams,
    activeSortField: string,
    sortDirection: SortDirection,
) {
  const expressions: SearchExpression = {
    expression: activeSortField,
    direction: translateSortDirectionToApi(sortDirection),
  };

  if (filters.query && filters.query.query_string) {
    filters.query = {query_string: filters.query.query_string, expressions};
  } else {
    filters.query = {expressions};
  }
  return filters;
}

@Injectable()
/** Class to connect to the backend's Shelf Service API methods. */
export class ShelfService extends ApiService {
  /** Implements ApiService's apiEndpoint requirement. */
  apiEndpoint = 'shelf';

  /**
   * Get specific shelf from the backend.
   * @param shelfId Identifier for the Shelf to be gotten from the backend.
   */
  getShelf(shelfId: string) {
    return this.post<Shelf>('get', {'location': shelfId})
        .pipe(map(res => new Shelf(res)));
  }

  /**
   * Creates a particular shelf into the Grab n Go Loaners program.
   * @param newShelf Shelf that will be created in the program.
   */
  create(newShelf: Shelf) {
    return this.post('enroll', newShelf.toApiMessage()).pipe(tap(res => {
      this.snackBar.open(`Shelf ${newShelf.name} created.`);
    }));
  }

  /**
   * Update a particular shelf calling the backend.
   * @param newShelf New shelf information.
   */
  update(newShelf: Shelf) {
    const shelfToBeUpdated = newShelf.toApiMessage();
    return this.post('update', shelfToBeUpdated).pipe(tap(() => {
      this.snackBar.open(`Shelf ${newShelf.name} updated.`);
    }));
  }

  /**
   * Disables a shelf in the backend API.
   * @param shelf Shelf that will be disabled in the program.
   */
  disable(shelf: Shelf) {
    this.post('disable', shelf.toApiMessage()).subscribe(res => {
      this.snackBar.open(`Shelf ${shelf.name} disabled.`);
    });
  }

  /**
   * Lists all shelves enrolled in the program.
   */
  list(
      filters: ShelfApiParams = {},
      activeSortField = 'id',
      sortDirection: SortDirection = 'asc',
      ): Observable<ListShelfResponse> {
    filters = setupQueryFilters(filters, activeSortField, sortDirection);

    return this.post<ListShelfResponseApiParams>('list', filters)
        .pipe(map(res => {
          const shelves =
              res.shelves && res.shelves.map(s => new Shelf(s)) || [];
          const retrievedShelves: ListShelfResponse = {
            shelves,
            totalResults: res.total_results,
            totalPages: res.total_pages,
          };
          return retrievedShelves;
        }));
  }

  /**
   * Performs an audit to a particular shelf, adding the devices to the shelf.
   * @param shelf Shelf that will be audited on this call.
   * @param deviceIdList List of device ids that will be added to the shelf.
   */
  audit(shelf: Shelf, deviceIdList: string[] = []): Observable<void> {
    let snackBarMessage: string;
    const shelfMessage = shelf.toApiMessage();
    shelfMessage['device_identifiers'] = deviceIdList;
    if (deviceIdList.length > 0) {
      snackBarMessage = `Shelf ${shelf.name} audited with devices
                          ${deviceIdList.toString().replace(/,/g, ', ')}.`;
    } else {
      snackBarMessage = `Shelf ${shelf.name} audited as empty.`;
    }

    return this.post<void>('audit', shelfMessage).pipe(tap(() => {
      this.snackBar.open(snackBarMessage);
    }));
  }
}
