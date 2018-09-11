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

import {Component, OnInit} from '@angular/core';
import {Title} from '@angular/platform-browser';
import {ActivatedRoute, Router} from '@angular/router';

import {LoaderView} from '../../../../../shared/components/loader';
import {CONFIG} from '../../app.config';
import {AuthService} from '../../services/auth';

/**
 * Component that renders the Authorization flow of the application.
 */
@Component({
  preserveWhitespaces: true,
  selector: 'loaner-authorization',
  styleUrls: ['authorization.scss'],
  templateUrl: 'authorization.ng.html',
})
export class Authorization extends LoaderView implements OnInit {
  /** Title for the component. */
  private readonly title = `Authorization - ${CONFIG.appName}`;
  /** Url to be redirected after login. */
  private returnUrl!: string;

  constructor(
      private readonly authService: AuthService,
      private readonly route: ActivatedRoute,
      private readonly router: Router,
      private readonly titleService: Title,
  ) {
    super(true);
    this.authService.whenLoaded().subscribe(() => {
      this.ready();
    });
  }

  ngOnInit() {
    this.returnUrl = this.route.snapshot.queryParams['returnUrl'] || '/';
    this.titleService.setTitle(this.title);
    if (this.authService.isSignedIn) {
      this.router.navigateByUrl(this.returnUrl);
    }
  }

  login() {
    this.authService.signIn();
    this.authService.whenSignedIn().subscribe(() => {
      this.router.navigateByUrl(this.returnUrl);
    });
  }
}
