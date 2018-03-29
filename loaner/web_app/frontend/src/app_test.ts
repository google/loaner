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

import {ComponentFixture, fakeAsync, flushMicrotasks, TestBed} from '@angular/core/testing';
import {RouterTestingModule} from '@angular/router/testing';

import {AppComponent, NavigationItem} from './app';
import {CONFIG} from './app.config';
import {AppModule} from './app.module';
import {MaterialModule} from './core/material_module';
import {User} from './models/user';
import {AuthService} from './services/auth';
import {UserService} from './services/user';
import {AuthServiceMock, UserServiceMock} from './testing/mocks';


describe('AppComponent', () => {
  let fixture: ComponentFixture<AppComponent>;
  let app: AppComponent;

  const visibleRoute: NavigationItem = {
    icon: 'laptop_chromebook',
    name: 'TestItem_Visible',
    routerLink: 'user',
    requiredRole: CONFIG.roles.USER,
    hideOnRoutes: []
  };
  const hiddenRoute: NavigationItem = {
    icon: 'laptop_chromebook',
    name: 'TestItem_Hidden',
    routerLink: 'user',
    requiredRole: CONFIG.roles.USER,
    hideOnRoutes: ['']
  };

  beforeEach(fakeAsync(() => {
    TestBed
        .configureTestingModule({
          imports: [AppModule, RouterTestingModule, MaterialModule],
          providers: [
            {provide: AuthService, useClass: AuthServiceMock},
            {provide: UserService, useClass: UserServiceMock},
          ],
        })
        .compileComponents();

    flushMicrotasks();

    fixture = TestBed.createComponent(AppComponent);
    app = fixture.debugElement.componentInstance;
    app.user = new User();
  }));

  it(`should have as title 'Grab n Go Application'`, () => {
    expect(app.title).toEqual('Grab n Go Application');
  });

  it('should have an mat-toolbar tag', () => {
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    expect(compiled.querySelector('mat-toolbar')).toBeTruthy();
  });

  it('should have an mat-sidenav inside an mat-sidenav-container', () => {
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    expect(compiled.querySelector('mat-sidenav-container > mat-sidenav'))
        .toBeTruthy();
  });

  it('should have a menu button inside of mat-toolbar', () => {
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    expect(compiled.querySelector('mat-toolbar button mat-icon').textContent)
        .toContain('menu');
  });

  it('should not render shelves side bar item if is only user', () => {
    app.user = new User({roles: [CONFIG.roles.USER]});
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    compiled
        .querySelectorAll(
            'mat-sidenav-container > mat-sidenav > mat-nav-list > div')
        .forEach((item: Node) => {
          expect(item.textContent).not.toContain('shelves');
          expect(item.textContent).not.toContain('devices');
        });
  });

  it('should render technician sidebar items if a list of roles is passed',
     () => {
       app.user = new User({
         roles: [
           CONFIG.roles.USER,
           CONFIG.roles.TECHNICIAN,
         ]
       });
       fixture.detectChanges();
       const compiled = fixture.debugElement.nativeElement;
       const sideNavListContent =
           compiled
               .querySelector(
                   'mat-sidenav-container > mat-sidenav > mat-nav-list')
               .innerHTML;
       expect(sideNavListContent).toContain('Devices');
       expect(sideNavListContent).toContain('ng-reflect-router-link="devices"');
       expect(sideNavListContent).toContain('Shelves');
       expect(sideNavListContent).toContain('ng-reflect-router-link="shelves"');
     });

  it('should render user sidebar items for user role', () => {
    app.user = new User({
      roles: [
        CONFIG.roles.USER,
      ]
    });
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    const sideNavListContent =
        compiled
            .querySelector('mat-sidenav-container > mat-sidenav > mat-nav-list')
            .innerHTML;
    expect(sideNavListContent).toContain('Report issues');
    expect(sideNavListContent)
       .toContain('https://github.com/google/loaner/issues');
  });

  it('should determine whether a navigation item can be shown', () => {
    app.user = new User({
      roles: [
        CONFIG.roles.USER,
      ]
    });
    app.navigationItems.push(visibleRoute);
    app.navigationItems.push(hiddenRoute);
    fixture.detectChanges();
    expect(app.canShow(visibleRoute)).toBe(true);
    expect(app.canShow(hiddenRoute)).toBe(false);
  });

  it('should hide options for hidden routes', () => {
    app.user = new User({
      roles: [
        CONFIG.roles.USER,
      ]
    });
    app.navigationItems.push(visibleRoute);
    app.navigationItems.push(hiddenRoute);
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    const sideNavListContent =
        compiled
            .querySelector('mat-sidenav-container > mat-sidenav > mat-nav-list')
            .innerHTML;
    expect(sideNavListContent).toContain('TestItem_Visible');
    expect(sideNavListContent).not.toContain('TestItem_Hidden');
  });

  it('should show navigation items only once each', () => {
    app.user = new User({
      roles: [
        CONFIG.roles.USER,
      ]
    });
    app.navigationItems.push({
      icon: 'laptop_chromebook',
      name: 'TestItem_WithRouterLinkAndUrl',
      routerLink: 'user',
      url: '/user',
      requiredRole: CONFIG.roles.USER,
      hideOnRoutes: [],
    });

    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    const sideNavListContent =
        compiled
            .querySelector('mat-sidenav-container > mat-sidenav > mat-nav-list')
            .innerHTML;
    expect(sideNavListContent.split('TestItem_WithRouterLinkAndUrl').length - 1)
        .toBe(1);
  });
});
