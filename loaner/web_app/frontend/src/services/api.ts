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

import {HttpClient, HttpErrorResponse, HttpParams} from '@angular/common/http';
import {Injectable} from '@angular/core';
import {Observable, throwError} from 'rxjs';
import {catchError} from 'rxjs/operators';

import {CONFIG} from '../app.config';

import {LoanerSnackBar} from './snackbar';

/** Base abstract class for all API calls. */
@Injectable()
export abstract class ApiService {
  /** API Endpoint that will be overwritten by the child classes. */
  abstract apiEndpoint: string;
  /** The location and origin URL that will compose the base url for the API. */
  private LOCATION =
      `${CONFIG.endpointsHostname}/${CONFIG.apiName}/${CONFIG.apiVersion}/`;

  constructor(
      protected readonly snackBar: LoanerSnackBar,
      private readonly http: HttpClient) {}

  /**
   * Post function that calls the http service on the backend.
   *
   * @param apiMethodAPI method that will be called in this request.
   *     Eg: 'CreateShelf' will compose the url
   *     _ah/api/loaner/v1/shelf/CreateShelf.
   * @param data Data object that will be passed to the backend API.
   * @param showSnackbarOnFailure Whether the snackbar should be shown if the
   *     API call fails.
   */
  protected post<T>(apiMethod: string, data = {}, showSnackbarOnFailure = true):
      Observable<T> {
    const url = `${this.LOCATION}${this.apiEndpoint}/${apiMethod}`;

    return this.http.post<T>(url, data).pipe(
        catchError(error => this.handleError(error, showSnackbarOnFailure)));
  }

  /**
   * Get function that calls the http service on the backend.
   *
   * @param apiMethodAPI method that will be called in this request.
   *     Eg: 'CreateShelf' will compose the url
   *     _ah/api/loaner/v1/shelf/CreateShelf.
   * @param data Data object that will be passed to the backend API as a Search
   *     param.
   * @param showSnackbarOnFailure Whether the snackbar should be shown if the
   *     API call fails.
   */
  // tslint:disable:no-any Data could be any object to be parsed to
  // the querystring.
  protected get<T>(
      apiMethod: string, data: any = {},
      showSnackbarOnFailure = true): Observable<T> {
    // tslint:enable:no-any
    let url = `${this.LOCATION}${this.apiEndpoint}/${apiMethod}`;

    if (data) {
      const queryString = buildQueryStringFromObject(data);
      url = `${url}?${queryString}`;
    }

    return this.http.get<T>(url).pipe(
        catchError(error => this.handleError(error, showSnackbarOnFailure)));
  }

  /** Shows the snackbar if applicable and re-throws the error to the caller. */
  private handleError(
      error: HttpErrorResponse, showSnackbarOnFailure: boolean) {
    if (showSnackbarOnFailure) {
      this.snackBar.open(`ERROR: ${error.error.error.message}`);
    }
    return throwError(error);
  }
}

/** Builds a URL-safe query string from a generic object. */
// tslint:disable-next-line:no-any Data could be any object to be parsed.
const buildQueryStringFromObject = (data: any) => {
  let params = new HttpParams();
  for (const key in data) {
    if (data.hasOwnProperty(key)) {
      params = params.append(key, data[key]);
    }
  }
  return params.toString();
};
