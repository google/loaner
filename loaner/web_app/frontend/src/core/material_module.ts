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

import {CdkTableModule} from '@angular/cdk/table';
import {NgModule} from '@angular/core';
import {FlexLayoutModule} from '@angular/flex-layout';
import {MatAutocompleteModule, MatBadgeModule, MatButtonModule, MatCardModule, MatCheckboxModule, MatChipsModule, MatDatepickerModule, MatDialogModule, MatExpansionModule, MatGridListModule, MatIconModule, MatIconRegistry, MatInputModule, MatListModule, MatMenuModule, MatNativeDateModule, MatPaginatorModule, MatProgressBarModule, MatProgressSpinnerModule, MatSelectModule, MatSidenavModule, MatSlideToggleModule, MatSnackBarModule, MatSortModule, MatTableModule, MatTabsModule, MatToolbarModule, MatTooltipModule,} from '@angular/material';

const MATERIAL_MODULES = [
  CdkTableModule,        FlexLayoutModule,
  MatAutocompleteModule, MatBadgeModule,
  CdkTableModule,        FlexLayoutModule,
  MatAutocompleteModule, MatButtonModule,
  MatCardModule,         MatCheckboxModule,
  MatDialogModule,       MatExpansionModule,
  MatGridListModule,     MatIconModule,
  MatInputModule,        MatListModule,
  MatMenuModule,         MatPaginatorModule,
  MatProgressBarModule,  MatProgressSpinnerModule,
  MatSelectModule,       MatSidenavModule,
  MatSlideToggleModule,  MatSnackBarModule,
  MatSortModule,         MatTableModule,
  MatTabsModule,         MatToolbarModule,
  MatTooltipModule,      MatDatepickerModule,
  MatNativeDateModule,   MatChipsModule,
  MatSlideToggleModule,
];

@NgModule({
  exports: MATERIAL_MODULES,
  imports: MATERIAL_MODULES,
})
export class MaterialModule {
}

export {MatIconRegistry};
