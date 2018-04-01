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
import {By} from '@angular/platform-browser';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {RouterTestingModule} from '@angular/router/testing';
import {of} from 'rxjs';

import {GuestMode} from '../../../../../shared/components/guest';
import {GuestModeMock} from '../../../../../shared/testing/mocks';
import {DeviceService} from '../../services/device';
import {DeviceServiceMock, TEST_DEVICE_ASSIGNED, TEST_DEVICE_DAMAGED, TEST_DEVICE_LOCKED, TEST_DEVICE_LOST, TEST_DEVICE_MARKED_FOR_RETURN, TEST_DEVICE_OVERDUE, TEST_DEVICE_UNASSIGNED} from '../../testing/mocks';
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

  it('should create the DeviceList', () => {
    expect(DeviceListTable).toBeDefined();
  });

  it('should render title field "Identifier" inside mat-header-row ', () => {
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    expect(compiled.querySelector('.mat-header-row').textContent)
        .toContain('Identifier');
  });

  it('should render title field "Due date" inside mat-header-row ', () => {
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    expect(compiled.querySelector('.mat-header-row').textContent)
        .toContain('Due date');
  });

  it('should render title field "Model" inside mat-header-row ', () => {
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    expect(compiled.querySelector('.mat-header-row').textContent)
        .toContain('Device Model');
  });

  it('should render title field "Assigned to" inside mat-header-row ', () => {
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    expect(compiled.querySelector('.mat-header-row').textContent)
        .toContain('Assigned to');
  });

  it('should pause loading when a row is in focus', () => {
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    const element = compiled.querySelector('.mat-row');
    element.dispatchEvent(new Event('focus'));
    expect(deviceListTable.pauseLoading).toBe(true);
    element.dispatchEvent(new Event('blur'));
    expect(deviceListTable.pauseLoading).toBe(false);
  });

  it('should pause loading when the row menu trigger is in focus', () => {
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    const element = compiled.querySelector('.mat-icon-button');
    element.dispatchEvent(new Event('focus'));
    expect(deviceListTable.pauseLoading).toBe(true);
    element.dispatchEvent(new Event('blur'));
    expect(deviceListTable.pauseLoading).toBe(false);
  });

  it('it should have opened guest dialog after Enable Guest is clicked.',
     () => {
       const guestModeService: GuestMode = TestBed.get(GuestMode);
       spyOn(guestModeService, 'openDialog');
       const actionsButton = fixture.debugElement.query(By.css('.icon-more'));
       actionsButton.triggerEventHandler('click', null);
       fixture.detectChanges();
       const buttonGuest = fixture.debugElement.query(By.css('.actions-menu'))
                               .query(By.css('.button-guest'));
       buttonGuest.triggerEventHandler('click', null);

       expect(guestModeService.openDialog).toHaveBeenCalled();
     });

  it('should show the assigned chip when device is assigned', () => {
    const deviceService: DeviceService = TestBed.get(DeviceService);
    spyOn(deviceService, 'list').and.returnValue(of([TEST_DEVICE_ASSIGNED]));
    fakeAsync(() => {
      fixture.detectChanges();
      const matChipListContent =
          fixture.debugElement.nativeElement.querySelector('mat-chip-list')
              .textContent;
      expect(matChipListContent).toContain('Assigned');
    });
  });

  it('should show the damaged chip when device is damaged', () => {
    const deviceService: DeviceService = TestBed.get(DeviceService);
    spyOn(deviceService, 'list').and.returnValue(of([TEST_DEVICE_DAMAGED]));
    fakeAsync(() => {
      fixture.detectChanges();
      const matChipListContent =
          fixture.debugElement.nativeElement.querySelector('mat-chip-list')
              .textContent;
      expect(matChipListContent).toContain('Damaged');
    });
  });

  it('should show the locked chip when device is locked', () => {
    const deviceService: DeviceService = TestBed.get(DeviceService);
    spyOn(deviceService, 'list').and.returnValue(of([TEST_DEVICE_LOCKED]));
    fakeAsync(() => {
      fixture.detectChanges();
      const matChipListContent =
          fixture.debugElement.nativeElement.querySelector('mat-chip-list')
              .textContent;
      expect(matChipListContent).toContain('Locked');
    });
  });

  it('should show the lost chip when device is lost', () => {
    const deviceService: DeviceService = TestBed.get(DeviceService);
    spyOn(deviceService, 'list').and.returnValue(of([TEST_DEVICE_LOST]));
    fakeAsync(() => {
      fixture.detectChanges();
      const matChipListContent =
          fixture.debugElement.nativeElement.querySelector('mat-chip-list')
              .textContent;
      expect(matChipListContent).toContain('Lost');
    });
  });

  it('should show the pending return chip when device is pending return',
     () => {
       const deviceService: DeviceService = TestBed.get(DeviceService);
       spyOn(deviceService, 'list')
           .and.returnValue(of([TEST_DEVICE_MARKED_FOR_RETURN]));
       fakeAsync(() => {
         fixture.detectChanges();
         const matChipListContent =
             fixture.debugElement.nativeElement.querySelector('mat-chip-list')
                 .textContent;
         expect(matChipListContent).toContain('Pending return');
       });
     });

  it('should show the overdue chip when device is overdue', () => {
    const deviceService: DeviceService = TestBed.get(DeviceService);
    spyOn(deviceService, 'list').and.returnValue(of([TEST_DEVICE_OVERDUE]));
    fakeAsync(() => {
      fixture.detectChanges();
      const matChipListContent =
          fixture.debugElement.nativeElement.querySelector('mat-chip-list')
              .textContent;
      expect(matChipListContent).toContain('Overdue');
    });
  });

  it('should show the unassigned chip when device is unassigned', () => {
    const deviceService: DeviceService = TestBed.get(DeviceService);
    spyOn(deviceService, 'list').and.returnValue(of([TEST_DEVICE_UNASSIGNED]));
    fakeAsync(() => {
      fixture.detectChanges();
      const matChipListContent =
          fixture.debugElement.nativeElement.querySelector('mat-chip-list')
              .textContent;
      expect(matChipListContent).toContain('Unassigned');
    });
  });

  it('should filter devices by "assigned"', () => {
    const deviceService: DeviceService = TestBed.get(DeviceService);
    spyOn(deviceService, 'list').and.returnValue(of([
      TEST_DEVICE_ASSIGNED,
      TEST_DEVICE_UNASSIGNED,
    ]));
    const filterInput = fixture.debugElement.nativeElement.querySelector(
        'input[placeholder="Filter devices"]');
    filterInput.value = 'assigned';
    fakeAsync(() => {
      fixture.detectChanges();
      const tableContent =
          fixture.debugElement.nativeElement.querySelector('mat-table')
              .textContent;
      expect(tableContent).toContain(TEST_DEVICE_ASSIGNED.id);
      expect(tableContent).not.toContain(TEST_DEVICE_UNASSIGNED.id);
    });
  });

  it('should filter devices by "damaged"', () => {
    const deviceService: DeviceService = TestBed.get(DeviceService);
    spyOn(deviceService, 'list').and.returnValue(of([
      TEST_DEVICE_DAMAGED,
      TEST_DEVICE_ASSIGNED,
    ]));
    const filterInput = fixture.debugElement.nativeElement.querySelector(
        'input[placeholder="Filter devices"]');
    filterInput.value = 'damaged';
    fakeAsync(() => {
      fixture.detectChanges();
      const tableContent =
          fixture.debugElement.nativeElement.querySelector('mat-table')
              .textContent;
      expect(tableContent).toContain(TEST_DEVICE_DAMAGED.id);
      expect(tableContent).not.toContain(TEST_DEVICE_ASSIGNED.id);
    });
  });

  it('should filter devices by "locked"', () => {
    const deviceService: DeviceService = TestBed.get(DeviceService);
    spyOn(deviceService, 'list').and.returnValue(of([
      TEST_DEVICE_LOCKED,
      TEST_DEVICE_ASSIGNED,
    ]));
    const filterInput = fixture.debugElement.nativeElement.querySelector(
        'input[placeholder="Filter devices"]');
    filterInput.value = 'locked';
    fakeAsync(() => {
      fixture.detectChanges();
      const tableContent =
          fixture.debugElement.nativeElement.querySelector('mat-table')
              .textContent;
      expect(tableContent).toContain(TEST_DEVICE_LOCKED.id);
      expect(tableContent).not.toContain(TEST_DEVICE_ASSIGNED.id);
    });
  });

  it('should filter devices by "lost"', () => {
    const deviceService: DeviceService = TestBed.get(DeviceService);
    spyOn(deviceService, 'list').and.returnValue(of([
      TEST_DEVICE_LOST,
      TEST_DEVICE_ASSIGNED,
    ]));
    const filterInput = fixture.debugElement.nativeElement.querySelector(
        'input[placeholder="Filter devices"]');
    filterInput.value = 'lost';
    fakeAsync(() => {
      fixture.detectChanges();
      const tableContent =
          fixture.debugElement.nativeElement.querySelector('mat-table')
              .textContent;
      expect(tableContent).toContain(TEST_DEVICE_LOST.id);
      expect(tableContent).not.toContain(TEST_DEVICE_ASSIGNED.id);
    });
  });

  it('should filter devices by "pending return"', () => {
    const deviceService: DeviceService = TestBed.get(DeviceService);
    spyOn(deviceService, 'list').and.returnValue(of([
      TEST_DEVICE_MARKED_FOR_RETURN,
      TEST_DEVICE_ASSIGNED,
    ]));
    const filterInput = fixture.debugElement.nativeElement.querySelector(
        'input[placeholder="Filter devices"]');
    filterInput.value = 'pending return';
    fakeAsync(() => {
      fixture.detectChanges();
      const tableContent =
          fixture.debugElement.nativeElement.querySelector('mat-table')
              .textContent;
      expect(tableContent).toContain(TEST_DEVICE_MARKED_FOR_RETURN.id);
      expect(tableContent).not.toContain(TEST_DEVICE_ASSIGNED.id);
    });
  });

  it('should filter devices by "overdue"', () => {
    const deviceService: DeviceService = TestBed.get(DeviceService);
    spyOn(deviceService, 'list').and.returnValue(of([
      TEST_DEVICE_OVERDUE,
      TEST_DEVICE_ASSIGNED,
    ]));
    const filterInput = fixture.debugElement.nativeElement.querySelector(
        'input[placeholder="Filter devices"]');
    filterInput.value = 'overdue';
    fakeAsync(() => {
      fixture.detectChanges();
      const tableContent =
          fixture.debugElement.nativeElement.querySelector('mat-table')
              .textContent;
      expect(tableContent).toContain(TEST_DEVICE_OVERDUE.id);
      expect(tableContent).not.toContain(TEST_DEVICE_ASSIGNED.id);
    });
  });

  it('should filter devices by "unassigned"', () => {
    const deviceService: DeviceService = TestBed.get(DeviceService);
    spyOn(deviceService, 'list').and.returnValue(of([
      TEST_DEVICE_ASSIGNED,
      TEST_DEVICE_UNASSIGNED,
    ]));
    const filterInput = fixture.debugElement.nativeElement.querySelector(
        'input[placeholder="Filter devices"]');
    filterInput.value = 'unassigned';
    fakeAsync(() => {
      fixture.detectChanges();
      const tableContent =
          fixture.debugElement.nativeElement.querySelector('mat-table')
              .textContent;
      expect(tableContent).toContain(TEST_DEVICE_UNASSIGNED.id);
      expect(tableContent).not.toContain(TEST_DEVICE_ASSIGNED.id);
    });
  });

  it('should filter devices by partial match: "lo" filters "lost" and "locked"',
     () => {
       const deviceService: DeviceService = TestBed.get(DeviceService);
       spyOn(deviceService, 'list').and.returnValue(of([
         TEST_DEVICE_LOST,
         TEST_DEVICE_LOCKED,
         TEST_DEVICE_ASSIGNED,
       ]));
       const filterInput = fixture.debugElement.nativeElement.querySelector(
           'input[placeholder="Filter devices"]');
       filterInput.value = 'lo';
       fakeAsync(() => {
         fixture.detectChanges();
         const tableContent =
             fixture.debugElement.nativeElement.querySelector('mat-table')
                 .textContent;
         expect(tableContent).not.toContain(TEST_DEVICE_ASSIGNED.id);
       });
     });

  it('should handle multiple filters', () => {
    const deviceService: DeviceService = TestBed.get(DeviceService);
    spyOn(deviceService, 'list').and.returnValue(of([
      TEST_DEVICE_LOST,
      TEST_DEVICE_LOCKED,
      TEST_DEVICE_ASSIGNED,
    ]));
    const filterInput = fixture.debugElement.nativeElement.querySelector(
        'input[placeholder="Filter devices"]');
    filterInput.value = 'assign loc';
    fakeAsync(() => {
      fixture.detectChanges();
      const tableContent =
          fixture.debugElement.nativeElement.querySelector('mat-table')
              .textContent;
      expect(tableContent).toContain(TEST_DEVICE_LOCKED.id);
      expect(tableContent).toContain(TEST_DEVICE_ASSIGNED.id);
      expect(tableContent).not.toContain(TEST_DEVICE_LOST.id);
    });
  });

  it('should filter devices by device identifier', () => {
    const deviceService: DeviceService = TestBed.get(DeviceService);
    spyOn(deviceService, 'list').and.returnValue(of([
      TEST_DEVICE_LOST,
      TEST_DEVICE_LOCKED,
      TEST_DEVICE_ASSIGNED,
    ]));
    const filterInput = fixture.debugElement.nativeElement.querySelector(
        'input[placeholder="Filter devices"]');
    filterInput.value = TEST_DEVICE_ASSIGNED.id;
    fakeAsync(() => {
      fixture.detectChanges();
      const tableContent =
          fixture.debugElement.nativeElement.querySelector('mat-table')
              .textContent;
      expect(tableContent).toContain(TEST_DEVICE_ASSIGNED.id);
      expect(tableContent).not.toContain(TEST_DEVICE_LOCKED.id);
      expect(tableContent).not.toContain(TEST_DEVICE_LOST.id);
    });
  });

  it('should filter devices when searching for username of assignee', () => {
    const deviceService: DeviceService = TestBed.get(DeviceService);
    spyOn(deviceService, 'list').and.returnValue(of([
      TEST_DEVICE_ASSIGNED,
      TEST_DEVICE_UNASSIGNED,
    ]));
    const filterInput = fixture.debugElement.nativeElement.querySelector(
        'input[placeholder="Filter devices"]');
    filterInput.value = TEST_DEVICE_ASSIGNED.assignedUser;
    fakeAsync(() => {
      fixture.detectChanges();
      const tableContent =
          fixture.debugElement.nativeElement.querySelector('mat-table')
              .textContent;
      expect(tableContent).toContain(TEST_DEVICE_ASSIGNED.id);
    });
  });
});
