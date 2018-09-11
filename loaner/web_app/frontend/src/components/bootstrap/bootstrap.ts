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

import {Component, OnDestroy, OnInit} from '@angular/core';

import {Router} from '@angular/router';
import {interval, Subject} from 'rxjs';
import {switchMap, takeUntil} from 'rxjs/operators';

import {CONFIG} from '../../app.config';
import * as bootstrap from '../../models/bootstrap';
import {BootstrapService} from '../../services/bootstrap';

/**
 * Component that renders the Bootstrap flow of the application.
 */
@Component({
  selector: 'loaner-bootstrap',
  styleUrls: ['bootstrap.scss'],
  templateUrl: 'bootstrap.ng.html',
})
export class Bootstrap implements OnInit, OnDestroy {
  private onDestroy = new Subject<void>();
  /** Whether or not the bootstrap has been started by the user. */
  bootstrapStarted = false;
  /** Whether or not the bootstrap is in progress. */
  inProgress = false;
  /** This will be populated with the bootstrap status from the backend. */
  bootstrapStatus!: bootstrap.Status;
  /** This gets flipped on ngInit depending on whether bootstrap is enabled. */
  bootstrapEnabled!: boolean;

  constructor(
      private readonly bootstrapService: BootstrapService,
      private readonly router: Router) {}

  ngOnInit() {
    this.inProgress = true;
    this.bootstrapService.getStatus().subscribe((status: bootstrap.Status) => {
      this.bootstrapEnabled = status.enabled;
      this.bootstrapStarted = status.started;
      this.inProgress = false;
    });
  }

  bootstrapApplication() {
    this.bootstrapStarted = true;
    this.inProgress = true;
    const tasksToRun = this.bootstrapStatus &&
        this.bootstrapStatus.tasks.filter(task => !task.success);
    this.bootstrapService.run(tasksToRun).subscribe(status => {
      this.bootstrapStatus = status;
    });

    const repeater =
        interval(5000)
            .pipe(
                takeUntil(this.onDestroy),
                switchMap(() => this.bootstrapService.getStatus()),
                )
            .subscribe((status: bootstrap.Status) => {
              this.bootstrapStatus = status;

              if (this.bootstrapStatus.completed ||
                  this.bootstrapTasksFinished || this.failedTasks) {
                this.inProgress = false;
                repeater.unsubscribe();
              }
            });
  }

  ngOnDestroy() {
    this.onDestroy.next();
  }

  redirectToApp() {
    this.router.navigate(['/devices']);
  }

  get isEnabled(): boolean {
    return this.bootstrapEnabled;
  }

  get bootstrapTasksFinished(): boolean {
    return this.hasTasks &&
        this.bootstrapStatus.tasks.every(task => !!task.success);
  }

  get failedTasks(): bootstrap.Task[] {
    if (this.hasTasks) {
      return this.bootstrapStatus.tasks.filter(task => task.success === false);
    }
    return [];
  }

  get hasTasks(): boolean {
    return this.bootstrapStatus && !!this.bootstrapStatus.tasks;
  }

  get canBootstrap(): boolean {
    return !this.bootstrapStarted && this.isEnabled && !this.inProgress &&
        !this.bootstrapTasksFinished;
  }

  get canRetry(): boolean {
    return this.bootstrapStarted && !this.inProgress &&
        !this.bootstrapTasksFinished;
  }

  get appName() {
    return CONFIG.appName;
  }
}
