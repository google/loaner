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

import {HttpClient} from '@angular/common/http';
import {Injectable} from '@angular/core';
import {BehaviorSubject, Observable} from 'rxjs';

import {SearchIndexType} from '../models/config';

import {ApiService} from './api';
import {LoanerSnackBar} from './snackbar';

@Injectable()
export class SearchService extends ApiService {
  private searchTextSource = new BehaviorSubject<string>('');
  apiEndpoint = 'search';

  searchText: Observable<string> = this.searchTextSource.asObservable();

  constructor(
      readonly snackbar: LoanerSnackBar,
      private readonly directHttp: HttpClient) {
    super(snackbar, directHttp);
  }

  /**
   * Function to change the text to be searched.
   * @param query represents what is being searched.
   */
  changeSearchText(query: string) {
    this.searchTextSource.next(query);
  }

  /** Gets the helper text from assets/search_help.md file. */
  getHelp(): Observable<string> {
    return this.directHttp.get(
        './assets/search_help.md', {'responseType': 'text'});
  }

  /** Builds the request for reindexing and clearing the search index */
  private getRequestType(searchType: SearchIndexType) {
    return {'model': searchType === SearchIndexType.Shelf ? 'SHELF' : 'DEVICE'};
  }

  /**
   * Reindexes the specified type for searching.
   * @param searchType represents what should be reindexed.
   */
  reindex(searchType: SearchIndexType) {
    const request = this.getRequestType(searchType);
    return this.get('reindex', request).subscribe(() => {
      this.snackBar.open(`Reindexing ${searchType} search.`);
    });
  }

  /**
   * Clears the index for the specified type for searching.
   * @param searchType represents what should be cleared.
   */
  clearIndex(searchType: SearchIndexType) {
    const request = this.getRequestType(searchType);
    return this.get('clear', request).subscribe(() => {
      this.snackBar.open(`Clearing index for ${searchType} search.`);
    });
  }
}
