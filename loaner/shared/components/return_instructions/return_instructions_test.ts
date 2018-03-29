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

import {async, ComponentFixture, TestBed} from '@angular/core/testing';


import {FlowsEnum, LoanerReturnInstructions} from './index';
import {MaterialModule} from './material_module';


describe('LoanerReturnInstructions', () => {
  let app: LoanerReturnInstructions;
  let fixture: ComponentFixture<LoanerReturnInstructions>;

  beforeEach(async(() => {
    TestBed
        .configureTestingModule({
          declarations: [LoanerReturnInstructions],
          imports: [MaterialModule],
        })
        .compileComponents();
  }));

  beforeEach(async(() => {
    fixture = TestBed.createComponent(LoanerReturnInstructions);
    app = fixture.debugElement.componentInstance;
    app.flow = FlowsEnum.ONBOARDING;
    fixture.detectChanges();
  }));


  it('renders the return text for the onboarding flow', () => {
    app.flow = FlowsEnum.ONBOARDING;
    fixture.detectChanges();
    const returnBox =
        fixture.debugElement.nativeElement.querySelector('.return-card');
    expect(returnBox.textContent).toContain(`Before you go!`);
  });

  it('renders the return text for the offboarding flow', () => {
    app.flow = FlowsEnum.OFFBOARDING;
    app.programName = 'Test Program';
    fixture.detectChanges();
    const returnBox =
        fixture.debugElement.nativeElement.querySelector('.return-card');
    expect(returnBox.textContent).toContain(`Thanks for using Test Program!`);
  });
});
