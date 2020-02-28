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

import {CreateTemplateRequest, ListTemplateResponse, ListTemplateResponseApiParams, Template, TemplateApiParams} from '../models/template';

import {ApiService} from './api';

/** A template service that manages API calls to the backend. */
@Injectable()
export class TemplateService extends ApiService {
  /** Implements ApiService's apiEndpoint requirement. */
  apiEndpoint = 'template';

  create(template: Template): Observable<void> {
    const params: CreateTemplateRequest = {'template': template.toApiMessage()};
    return this.post<void>('create', params).pipe(tap(() => {
      this.snackBar.open(`Template ${template.name} created.`);
    }));
  }

  remove(template: Template): Observable<void> {
    return this.post<void>('remove', {'name': template.name}).pipe(tap(() => {
      this.snackBar.open(`Template: ${template.name} has been deleted.`);
    }));
  }

  update(template: Template): Observable<void> {
    const params: TemplateApiParams = template.toApiMessage();
    return this.post<void>('update', params).pipe(tap(() => {
      this.snackBar.open(`Template: ${template.name} has been updated.`);
    }));
  }

  list(): Observable<ListTemplateResponse> {
    return this.get<ListTemplateResponseApiParams>('list').pipe(map(res => {
      const templates = res.templates &&
              res.templates.map(template => new Template(template)) ||
          [];
      const retrievedTemplates: ListTemplateResponse = {templates};
      return retrievedTemplates;
    }));
  }
}
