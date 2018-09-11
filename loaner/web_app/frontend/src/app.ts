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
import {NavigationEnd, Router} from '@angular/router';

import {LoaderService, LoaderView} from '../../../shared/components/loader';
import {ConfigService} from '../../../shared/config';

import {CONFIG} from './app.config';
import {SEARCH_PERMISSIONS} from './app.routing';
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
  requiredPermission?: string[];
  hideOnRoutes: string[];
}

/** Which items are shown in the app's sidebar. */
export const NAVIGATION_ITEMS: NavigationItem[] = [
  {
    icon: 'laptop_chromebook',
    name: 'My Loans',
    routerLink: 'user',
    hideOnRoutes: [
      '/bootstrap',
      '/authorization',
    ]
  },
  {
    icon: 'view_list',
    name: 'Shelves',
    routerLink: 'shelves',
    requiredPermission: [
      CONFIG.appPermissions.READ_SHELVES,
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
    requiredPermission: [
      CONFIG.appPermissions.READ_DEVICES,
    ],
    hideOnRoutes: [
      '/bootstrap',
      '/authorization',
    ]
  },
  {
    icon: 'developer_board',
    name: 'Configuration',
    routerLink: 'configuration',
    requiredPermission: [
      CONFIG.appPermissions.MODIFY_CONFIG,
    ],
    hideOnRoutes: [
      '/authorization',
    ]
  },
  {
    icon: 'bug_report',
    name: 'Report issues',
    url: 'https://github.com/google/loaner/issues',
    hideOnRoutes: [],
  },
];

/** Root component of the Loaner app. */
@Component({
  preserveWhitespaces: true,
  encapsulation: ViewEncapsulation.None,
  selector: 'app-root',
  styleUrls: ['app.scss'],
  templateUrl: 'app.ng.html',
})
export class AppComponent extends LoaderView {
  readonly title = `${CONFIG.appName} Application`;
  readonly navigationItems: NavigationItem[] = NAVIGATION_ITEMS;
  user!: User;
  pending = false;

  constructor(
      readonly authService: AuthService,
      readonly loaderService: LoaderService,
      readonly userService: UserService,
      readonly ngZone: NgZone,
      private readonly config: ConfigService,
      private readonly location: Location,
      private readonly router: Router,
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

    // Handles the content pushes to Google Analytics if enabled.
    if (this.config.analyticsEnabled) {
      this.router.events.subscribe(event => {
        if (event instanceof NavigationEnd) {
          // tslint:disable:no-any DefinitelyTyped does not yet support gtag so
          // we must cast a type of any.
          (window as any)['gtag']('config', this.config.analyticsId, {
            'page_title': this.titleService.getTitle(),
            'page_path': event.urlAfterRedirects,
          });
        }
      });
    }
  }

  ngOnInit() {
    this.titleService.setTitle(this.title);

    this.loaderService.pending.subscribe(async pending => {
      this.pending = await pending;
    });
  }

  /*
   * Checks a NavigationItem's required permission against the user's
   * permissions to determine whether it can be shown.
   */
  canViewBasedOnPermission(navigationItem: NavigationItem): boolean {
    if (!navigationItem.requiredPermission) {
      return true;
    }
    return this.user &&
        this.user.hasPermission(...navigationItem.requiredPermission);
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
        this.canViewBasedOnPermission(navigationItem);
  }

  /**
   * Checks whether a given user can access the search features.
   */
  canShowSearchBox(): boolean {
    return this.user && this.user.hasPermission(...SEARCH_PERMISSIONS);
  }
}
