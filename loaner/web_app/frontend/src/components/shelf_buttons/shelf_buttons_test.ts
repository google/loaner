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
import {RouterTestingModule} from '@angular/router/testing';
import {of} from 'rxjs';

import {UserService} from '../../services/user';
import {TEST_USER, TEST_USER_NO_PERMISSIONS, TEST_USER_SUPERADMIN, UserServiceMock} from '../../testing/mocks';

import {ShelfButtons, ShelfButtonsModule} from './index';

describe('ShelfButtonsComponent', () => {
  let fixture: ComponentFixture<ShelfButtons>;
  let componentInstance: ShelfButtons;

  beforeEach(() => {
    TestBed
        .configureTestingModule({
          imports: [
            RouterTestingModule,
            ShelfButtonsModule,
          ],
          providers: [
            {provide: UserService, useClass: UserServiceMock},
          ],
        })
        .compileComponents();

    fixture = TestBed.createComponent(ShelfButtons);
    componentInstance = fixture.debugElement.componentInstance;
  });

  it('creates the ShelfButtons', () => {
    expect(componentInstance).toBeDefined();
  });

  it('shows the ADD NEW SHELF button', () => {
    const userService = TestBed.get(UserService);
    spyOn(userService, 'whenUserLoaded').and.returnValue(of(TEST_USER));
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    const button = compiled.querySelector('button');
    expect(button.textContent).toContain('ADD NEW SHELF');
  });

  it('does NOT show the ADD NEW SHELF button', () => {
    const userService = TestBed.get(UserService);
    spyOn(userService, 'whenUserLoaded')
        .and.returnValue(of(TEST_USER_NO_PERMISSIONS));
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    const button = compiled.querySelector('button');
    expect(button).toBeFalsy();
  });

  it('shows the ADD NEW SHELF button for superadmins', () => {
    const userService = TestBed.get(UserService);
    spyOn(userService, 'whenUserLoaded')
        .and.returnValue(of(TEST_USER_SUPERADMIN));
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    const button = compiled.querySelector('button');
    expect(button.textContent).toContain('ADD NEW SHELF');
  });
});
