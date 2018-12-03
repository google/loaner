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

import * as moment from 'moment';

import {SearchQuery} from './search';
import {Shelf, ShelfApiParams} from './shelf';

/**
 * Interface with fields that come from our device API.
 */
export declare interface DeviceApiParams {
  serial_number?: string;
  asset_tag?: string;
  identifier?: string;
  urlkey?: string;
  damaged?: boolean;
  damaged_reason?: string;
  device_model?: string;
  shelf?: ShelfApiParams;
  assigned_user?: string;
  assignment_date?: Date;
  due_date?: Date;
  last_heartbeat?: Date;
  last_known_healthy?: Date;
  lost?: boolean;
  locked?: boolean;
  pending_return?: boolean;
  mark_pending_return_date?: Date;
  max_extend_date?: Date;
  given_name?: string;
  guest_enabled?: boolean;
  guest_permitted?: boolean;
  page_size?: number;
  page_number?: number;
  query?: SearchQuery;
  overdue?: boolean;
}

export declare interface DeviceRequestApiParams {
  asset_tag?: string;
  chrome_device_id?: string;
  serial_number?: string;
  urlkey?: string;
  identifier?: string;
}

export declare interface ExtendDeviceRequestApiParams {
  device?: DeviceRequestApiParams;
  extend_date?: string;
}

export declare interface MarkAsDamagedRequestApiParams {
  device?: DeviceRequestApiParams;
  damaged_reason?: string;
}

export declare interface ListDevicesResponseApiParams {
  devices: DeviceApiParams[];
  total_results: number;
  total_pages: number;
}

export interface ListDevicesResponse {
  devices: Device[];
  totalResults: number;
  totalPages: number;
}


/** A device model with all its properties and methods. */
export class Device {
  /** Serial number of the device. */
  serialNumber = '';
  /** Asset tag of the device. */
  assetTag = '';
  /** Device's identifier not known upfront, asset tag or serial number. */
  identifier = '';
  /** Urlsafe Key identifier for the device. */
  urlkey = '';
  /** Computer model of the device. */
  deviceModel = 'Unknown Device Model';
  /** Which shelf the device is currently assigned to. */
  shelf!: Shelf;
  /** Which user the device is currently assigned to. */
  assignedUser = '';
  /** Which date the device was assigned to the user. */
  assignmentDate!: Date;
  /** If the device is marked as damaged. */
  damaged = false;
  /** Reason for the device being reported as damaged. */
  damagedReason?: string;
  /** Which date the device should be returned to the shelf. */
  dueDate!: Date;
  /** The last heartbeat from the device to the backend. */
  lastHeartbeat!: Date;
  /** The last check in of the device at a shelf. */
  lastKnownHealthy!: Date;
  /** If the device is in a lost state for the program. */
  lost = false;
  /** If the device is in a locked state for the program. */
  locked = false;
  /** If the device is pending return for a shelf. */
  pendingReturn = false;
  /** If guest has already been enabled for this device. */
  guestEnabled = false;
  /** If guest has been enabled allowed for this device. */
  guestAllowed = false;
  /** The maximum date this device can be extended. */
  maxExtendDate!: Date;
  /** Given name on this loan. */
  givenName = 'there';
  /** Indicates an overdue device. */
  overdue = false;
  /** List of flags relevant to this device. */
  chips: DeviceChip[] = [];

  constructor(device: DeviceApiParams = {}) {
    this.serialNumber = device.serial_number || this.serialNumber;
    this.assetTag = device.asset_tag || this.assetTag;
    this.identifier = device.identifier || this.identifier;
    this.urlkey = device.urlkey || this.urlkey;
    this.damaged = !!device.damaged || this.damaged;
    this.damagedReason = device.damaged_reason || this.damagedReason;
    this.deviceModel = device.device_model || this.deviceModel;
    this.shelf = new Shelf(device.shelf) || this.shelf;
    this.assignedUser = device.assigned_user || this.assignedUser;
    this.assignmentDate = device.assignment_date || this.assignmentDate;
    this.dueDate = device.due_date || this.dueDate;
    this.lastHeartbeat = device.last_heartbeat || this.lastHeartbeat;
    this.lastKnownHealthy = device.last_known_healthy || this.lastKnownHealthy;
    this.lost = device.lost || this.lost;
    this.locked = device.locked || this.locked;
    this.pendingReturn = !!device.mark_pending_return_date ||
        device.pending_return || this.pendingReturn;
    this.maxExtendDate = device.max_extend_date || this.maxExtendDate;
    this.guestEnabled = device.guest_enabled || this.guestEnabled;
    this.guestAllowed = device.guest_permitted || this.guestAllowed;
    this.givenName = device.given_name || this.givenName;
    this.overdue = !!device.overdue || this.overdue;
    this.chips = this.makeChips();
  }

