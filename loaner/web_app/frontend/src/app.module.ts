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

import {HTTP_INTERCEPTORS, HttpClientModule} from '@angular/common/http';
import {NgModule} from '@angular/core';
import {BrowserModule, DomSanitizer, Title} from '@angular/platform-browser';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';

import {LoaderModule} from '../../../shared/components/loader';

import {AppComponent} from './app';
import {LoanerRouterModule} from './app.routing';
import {MaterialModule, MatIconRegistry} from './core/material_module';
import {AuthService} from './services/auth';
import {AuthGuard} from './services/auth_guard';
import {BootstrapService} from './services/bootstrap';
import {ConfigService} from './services/config';
import {DeviceService} from './services/device';
import {LoanerOAuthInterceptor} from './services/oauth_interceptor';
import {ShelfService} from './services/shelf';
import {LoanerSnackBar} from './services/snackbar';
import {UserService} from './services/user';

/** Root module of the Loaner app. */
@NgModule({
  bootstrap: [AppComponent],
  declarations: [
    AppComponent,
  ],
  imports: [
    BrowserAnimationsModule,
    BrowserModule,
    HttpClientModule,
    MaterialModule,
    LoaderModule,
    LoanerRouterModule,
  ],
  providers: [
    AuthService,
    AuthGuard,
    BootstrapService,
    ConfigService,
    DeviceService,
    LoanerSnackBar,
    ShelfService,
    Title,
    UserService,
    {
      provide: HTTP_INTERCEPTORS,
      useClass: LoanerOAuthInterceptor,
      multi: true,
    },
  ]
})
export class AppModule {
  constructor(matIconRegistry: MatIconRegistry, domSanitizer: DomSanitizer) {
    matIconRegistry.addSvgIcon(
        'checkin',
        // Note(rjamet): The bypassSecurity here can't be refactored: the code
        // is destined to be open-sourced.
        domSanitizer.bypassSecurityTrustResourceUrl('/assets/checkin.svg'));
  }
}
