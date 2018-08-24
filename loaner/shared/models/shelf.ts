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

import {SearchQuery} from './search';

/**
 * Interface with fields for a shelf request.
 */
export declare interface ShelfRequestParams {
  location?: string;
  urlsafe_key?: string;
}

/**
 * Interface with fields that come from our shelf API.
 */
export declare interface ShelfApiParams {
  friendly_name?: string;
  location?: string;
  identifier?: string;
  latitude?: number;
  longitude?: number;
  altitude?: number;
  audit_notification_enabled?: boolean;
  capacity?: number;
  last_audit_time?: Date;
  last_audit_by?: string;
  responsible_for_audit?: string;
  device_identifiers?: string[];
  shelf_request?: ShelfRequestParams;
  page_size?: number;
  page_number?: number;
  query?: SearchQuery;
}

export declare interface ListShelfResponseApiParams {
  shelves: ShelfApiParams[];
  total_results: number;
  total_pages: number;
}

export interface ListShelfResponse {
  shelves: Shelf[];
  totalResults: number;
  totalPages: number;
}

export class Shelf {
  /** The friendly name of a given shelf. */
  friendlyName = '';
  /** The floor location of a given shelf. */
  location = '';
  /** The identifier for a shelf. A string of friendly name or location. */
  identifier = '';
  /** Latitude on which the shelf is located. */
  latitude? = 0;
  /** Longitude on which the shelf is located. */
  longitude? = 0;
  /** Altitude on which the shelf is located. */
  altitude? = 0;
  /** How many devices the shelf can have assigned to it. */
  capacity!: number;
  /** The last time the shelf was audited. */
  lastAuditTime!: Date;
  /** The username of the last person who audited the shelf. */
  lastAuditBy = '';
  /** The group responsible for auditing the shelf. */
  responsibleForAudit = '';
  /** The representation of a shelf request. */
  shelfRequest!: ShelfRequestParams;
  /** Enable audit notifications. */
  auditNotificationEnabled = true;

  /**
   * Property for the shelf name, which is preferred to be it's friendly
   * name or its location if friendly name isn't set.
   */
  get name() {
    return this.friendlyName || this.location;
  }

  constructor(shelf: ShelfApiParams = {}) {
    this.friendlyName = shelf.friendly_name || this.friendlyName;
    this.location = shelf.location || this.location;
    this.identifier = shelf.identifier || this.identifier;
    this.latitude = shelf.latitude || this.latitude;
    this.longitude = shelf.longitude || this.longitude;
    this.altitude = shelf.altitude || this.altitude;
    this.capacity = shelf.capacity || this.capacity;
    this.lastAuditTime = shelf.last_audit_time || this.lastAuditTime;
    this.lastAuditBy = shelf.last_audit_by || this.lastAuditBy;
    this.responsibleForAudit =
        shelf.responsible_for_audit || this.responsibleForAudit;
    this.shelfRequest = shelf.shelf_request || this.shelfRequest;
    this.auditNotificationEnabled =
        shelf.audit_notification_enabled === undefined ?
        this.auditNotificationEnabled :
        shelf.audit_notification_enabled;
  }

  /** Translates the Shelf model object to the API message. */
  toApiMessage(): ShelfApiParams {
    return {
      altitude: this.altitude,
      last_audit_by: this.lastAuditBy,
      last_audit_time: this.lastAuditTime,
      latitude: this.latitude,
      longitude: this.longitude,
      friendly_name: this.friendlyName,
      identifier: this.identifier,
      location: this.location,
      responsible_for_audit: this.responsibleForAudit,
      capacity: this.capacity,
      shelf_request: this.shelfRequest,
      audit_notification_enabled: this.auditNotificationEnabled,
    };
  }
}
