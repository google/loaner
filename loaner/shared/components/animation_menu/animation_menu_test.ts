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

import {ComponentFixture, TestBed} from '@angular/core/testing';
import {MatDialogRef} from '@angular/material';
import {By} from '@angular/platform-browser';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';

import {AnimationMenuService} from '../../services/animation_menu_service';
import {AnimationMenuServiceMock} from '../../testing/mocks';

import {AnimationMenuComponent} from './index';
import {MaterialModule} from './material_module';

/** Mock material DialogRef. */
class MatDialogRefMock {}

describe('AnimationMenuComponent', () => {
  let component: AnimationMenuComponent;
  let fixture: ComponentFixture<AnimationMenuComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [AnimationMenuComponent],
      imports: [
        BrowserAnimationsModule,
        MaterialModule,
      ],
      providers: [
        {
          provide: AnimationMenuService,
          useClass: AnimationMenuServiceMock,
        },
        {
          provide: MatDialogRef,
          useClass: MatDialogRefMock,
        },
      ],
    });
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(AnimationMenuComponent);
    component = fixture.debugElement.componentInstance;
  });

  it('should create dialog component', () => {
    expect(component).toBeDefined();
  });

  it('should show the slider', () => {
    expect(fixture.debugElement.query(By.css('.mat-dialog-title'))
               .nativeElement.innerText)
        .toBe('Animation Menu');
  });

  it('should render the close button', () => {
    fixture.detectChanges();
    expect(
        fixture.debugElement.query(By.css('#close')).nativeElement.textContent)
        .toContain('Close');
  });
});
