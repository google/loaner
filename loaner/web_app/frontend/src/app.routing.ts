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

import {NgModule} from '@angular/core';
import {RouterModule, Routes} from '@angular/router';

import {CONFIG} from './app.config';
import {Authorization, AuthorizationModule} from './components/authorization';
import {AuthGuard} from './services/auth_guard';
import {AuditView, AuditViewModule} from './views/audit_view';
import {BootstrapView, BootstrapViewModule} from './views/bootstrap_view';
import {DeviceDetailView, DeviceDetailViewModule} from './views/device_detail_view';
import {DeviceListView, DeviceListViewModule} from './views/device_list_view';
import {SearchView, SearchViewModule} from './views/search_view';
import {ShelfActionsView, ShelfActionsViewModule} from './views/shelf_actions_view';
import {ShelfDetailView, ShelfDetailViewModule} from './views/shelf_detail_view';
import {ShelfListView, ShelfListViewModule} from './views/shelf_list_view';
import {UserView, UserViewModule} from './views/user_view';

/** Defines the Angular app routes and which views are loaded on which route. */
const routes: Routes = [
  {path: 'authorization', component: Authorization},
  {
    path: 'bootstrap',
    component: BootstrapView,
    canActivate: [AuthGuard],
    data: {
      'requiredRoles': [CONFIG.roles.TECHNICAL_ADMIN],
    },
  },
  {
    path: 'search',
    children: [
      {
        path: '',
        component: SearchView,
        canActivate: [AuthGuard],
        data: {
          'requiredRoles': [
            CONFIG.roles.TECHNICAL_ADMIN,
            CONFIG.roles.TECHNICIAN,
            CONFIG.roles.OPERATIONAL_ADMIN,
          ],
        },
      },
      {
        path: ':model',
        component: SearchView,
        canActivate: [AuthGuard],
        data: {
          'requiredRoles': [
            CONFIG.roles.TECHNICAL_ADMIN,
            CONFIG.roles.TECHNICIAN,
            CONFIG.roles.OPERATIONAL_ADMIN,
          ],
        },
      },
      {
        path: ':model/:query',
        component: SearchView,
        canActivate: [AuthGuard],
        data: {
          'requiredRoles': [
            CONFIG.roles.TECHNICAL_ADMIN,
            CONFIG.roles.TECHNICIAN,
            CONFIG.roles.OPERATIONAL_ADMIN,
          ],
        },
      },
    ],
  },
  {
    path: 'user',
    children: [
      {
        path: '',
        component: UserView,
        canActivate: [AuthGuard],
        data: {
          'requiredRoles': [CONFIG.roles.USER],
        },
      },
      {
        path: ':id',
        component: UserView,
        canActivate: [AuthGuard],
        data: {
          'requiredRoles': [CONFIG.roles.USER],
        },
      },
    ]
  },
  {
    path: 'devices',
    children: [
      {
        path: '',
        component: DeviceListView,
        canActivate: [AuthGuard],
        data: {
          'requiredRoles': [
            CONFIG.roles.TECHNICAL_ADMIN,
            CONFIG.roles.TECHNICIAN,
            CONFIG.roles.OPERATIONAL_ADMIN,
          ],
        },
      },
      {
        path: ':action',
        component: DeviceListView,
        canActivate: [AuthGuard],
        data: {
          'requiredRoles': [
            CONFIG.roles.TECHNICAL_ADMIN,
            CONFIG.roles.TECHNICIAN,
            CONFIG.roles.OPERATIONAL_ADMIN,
          ],
        },
      },
    ]
  },
  {
    path: 'device/:id',
    component: DeviceDetailView,
    canActivate: [AuthGuard],
    data: {
      'requiredRoles': [
        CONFIG.roles.TECHNICAL_ADMIN,
        CONFIG.roles.TECHNICIAN,
        CONFIG.roles.OPERATIONAL_ADMIN,
      ],
    },
  },
  {
    path: 'shelves',
    component: ShelfListView,
    canActivate: [AuthGuard],
    data: {
      'requiredRoles': [
        CONFIG.roles.TECHNICAL_ADMIN,
        CONFIG.roles.TECHNICIAN,
        CONFIG.roles.OPERATIONAL_ADMIN,
      ],
    },
  },
  {path: 'shelf', redirectTo: 'shelves', pathMatch: 'full'},
  {
    path: 'shelf',
    children: [
      {
        path: 'create',
        pathMatch: 'full',
        component: ShelfActionsView,
        canActivate: [AuthGuard],
        data: {
          'requiredRoles': [
            CONFIG.roles.TECHNICAL_ADMIN,
            CONFIG.roles.TECHNICIAN,
            CONFIG.roles.OPERATIONAL_ADMIN,
          ],
        },
      },
      {
        path: ':id/update',
        component: ShelfActionsView,
        canActivate: [AuthGuard],
        data: {
          'requiredRoles': [
            CONFIG.roles.TECHNICAL_ADMIN,
            CONFIG.roles.TECHNICIAN,
            CONFIG.roles.OPERATIONAL_ADMIN,
          ],
        },
      },
      {
        path: ':id/details',
        component: ShelfDetailView,
        canActivate: [AuthGuard],
        data: {
          'requiredRoles': [
            CONFIG.roles.TECHNICAL_ADMIN,
            CONFIG.roles.TECHNICIAN,
            CONFIG.roles.OPERATIONAL_ADMIN,
          ],
        },
      },
      {
        path: ':id/audit',
        component: AuditView,
        canActivate: [AuthGuard],
        data: {
          'requiredRoles': [
            CONFIG.roles.TECHNICAL_ADMIN,
            CONFIG.roles.TECHNICIAN,
            CONFIG.roles.OPERATIONAL_ADMIN,
          ],
        },
      },
    ]
  },
  {path: '**', redirectTo: 'user'},
];

@NgModule({
  imports: [
    AuthorizationModule,
    AuditViewModule,
    BootstrapViewModule,
    ShelfActionsViewModule,
    DeviceDetailViewModule,
    DeviceListViewModule,
    SearchViewModule,
    ShelfDetailViewModule,
    ShelfListViewModule,
    UserViewModule,
    RouterModule.forRoot(routes),
  ],
  exports: [
    RouterModule,
  ],
})
export class LoanerRouterModule {
}
