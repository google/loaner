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

import {Component, ViewChild} from '@angular/core';
import {ComponentFixture, TestBed} from '@angular/core/testing';
import {RouterTestingModule} from '@angular/router/testing';

import {BottomNavComponent} from './bottom_nav';
import {BottomNavModule} from './index';

describe('BottomNavComponent', () => {
  let component: SimpleBottomNavTestApp;
  let fixture: ComponentFixture<SimpleBottomNavTestApp>;


  beforeEach(() => {
    TestBed
        .configureTestingModule({
          declarations: [SimpleBottomNavTestApp],
          imports: [
            BottomNavModule,
            RouterTestingModule,
          ],
        })
        .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(SimpleBottomNavTestApp);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create test component', () => {
    expect(component).toBeTruthy();
  });

  it('should display navigation tabs', () => {
    expect(fixture.nativeElement.querySelector('bottom-nav').innerText)
        .toContain('Troubleshoot');
    expect(fixture.nativeElement.querySelector('bottom-nav').innerText)
        .toContain('Status');
    expect(fixture.nativeElement.querySelector('bottom-nav').innerText)
        .toContain('FAQ');
  });
});

@Component({
  selector: 'test-app',
  template: `
<bottom-nav [tabs]="navTabs"></bottom-nav>
  `
})
class SimpleBottomNavTestApp {
  @ViewChild(BottomNavComponent) bottomNav!: BottomNavComponent;
  readonly navTabs = [
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
}
