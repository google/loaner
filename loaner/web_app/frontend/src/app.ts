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
import {Component, NgZone, ViewEncapsulation} from '@angular/core';
import {Title} from '@angular/platform-browser';

import {LoaderView} from '../../../shared/components/loader/loader';

import {CONFIG} from './app.config';
import {User} from './models/user';
import {AuthService} from './services/auth';
import {UserService} from './services/user';

/**
 * Defines what must be contained in a navigation items that appear on the
 * sidebar.
 */
export declare interface NavigationItem {
  icon: string;
  name: string;
  routerLink?: string;
  url?: string;
  requiredRole: string|string[];
  hideOnRoutes: string[];
}

/** Which items are shown in the app's sidebar. */
export const NAVIGATION_ITEMS: NavigationItem[] = [
  {
    icon: 'laptop_chromebook',
    name: 'My Loans',
    routerLink: 'user',
    requiredRole: CONFIG.roles.USER,
    hideOnRoutes: [
      '/bootstrap',
      '/authorization',
    ]
  },
  {
    icon: 'view_list',
    name: 'Shelves',
    routerLink: 'shelves',
    requiredRole: [
      CONFIG.roles.TECHNICIAN,
      CONFIG.roles.OPERATIONAL_ADMIN,
      CONFIG.roles.TECHNICAL_ADMIN,
    ],
    hideOnRoutes: [
      '/bootstrap',
      '/authorization',
    ]
  },
  {
    icon: 'devices',
    name: 'Devices',
    routerLink: 'devices',
    requiredRole: [
      CONFIG.roles.TECHNICIAN,
      CONFIG.roles.OPERATIONAL_ADMIN,
      CONFIG.roles.TECHNICAL_ADMIN,
    ],
    hideOnRoutes: [
      '/bootstrap',
      '/authorization',
    ]
  },
  {
    icon: 'bug_report',
    name: 'Report issues',
    url: 'https://github.com/google/loaner/issues',
    requiredRole: [
      CONFIG.roles.USER,
      CONFIG.roles.TECHNICIAN,
      CONFIG.roles.OPERATIONAL_ADMIN,
      CONFIG.roles.TECHNICAL_ADMIN,
    ],
    hideOnRoutes: [],
  },
];

/** Root component of the Loaner app. */
@Component({
  preserveWhitespaces: true,
  encapsulation: ViewEncapsulation.None,
  selector: 'app-root',
  styleUrls: ['app.scss'],
  templateUrl: 'app.html',
})
export class AppComponent extends LoaderView {
  readonly title = `${CONFIG.appName} Application`;
  readonly navigationItems: NavigationItem[] = NAVIGATION_ITEMS;
  user: User;

  constructor(
      readonly authService: AuthService,
      readonly userService: UserService,
      readonly ngZone: NgZone,
      private readonly location: Location,
      private readonly titleService: Title,
  ) {
    super(true);
    ngZone.run(() => {
      authService.whenLoaded().subscribe(() => {
        if (!authService.isSignedIn ||
            this.location.path().startsWith('/authorization')) {
          this.ready();
        }
      });
    });

    userService.whenUserLoaded().subscribe(user => {
      this.user = user;
      this.ready();
    });
  }

  ngOnInit() {
    this.titleService.setTitle(this.title);
  }

  /*
   * Checks a NavigationItem's required role against the user's role to
   * determine whether it can be shown.
   */
  canViewBasedOnRole(navigationItem: NavigationItem): boolean {
    return this.user && this.user.hasRole(navigationItem.requiredRole);
  }

  /*
   * Checks a NavigationItem's hidden routes against the current route to
   * determine whether it can be shown.
   */
  canViewBasedOnHiddenRoutes(navigationItem: NavigationItem): boolean {
    return navigationItem.hideOnRoutes
               .filter(route => this.location.path().startsWith(route))
               .length === 0;
  }

  /*
   * Determines whether a NavigationItem can be shown based on its hidden routes
   * and the user's role.
   */
  canShow(navigationItem: NavigationItem): boolean {
    return this.canViewBasedOnHiddenRoutes(navigationItem) &&
        this.canViewBasedOnRole(navigationItem);
  }
}
