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
import {CanDeactivateGuard} from './services/can_deactivate_guard';
import {AuditView, AuditViewModule} from './views/audit_view';
import {BootstrapView, BootstrapViewModule} from './views/bootstrap_view';
import {ConfigurationView, ConfigurationViewModule} from './views/configuration_view';
import {DeviceActionsView, DeviceActionsViewModule} from './views/device_actions_view';
import {DeviceDetailView, DeviceDetailViewModule} from './views/device_detail_view';
import {DeviceListView, DeviceListViewModule} from './views/device_list_view';
import {SearchView, SearchViewModule} from './views/search_view';
import {ShelfActionsView, ShelfActionsViewModule} from './views/shelf_actions_view';
import {ShelfDetailView, ShelfDetailViewModule} from './views/shelf_detail_view';
import {ShelfListView, ShelfListViewModule} from './views/shelf_list_view';
import {UserView, UserViewModule} from './views/user_view';

/** Defines the required permission to see/use the search for shelf/devices. */
export const SEARCH_PERMISSIONS: string[] = [
  CONFIG.appPermissions.READ_DEVICES,
  CONFIG.appPermissions.READ_SHELVES,
];

/** Defines the Angular app routes and which views are loaded on which route. */
const routes: Routes = [
  {path: 'authorization', component: Authorization},
  {
    path: 'bootstrap',
    component: BootstrapView,
    canActivate: [AuthGuard],
    data: {
      'requiredPermissions': [
        CONFIG.appPermissions.BOOTSTRAP,
        CONFIG.appPermissions.READ_CONFIGS,
      ],
    },
  },
  {
    path: 'configuration',
    component: ConfigurationView,
    canActivate: [AuthGuard],
    data: {
      'requiredPermissions': [
        CONFIG.appPermissions.BOOTSTRAP,
        CONFIG.appPermissions.READ_CONFIGS,
        CONFIG.appPermissions.MODIFY_CONFIG,
      ]
    }
  },
  {
    path: 'search',
    children: [
      {
        path: '',
        component: SearchView,
        canActivate: [AuthGuard],
        data: {
          'requiredPermissions': SEARCH_PERMISSIONS,
        },
      },
      {
        path: ':model',
        component: SearchView,
        canActivate: [AuthGuard],
        data: {
          'requiredPermissions': SEARCH_PERMISSIONS,
        },
      },
      {
        path: ':model/:query',
        component: SearchView,
        canActivate: [AuthGuard],
        data: {
          'requiredPermissions': SEARCH_PERMISSIONS,
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
      },
      {
        path: ':id',
        component: UserView,
        canActivate: [AuthGuard],
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
          'requiredPermissions': [
            CONFIG.appPermissions.READ_DEVICES,
            CONFIG.appPermissions.MODIFY_DEVICE,
          ],
        },
      },
      {
        path: ':action',
        component: DeviceActionsView,
        canActivate: [AuthGuard],
        canDeactivate: [CanDeactivateGuard],
        data: {
          'requiredPermissions': [
            CONFIG.appPermissions.MODIFY_DEVICE,
            CONFIG.appPermissions.READ_CONFIGS,
            CONFIG.appPermissions.READ_DEVICES,
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
      'requiredPermissions': [
        CONFIG.appPermissions.READ_DEVICES,
      ],
    },
  },
  {
    path: 'shelves',
    component: ShelfListView,
    canActivate: [AuthGuard],
    data: {
      'requiredPermissions': [
        CONFIG.appPermissions.READ_DEVICES,
        CONFIG.appPermissions.READ_SHELVES,
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
        canDeactivate: [CanDeactivateGuard],
        data: {
          'requiredPermissions': [
            CONFIG.appPermissions.MODIFY_SHELF,
            CONFIG.appPermissions.READ_CONFIGS,
          ],
        },
      },
      {
        path: ':id/update',
        component: ShelfActionsView,
        canActivate: [AuthGuard],
        canDeactivate: [CanDeactivateGuard],
        data: {
          'requiredPermissions': [
            CONFIG.appPermissions.MODIFY_SHELF,
            CONFIG.appPermissions.READ_CONFIGS,
            CONFIG.appPermissions.READ_SHELVES,
          ],
        },
      },
      {
        path: ':id/details',
        component: ShelfDetailView,
        canActivate: [AuthGuard],
        data: {
          'requiredPermissions': [
            CONFIG.appPermissions.READ_DEVICES,
            CONFIG.appPermissions.READ_SHELVES,
          ],
        },
      },
      {
        path: ':id/audit',
        component: AuditView,
        canActivate: [AuthGuard],
        data: {
          'requiredPermissions': [
            CONFIG.appPermissions.READ_DEVICES,
            CONFIG.appPermissions.READ_SHELVES,
            CONFIG.appPermissions.AUDIT_SHELF,
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
    ConfigurationViewModule,
    ShelfActionsViewModule,
    DeviceActionsViewModule,
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
