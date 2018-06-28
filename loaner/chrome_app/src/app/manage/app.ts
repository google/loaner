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

import {PlatformLocation} from '@angular/common';
import {Component, NgModule, ViewChild, ViewEncapsulation} from '@angular/core';
import {BrowserModule} from '@angular/platform-browser';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {NavigationEnd, Router, RouterModule, Routes} from '@angular/router';

import {DamagedModule} from '../../../../shared/components/damaged';
import {ExtendModule} from '../../../../shared/components/extend';
import {GuestModeModule} from '../../../../shared/components/guest';
import {BACKGROUND_LOGO, BACKGROUND_LOGO_ENABLED, ConfigService} from '../../../../shared/config';
import {AnalyticsModule, AnalyticsService} from '../shared/analytics';
import {ChromeAppPlatformLocation,} from '../shared/chrome_app_platform_location';
import {HttpModule} from '../shared/http/http_module';

import {FaqComponent, FaqModule} from './faq';
import {BottomNavModule, NavTab} from './shared/bottom_nav';
import {StatusComponent, StatusModule} from './status';
import {TroubleshootComponent, TroubleshootModule} from './troubleshoot';

@Component({
  encapsulation: ViewEncapsulation.None,
  preserveWhitespaces: true,
  selector: 'app-root',
  styleUrls: ['./app.scss'],
  templateUrl: './app.ng.html',
})
export class AppRoot {
  backgroundLogo = BACKGROUND_LOGO;
  backgroundLogoEnabled = BACKGROUND_LOGO_ENABLED;

  // Represents the analytics image in the body.
  @ViewChild('analytics') analyticsImg!: HTMLImageElement|null;

  navBarTabs: NavTab[] = [
    {
      ariaLabel: 'Troubleshoot your device',
      icon: 'build',
      link: '/troubleshoot',
      title: 'Troubleshoot',
    },
    {
      ariaLabel: 'Status of your loan',
      icon: 'help',
      link: '/status',
      title: 'Status',
    },
    {
      ariaLabel: 'Frequently asked questions',
      icon: 'check_circle',
      link: '/faq',
      title: 'FAQ',
    },
  ];

  constructor(
      private readonly analyticsService: AnalyticsService,
      private readonly config: ConfigService,
      private readonly router: Router,
  ) {}

  ngAfterViewInit() {
    if (this.config.analyticsEnabled) {
      this.router.events.subscribe(route => {
        if (route instanceof NavigationEnd) {
          this.analyticsService
              .sendView('manage', route.url === '/' ? '/status' : route.url)
              .subscribe(url => {
                if (this.analyticsImg) {
                  this.analyticsImg.src = window.URL.createObjectURL(url);
                }
              });
        }
      });
    }
  }
}

/** Base route definition for the application. */
const APP_ROUTES: Routes = [
  {path: 'faq', component: FaqComponent},
  {path: 'troubleshoot', component: TroubleshootComponent},
  {path: 'status', component: StatusComponent},
  {path: '**', redirectTo: 'status'},
];

@NgModule({
  bootstrap: [AppRoot],
  declarations: [AppRoot],
  imports: [
    AnalyticsModule,
    BottomNavModule,
    BrowserAnimationsModule,
    BrowserModule,
    DamagedModule,
    ExtendModule,
    FaqModule,
    GuestModeModule,
    HttpModule,
    RouterModule.forRoot(APP_ROUTES, {useHash: true}),
    StatusModule,
    TroubleshootModule,
  ],
  providers: [
    ConfigService,
    {provide: PlatformLocation, useClass: ChromeAppPlatformLocation},
  ],
})
export class AppModule {
}
