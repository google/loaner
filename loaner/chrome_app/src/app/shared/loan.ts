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

import {HttpClient, HttpErrorResponse} from '@angular/common/http';
import {Injectable} from '@angular/core';
import {Observable} from 'rxjs';

import {APIService} from '../config';

import * as DeviceIdentifier from './device_identifier';

@Injectable()
export class Loan {
  constructor(private api: APIService, private http: HttpClient) {}

  /**
   * Request to extend the loan return date.
   * @param newDate Date in Python DateTime formatting, sent as a string.
   */
  extend(newDate: string): Observable<boolean> {
    return new Observable((observer) => {
      DeviceIdentifier.id().then((deviceId: string) => {
        const API = this.api.endpoints();
        const extendUrl = `${API}/loaner/v1/device/extend_loan`;
        const request: ExtendRequest = {
          device: {chrome_device_id: deviceId},
          extend_date: newDate,
        };

        this.http.post(extendUrl, request)
            .subscribe(
                () => {
                  observer.next(true);
                },

                (error: HttpErrorResponse) => {
                  observer.error(error);
                });
      });
    });
  }

  /**
   * Mark device as returned on the backend.
   */
  return(): Observable<boolean> {
    return new Observable((observer) => {
      DeviceIdentifier.id().then((deviceId: string) => {
        const API = this.api.endpoints();
        const returnUrl = `${API}/loaner/v1/device/mark_pending_return`;
        const request: ReturnRequest = {
          chrome_device_id: deviceId,
        };

        this.http.post(returnUrl, request)
            .subscribe(
                () => {
                  observer.next(true);
                },

                (error: HttpErrorResponse) => {
                  observer.error(error);
                });
      });
    });
  }

  /**
   * Mark device as damaged on the backend.
   * @param damagedReason Optional reason for what's damaged on the device.
   */
  damaged(damagedReason?: string): Observable<boolean> {
    return new Observable((observer) => {
      DeviceIdentifier.id().then((deviceId: string) => {
        const API = this.api.endpoints();
        const damagedUrl = `${API}/loaner/v1/device/mark_damaged`;
        const request: DamagedReasonRequest = {
          damaged_reason: damagedReason,
          device: {chrome_device_id: deviceId},
        };

        this.http.post(damagedUrl, request)
            .subscribe(
                () => {
                  observer.next(true);
                },

                (error: HttpErrorResponse) => {
                  observer.error(error);
                });
      });
    });
  }

  /**
   * Get loan info for device from backend.
   * @param givenName Represents if it should retrieve the given name.
   */
  getLoan(givenName?: boolean): Observable<LoanResponse> {
    return new Observable((observer) => {
      DeviceIdentifier.id().then((deviceId: string) => {
        const API = this.api.chrome();
        const loanUrl = `${API}/loaner/v1/chrome/loan`;

        const request: LoanRequest = {
          device_id: deviceId,
          need_name: givenName,
        };

        this.http.post<LoanResponse>(loanUrl, request)
            .subscribe(
                (response) => {
                  observer.next(response);
                },

                (error: HttpErrorResponse) => {
                  observer.error(error);
                });
      });
    });
  }

  /**
   * Enable guest mode for the loan.
   */
  enableGuestMode(): Observable<boolean> {
    return new Observable((observer) => {
      DeviceIdentifier.id().then((deviceId: string) => {
        const API = this.api.endpoints();
        const guestUrl = `${API}/loaner/v1/device/enable_guest_mode`;
        const request: GuestModeRequest = {
          chrome_device_id: deviceId,
        };

        this.http.post(guestUrl, request)
            .subscribe(
                () => {
                  observer.next(true);
                },

                (error: HttpErrorResponse) => {
                  observer.error(error);
                });
      });
    });
  }
}
