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

import {CreateTagRequest, ListTagRequest, ListTagResponse, ListTagResponseApiParams, Tag, UpdateTagRequest} from '../models/tag';

import {ApiService} from './api';

/** A tag service that manages API calls to the backend. */
@Injectable()
export class TagService extends ApiService {
  /** Implements ApiService's apiEndpoint requirement. */
  apiEndpoint = 'tag';

  create(tag: Tag) {
    const params: CreateTagRequest = {'tag': tag.toApiMessage()};
    return this.post('create', params).pipe(tap(() => {
      this.snackBar.open(`Tag ${tag.name} created.`);
    }));
  }

  destroy(tag: Tag) {
    return this.post('destroy', {'urlsafe_key': tag.urlSafeKey})
        .pipe(tap(() => {
          this.snackBar.open(`Tag ${tag.name} has been deleted`);
        }));
  }

  update(tag: Tag) {
    const params: UpdateTagRequest = {'tag': tag.toApiMessage()};
    return this.post('update', params).pipe(tap(() => {
      this.snackBar.open(`Tag: ${tag.name} has been updated.`);
    }));
  }

  list(params: ListTagRequest): Observable<ListTagResponse> {
    return this.post<ListTagResponseApiParams>('list', params).pipe(map(res => {
      const tags = res.tags && res.tags.map(tag => new Tag(tag)) || [];
      const retrievedTags: ListTagResponse = {
        tags,
        cursor: res.cursor,
        has_additional_results: res.has_additional_results,
        total_pages: res.total_pages,
      };
      return retrievedTags;
    }));
  }
}