  /**
   * Property to determine if the device can be extended.
   */
  get canExtend(): boolean {
    return !this.pendingReturn &&
        moment().isBefore(this.maxExtendDate, 'day') &&
        moment(this.dueDate).isBefore(this.maxExtendDate, 'day');
  }

  /**
   * Property to calculate amount of time (in ms) until the device is due.
   * A negative value indicates that the device is overdue.
   */
  get timeUntilDue(): number {
    return moment(this.dueDate).diff(moment(), 'ms');
  }

  /** Translates the Device model object to the API message. */
  toApiMessage(): DeviceApiParams {
    return {
      asset_tag: this.assetTag,
      identifier: this.identifier,
      urlkey: this.urlkey,
      assignment_date: this.assignmentDate,
      device_model: this.deviceModel,
      due_date: this.dueDate,
      locked: this.locked,
      lost: this.lost,
      pending_return: this.pendingReturn,
      serial_number: this.serialNumber,
      shelf: this.shelf.toApiMessage(),
      assigned_user: this.assignedUser,
      guest_enabled: this.guestEnabled,
      guest_permitted: this.guestAllowed,
      max_extend_date: this.maxExtendDate,
      given_name: this.givenName,
    };
  }

  /**
   * Creates chips based on the current state of the device.
   */
  private makeChips(): DeviceChip[] {
    const chipsToReturn: DeviceChip[] = [];
    if (!this.assignedUser) {
      chipsToReturn.push({
        icon: 'person_outline',
        label: 'Unassigned',
        tooltip: 'This device is unassigned.',
        color: DeviceChipColor.OK,
        status: DeviceChipStatus.UNASSIGNED,
      });
    } else if (this.overdue) {
      chipsToReturn.push({
        icon: 'event_busy',
        label: 'Overdue',
        tooltip: 'This device is being held past its due date.',
        color: DeviceChipColor.WARNING,
        status: DeviceChipStatus.OVERDUE,
      });
    } else if (this.assignedUser) {
      chipsToReturn.push({
        icon: 'person',
        label: 'Assigned',
        tooltip: `This device is assigned to ${this.assignedUser}`,
        color: DeviceChipColor.PRIMARY,
        status: DeviceChipStatus.ASSIGNED,
      });
    }
    if (this.locked) {
      chipsToReturn.push({
        icon: 'lock',
        label: 'Locked',
        tooltip: 'This device is locked.',
        color: DeviceChipColor.WARNING,
        status: DeviceChipStatus.LOCKED
      });
    }
    if (this.lost) {
      chipsToReturn.push({
        icon: 'gps_off',
        label: 'Lost',
        tooltip: 'This device was marked as lost.',
        color: DeviceChipColor.WARNING,
        status: DeviceChipStatus.LOST,
      });
    } else {
      if (this.pendingReturn) {
        chipsToReturn.push({
          icon: 'exit_to_app',
          label: 'Pending return',
          tooltip: 'This device is pending return.',
          color: DeviceChipColor.ACCENT,
          status: DeviceChipStatus.PENDING_RETURN,
        });
      }
      if (this.damaged) {
        chipsToReturn.push({
          icon: 'build',
          label: 'Damaged',
          tooltip: 'This device is marked as damaged.',
          color: DeviceChipColor.WARNING,
          status: DeviceChipStatus.DAMAGED,
        });
      }
    }

    return chipsToReturn;
  }
}

/**
 * Properties for a device to be enrolled/unenrolled/audited such as its
 * current status and error/success message.
 */
export interface DeviceOnAction {
  deviceId: string;
  status: Status;
  message?: string;
}

/** Device status to be showed in the view during actions */
export enum Status {
  READY = 1,
  ERROR,
  IN_PROGRESS,
}

/** Possible actions that can be taken on devices. */
export enum Actions {
  ENROLL = 'enroll',
  UNENROLL = 'unenroll',
}

export enum DeviceChipColor {
  PRIMARY = 'primary',
  ACCENT = 'accent',
  WARNING = 'warn',
  OK = 'ok',
}

export enum DeviceChipStatus {
  ASSIGNED = 'Assigned',
  DAMAGED = 'Damaged',
  LOCKED = 'Locked',
  LOST = 'Lost',
  PENDING_RETURN = 'Pending return',
  OVERDUE = 'Overdue',
  UNASSIGNED = 'Unassigned',
}

export interface DeviceChip {
  color: DeviceChipColor;
  icon: string;
  label: string;
  status: DeviceChipStatus;
  tooltip: string;
}
