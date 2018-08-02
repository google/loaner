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

import {OverlayContainer} from '@angular/cdk/overlay';
import {HttpClientModule} from '@angular/common/http';
import {async, ComponentFixture, ComponentFixtureAutoDetect, fakeAsync, flushMicrotasks, TestBed} from '@angular/core/testing';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {Router} from '@angular/router';
import {RouterTestingModule} from '@angular/router/testing';
import {of} from 'rxjs';

import {SearchService} from '../../services/search';
import {LoanerSnackBar} from '../../services/snackbar';
import {UserService} from '../../services/user';
import {TEST_USER_WITHOUT_ADMINISTRATE_LOAN, UserServiceMock} from '../../testing/mocks';

import {SearchBox, SearchBoxModule} from './index';

export const MARKDOWN_EXAMPLE = `# Testing
## 123
### 456
Regular text.
`;

describe('SearchBox', () => {
  let fixture: ComponentFixture<SearchBox>;
  let overlayContainerElement: HTMLElement;
  let searchBox: SearchBox;
  let searchService: SearchService;
  let router: Router;

  beforeEach(fakeAsync(() => {
    TestBed
        .configureTestingModule({
          imports: [
            HttpClientModule,
            RouterTestingModule,
            SearchBoxModule,
            BrowserAnimationsModule,
          ],
          providers: [
            {provide: ComponentFixtureAutoDetect, useValue: true},
            LoanerSnackBar,
            SearchService,
            {provide: UserService, useClass: UserServiceMock},
          ],
        })
        .compileComponents();

    flushMicrotasks();

    fixture = TestBed.createComponent(SearchBox);
    searchBox = fixture.debugElement.componentInstance;
    router = TestBed.get(Router);
    searchService = TestBed.get(SearchService);
    overlayContainerElement =
        TestBed.get(OverlayContainer).getContainerElement();
  }));

  it('should create the SearchBox', () => {
    expect(searchBox).toBeTruthy();
  });

  it('properly sets the styling of the selected input', async(() => {
       searchBox.isFocused = true;
       fixture.detectChanges();

       expect(fixture.debugElement.nativeElement.querySelector(
                  'mat-icon.search-box-focused'))
           .toBeTruthy();
       expect(fixture.debugElement.nativeElement.querySelector(
                  'input.search-box-focused'))
           .toBeTruthy();
       expect(fixture.debugElement.nativeElement.querySelector(
                  'input.search-box-unfocused'))
           .toBeFalsy();
     }));

  it('properly sets the default styling of the input', async(() => {
       searchBox.isFocused = false;
       fixture.detectChanges();

       expect(fixture.debugElement.nativeElement.querySelector(
                  'mat-icon.search-box-focused'))
           .toBeFalsy();

       expect(fixture.debugElement.nativeElement.querySelector(
                  'input.search-box-focused'))
           .toBeFalsy();
       expect(fixture.debugElement.nativeElement.querySelector(
                  'input.search-box-unfocused'))
           .toBeTruthy();
     }));

  it('properly have called the device results with a query of 1', async(() => {
       spyOn(router, 'navigate');
       searchBox.searchText = '1';
       searchBox.search('device');
       fixture.detectChanges();

       expect(router.navigate)
           .toHaveBeenCalledWith(
               ['/search/device/', '1'], Object({skipLocationChange: true}));
       expect(fixture.debugElement.nativeElement.querySelector(
                  'input.search-box-focused'))
           .toBeFalsy();
       expect(fixture.debugElement.nativeElement.querySelector(
                  'input.search-box-unfocused'))
           .toBeTruthy();
     }));

  it('properly have called the shelf results with a query of nyc', async(() => {
       spyOn(router, 'navigate');
       searchBox.searchText = 'nyc';
       searchBox.search('shelf');
       fixture.detectChanges();

       expect(router.navigate)
           .toHaveBeenCalledWith(
               ['/search/shelf/', 'nyc'], Object({skipLocationChange: true}));
       expect(fixture.debugElement.nativeElement.querySelector(
                  'input.search-box-focused'))
           .toBeFalsy();
       expect(fixture.debugElement.nativeElement.querySelector(
                  'input.search-box-unfocused'))
           .toBeTruthy();
     }));

  it('properly works when using the text field to search for a device of 2',
     async(() => {
       spyOn(router, 'navigate');
       const inputElement =
           fixture.debugElement.nativeElement.querySelector('input.search-box');
       searchBox.searchText = '2';
       inputElement.dispatchEvent(new KeyboardEvent('keyup', {
         key: 'Enter',
       }));
       fixture.detectChanges();

       expect(router.navigate)
           .toHaveBeenCalledWith(
               ['/search/device/', '2'], Object({skipLocationChange: true}));
       expect(fixture.debugElement.nativeElement.querySelector(
                  'input.search-box-focused'))
           .toBeFalsy();
       expect(fixture.debugElement.nativeElement.querySelector(
                  'input.search-box-unfocused'))
           .toBeTruthy();
     }));

  it('does not search when the search text is empty', async(() => {
       spyOn(router, 'navigate');
       const inputElement =
           fixture.debugElement.nativeElement.querySelector('input.search-box');
       searchBox.searchText = '';
       inputElement.dispatchEvent(new KeyboardEvent('keyup', {
         key: 'Enter',
       }));
       fixture.detectChanges();

       expect(router.navigate)
           .not.toHaveBeenCalledWith(
               ['/search/device/', ''], Object({skipLocationChange: true}));
     }));

  it('properly works when using the autocomplete to search for a shelf of magic',
     async(() => {
       spyOn(router, 'navigate');
       searchBox.searchText = 'magic';
       searchBox.autocompleteTrigger.openPanel();
       fixture.detectChanges();
       // tslint:disable-next-line:no-unnecessary-type-assertion Type undefined.
       const autocompleteOptions = overlayContainerElement.querySelectorAll(
                                       'mat-option') as NodeListOf<HTMLElement>;
       autocompleteOptions[1]
           .click();  // We expect this to be the shelf option.
       fixture.detectChanges();

       expect(router.navigate)
           .toHaveBeenCalledWith(
               ['/search/shelf/', 'magic'], Object({skipLocationChange: true}));
       expect(fixture.debugElement.nativeElement.querySelector(
                  'input.search-box-focused'))
           .toBeFalsy();
       expect(fixture.debugElement.nativeElement.querySelector(
                  'input.search-box-unfocused'))
           .toBeTruthy();
     }));

  it('properly works when using the autocomplete to search for a device of 123456',
     async(() => {
       spyOn(router, 'navigate');
       searchBox.searchText = '123456';
       searchBox.autocompleteTrigger.openPanel();
       fixture.detectChanges();
       // tslint:disable-next-line:no-unnecessary-type-assertion Type undefined.
       const autocompleteOptions = overlayContainerElement.querySelectorAll(
                                       'mat-option') as NodeListOf<HTMLElement>;
       autocompleteOptions[0]
           .click();  // We expect this to be the device option.
       fixture.detectChanges();

       expect(router.navigate)
           .toHaveBeenCalledWith(
               ['/search/device/', '123456'],
               Object({skipLocationChange: true}));
       expect(fixture.debugElement.nativeElement.querySelector(
                  'input.search-box-focused'))
           .toBeFalsy();
       expect(fixture.debugElement.nativeElement.querySelector(
                  'input.search-box-unfocused'))
           .toBeTruthy();
     }));

  it('does not search when the search text is empty and shelf is clicked',
     async(() => {
       spyOn(router, 'navigate');
       searchBox.searchText = '';
       searchBox.autocompleteTrigger.openPanel();
       fixture.detectChanges();
       // tslint:disable-next-line:no-unnecessary-type-assertion Type undefined.
       const autocompleteOptions = overlayContainerElement.querySelectorAll(
                                       'mat-option') as NodeListOf<HTMLElement>;
       autocompleteOptions[1]
           .click();  // We expect this to be the shelf option.
       fixture.detectChanges();

       expect(router.navigate)
           .not.toHaveBeenCalledWith(
               ['/search/shelf/', ''], Object({skipLocationChange: true}));
     }));

  it('opens the search helper and displays the text properly', async(() => {
       fixture.debugElement.nativeElement
           .querySelector('button.help-icon-button')
           .click();
       spyOn(searchService, 'getHelp').and.returnValue(of(MARKDOWN_EXAMPLE));
       fixture.detectChanges();

       fixture.whenStable().then(() => {
         const headingTwoElements = overlayContainerElement.querySelectorAll(
                                        'h2') as NodeListOf<HTMLElement>;
         expect(headingTwoElements[0].textContent).toContain('Search helper');
         expect(overlayContainerElement.querySelector('h1')!.textContent)
             .toContain('Testing');
         expect(headingTwoElements[1].textContent).toContain('123');
         expect(overlayContainerElement.querySelector('h3')!.textContent)
             .toContain('456');
         expect(overlayContainerElement.querySelector('p')!.textContent)
             .toContain('Regular text.');
         expect(
             overlayContainerElement.querySelector('button#close')!.textContent)
             .toContain('Close');
       });
     }));

  it('properly works when using the autocomplete to search for a user of test_user',
     async(() => {
       spyOn(router, 'navigate');
       searchBox.searchText = 'test_user';
       searchBox.autocompleteTrigger.openPanel();
       fixture.detectChanges();
       // tslint:disable-next-line:no-unnecessary-type-assertion Type undefined.
       const autocompleteOptions = overlayContainerElement.querySelectorAll(
                                       'mat-option') as NodeListOf<HTMLElement>;
       autocompleteOptions[2].click();  // We expect this to be the user option.
       fixture.detectChanges();

       expect(router.navigate)
           .toHaveBeenCalledWith(
               ['/search/user/', 'test_user'],
               Object({skipLocationChange: true}));
       expect(fixture.debugElement.nativeElement.querySelector(
                  'input.search-box-focused'))
           .toBeFalsy();
       expect(fixture.debugElement.nativeElement.querySelector(
                  'input.search-box-unfocused'))
           .toBeTruthy();
     }));

  it('does not allow an unprivileged user to see the user option', async(() => {
       const userService: UserService = TestBed.get(UserService);
       spyOn(userService, 'whenUserLoaded')
           .and.returnValue(of(TEST_USER_WITHOUT_ADMINISTRATE_LOAN));
       searchBox.ngOnInit();
       fixture.detectChanges();
       searchBox.autocompleteTrigger.openPanel();
       // tslint:disable-next-line:no-unnecessary-type-assertion Type undefined.
       const autocompleteOptions = overlayContainerElement.querySelectorAll(
                                       'mat-option') as NodeListOf<HTMLElement>;
       fixture.detectChanges();

       expect(autocompleteOptions[2]).not.toBeTruthy();
     }));
});
