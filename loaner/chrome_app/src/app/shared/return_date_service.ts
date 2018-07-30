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
import * as moment from 'moment';
import {BehaviorSubject, Observable} from 'rxjs';

import {FailAction, FailType, Failure} from './failure';
import {Loan} from './loan';

@Injectable()
export class ReturnDateService {
  dueDate?: Date;
  maxReturnDate?: Date;
  newReturnDate?: Date;
  toBeSubmitted = true;

  /** Formats the new requested due date via moment for API interaction. */
  get formattedNewDueDate() {
    return moment(this.newReturnDate!).format(`YYYY-MM-DD[T][00]:[00]:[00]`);
  }

  /** Validates the date using the new formatted due date. */
  get dateValidation() {
    return this.validateDate(this.formattedNewDueDate);
  }

  /** Initializes the behavior subjects to be used for component comms. */
  private dueDateSource = new BehaviorSubject<Date|undefined>(this.dueDate);
  private maxReturnDateSource =
      new BehaviorSubject<Date|undefined>(this.maxReturnDate);
  private newReturnDateSource =
      new BehaviorSubject<Date|undefined>(this.newReturnDate);
  private validDateSource = new BehaviorSubject<boolean>(true);

  validDate = this.validDateSource.asObservable();

  constructor(private readonly loan: Loan, private readonly failure: Failure) {}

  /**
   * Used to update the new return date using behavior subjects.
   *
   * @returns The new return date added to the service.
   */
  updateNewReturnDate(date: Date): Observable<undefined|Date> {
    this.newReturnDate = date;
    this.newReturnDateSource.next(date);
    this.validDateSource.next(this.validateDate(moment(date).format()));
    return this.newReturnDateSource.asObservable();
  }

  /** Used to update the max due date using behavior subjects. */
  updateDueDate(date: Date) {
    this.dueDateSource.next(date);
    this.dueDate = date;
  }

  /** Used to update the max return date using behavior subjects. */
  updateMaxReturnDate(date: Date) {
    this.maxReturnDateSource.next(date);
    this.maxReturnDate = date;
  }

  /** Used to update the validity of a given date using behavior subjects. */
  updateValidDate(val: boolean) {
    this.validDateSource.next(val);
  }

  /** Gets the minimum return date and zeroes the time. */
  getMinimumReturnDate(): Date {
    const today = moment().set({
      hour: 0,
      minute: 0,
      second: 0,
    });
    return moment(today).add(1, 'd').toDate();
  }

  /**
   * Validates if the date that has been put in is valid.
   * Checks if the date isn't changed and allows proceeding as such.
   * Used by the onboarding flow to do constant validation checks.
   */
  validationChecks() {
    return new Observable<boolean>(observer => {
      // If the due date is the same as the fields value, do nothing.
      if (this.dueDate === this.newReturnDate) {
        this.validDateSource.next(true);
        observer.next(true);
        // Check if the date is valid and within extendable ranges.
      } else if (this.dateValidation) {
        observer.next(true);
        // If neither of the above are true, fail the validation checks.
      } else {
        observer.next(false);
      }
    });
  }

  /**
   * Checks the dates to see if the loan can be extended.
   * @param date The formatted new extension date.
   */
  validateDate(date: string): boolean {
    return moment(date).diff(this.getMinimumReturnDate(), 'days') >= 0 &&
        moment(date).diff(this.maxReturnDate!, 'days') <= 0;
  }

  /** Used to change the set return date. */
  changeReturnDate(): boolean {
    if (this.dateValidation) {
      this.loan.extend(this.formattedNewDueDate)
          .subscribe(
              () => {
                this.newReturnDate = moment(this.formattedNewDueDate).toDate();
                this.toBeSubmitted = false;
                this.dueDate = this.newReturnDate;
                this.validDateSource.next(true);
              },
              (error) => {
                this.validDateSource.next(true);
                const message =
                    'Something happened with setting the return date.';
                this.failure.register(
                    message, FailType.Other, FailAction.Quit, error);
              });
      return true;
    } else {
      this.validDateSource.next(false);
      return false;
    }
  }
}
