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

import {ComponentFixture, ComponentFixtureAutoDetect, discardPeriodicTasks, fakeAsync, TestBed, tick} from '@angular/core/testing';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {RouterTestingModule} from '@angular/router/testing';
import {of} from 'rxjs';

import {GuestMode} from '../../../../../shared/components/guest';
import {GuestModeMock} from '../../../../../shared/testing/mocks';
import {DeviceService} from '../../services/device';
import {DEVICE_ASSIGNED, DEVICE_DAMAGED, DEVICE_LOCKED, DEVICE_LOST, DEVICE_LOST_AND_MORE, DEVICE_MARKED_FOR_RETURN, DEVICE_OVERDUE, DEVICE_UNASSIGNED, DeviceServiceMock} from '../../testing/mocks';

import {DeviceListTable, DeviceListTableModule} from '.';

describe('DeviceListTableComponent', () => {
  let fixture: ComponentFixture<DeviceListTable>;
  let deviceListTable: DeviceListTable;

  beforeEach(fakeAsync(() => {
    TestBed
        .configureTestingModule({
          imports: [
            RouterTestingModule,
            DeviceListTableModule,
            BrowserAnimationsModule,
          ],
          providers: [
            {provide: ComponentFixtureAutoDetect, useValue: true},
            {provide: DeviceService, useClass: DeviceServiceMock},
            {provide: GuestMode, useClass: GuestModeMock},
          ],
        })
        .compileComponents();

    tick();

    fixture = TestBed.createComponent(DeviceListTable);
    deviceListTable = fixture.debugElement.componentInstance;

    discardPeriodicTasks();
  }));

  it('creates the DeviceList', () => {
    expect(DeviceListTable).toBeDefined();
  });

  it('renders title field "Identifier" inside mat-header-row ', () => {
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    expect(compiled.querySelector('.mat-header-row').textContent)
        .toContain('Identifier');
  });

  it('renders title field "Due date" inside mat-header-row ', () => {
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    expect(compiled.querySelector('.mat-header-row').textContent)
        .toContain('Due date');
  });

  it('renders title field "Model" inside mat-header-row ', () => {
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    expect(compiled.querySelector('.mat-header-row').textContent)
        .toContain('Device Model');
  });

  it('renders title field "Assigned to" inside mat-header-row ', () => {
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    expect(compiled.querySelector('.mat-header-row').textContent)
        .toContain('Assigned to');
  });

  it('does NOT render the assigned or due date title inside mat-header-row ',
     () => {
       deviceListTable.displayedColumns = ['id', 'device_model'];
       fixture.detectChanges();
       const compiled = fixture.debugElement.nativeElement;
       expect(compiled.querySelector('.mat-header-row').textContent)
           .not.toContain('Assigned to');
       expect(compiled.querySelector('.mat-header-row').textContent)
           .not.toContain('Due date');
       expect(compiled.querySelector('.mat-header-row').textContent)
           .toContain('Identifier');
       expect(compiled.querySelector('.mat-header-row').textContent)
           .toContain('Device Model');
     });

  it('pauses loading when a row is in focus', () => {
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    const element = compiled.querySelector('.mat-row');
    element.dispatchEvent(new Event('focus'));
    expect(deviceListTable.pauseLoading).toBe(true);
    element.dispatchEvent(new Event('blur'));
    expect(deviceListTable.pauseLoading).toBe(false);
  });

  it('pauses loading when the row menu trigger is in focus', () => {
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    const element = compiled.querySelector('loaner-device-actions-menu');
    element.dispatchEvent(new Event('focus'));
    expect(deviceListTable.pauseLoading).toBe(true);
    element.dispatchEvent(new Event('blur'));
    expect(deviceListTable.pauseLoading).toBe(false);
  });

  it('shows the assigned chip when device is assigned', fakeAsync(() => {
       const deviceService: DeviceService = TestBed.get(DeviceService);
       spyOn(deviceService, 'list').and.returnValue(of({
         devices: [DEVICE_ASSIGNED],
         totalResults: 1,
         totalPages: 1,
       }));
       deviceListTable.ngAfterViewInit();
       const matChipListContent =
           fixture.debugElement.nativeElement.querySelector('mat-chip-list')
               .textContent;
       expect(matChipListContent).toContain('Assigned');
       discardPeriodicTasks();
     }));

  it('shows the damaged chip when device is damaged', fakeAsync(() => {
       const deviceService: DeviceService = TestBed.get(DeviceService);
       spyOn(deviceService, 'list').and.returnValue(of({
         devices: [DEVICE_DAMAGED],
         totalResults: 1,
         totalPages: 1,
       }));
       deviceListTable.ngAfterViewInit();
       const matChipListContent =
           fixture.debugElement.nativeElement.querySelector('mat-chip-list')
               .textContent;
       expect(matChipListContent).toContain('Damaged');
       discardPeriodicTasks();
     }));

  it('shows the locked chip when device is locked', fakeAsync(() => {
       const deviceService: DeviceService = TestBed.get(DeviceService);
       spyOn(deviceService, 'list').and.returnValue(of({
         devices: [DEVICE_LOCKED],
         totalResults: 1,
         totalPages: 1,
       }));
       deviceListTable.ngAfterViewInit();
       const matChipListContent =
           fixture.debugElement.nativeElement.querySelector('mat-chip-list')
               .textContent;
       expect(matChipListContent).toContain('Locked');
       discardPeriodicTasks();
     }));

  it('shows the lost chip when device is lost', fakeAsync(() => {
       const deviceService: DeviceService = TestBed.get(DeviceService);
       spyOn(deviceService, 'list').and.returnValue(of({
         devices: [DEVICE_LOST_AND_MORE],
         totalResults: 1,
         totalPages: 1,
       }));
       deviceListTable.ngAfterViewInit();
       const matChipListContent =
           fixture.debugElement.nativeElement.querySelector('mat-chip-list')
               .textContent;
       expect(matChipListContent).toContain('Lost');
       discardPeriodicTasks();
     }));

  it('shows the pending return chip when device is pending return',
     fakeAsync(() => {
       const deviceService: DeviceService = TestBed.get(DeviceService);
       spyOn(deviceService, 'list').and.returnValue(of({
         devices: [DEVICE_MARKED_FOR_RETURN],
         totalResults: 1,
         totalPages: 1,
       }));
       deviceListTable.ngAfterViewInit();
       const matChipListContent =
           fixture.debugElement.nativeElement.querySelector('mat-chip-list')
               .textContent;
       expect(matChipListContent).toContain('Pending return');
       discardPeriodicTasks();
     }));

  it('shows the overdue chip when device is overdue', fakeAsync(() => {
       const deviceService: DeviceService = TestBed.get(DeviceService);
       spyOn(deviceService, 'list').and.returnValue(of({
         devices: [DEVICE_OVERDUE],
         totalResults: 1,
         totalPages: 1,
       }));
       deviceListTable.ngAfterViewInit();
       const matChipListContent =
           fixture.debugElement.nativeElement.querySelector('mat-chip-list')
               .textContent;
       expect(matChipListContent).toContain('Overdue');
       discardPeriodicTasks();
     }));

  it('does not show the return and damaged chips if device is lost',
     fakeAsync(() => {
       const deviceService: DeviceService = TestBed.get(DeviceService);
       spyOn(deviceService, 'list').and.returnValue(of({
         devices: [DEVICE_LOST_AND_MORE],
         totalResults: 1,
         totalPages: 1,
       }));

       deviceListTable.ngAfterViewInit();
       const matChipListContent =
           fixture.debugElement.nativeElement.querySelector('mat-chip-list')
               .textContent;
       expect(matChipListContent).toContain('Lost');
       expect(matChipListContent).not.toContain('Pending return');
       expect(matChipListContent).not.toContain('Damaged');

       discardPeriodicTasks();
     }));

  it('shows the unassigned chip when device is unassigned', () => {
    const deviceService: DeviceService = TestBed.get(DeviceService);
    spyOn(deviceService, 'list').and.returnValue(of([DEVICE_UNASSIGNED]));
    fixture.detectChanges();
    const matChipListContent =
        fixture.debugElement.nativeElement.querySelector('mat-chip-list')
            .textContent;
    expect(matChipListContent).toContain('Unassigned');
  });
});
