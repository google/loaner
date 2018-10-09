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

import {Component} from '@angular/core';
import {IT_CONTACT_EMAIL, IT_CONTACT_PHONE, IT_CONTACT_WEBSITE, TROUBLESHOOTING_INFORMATION} from '../../../../../shared/config';

@Component({
  host: {
    'class': 'mat-typography',
  },
  selector: 'troubleshoot',
  templateUrl: './troubleshoot.ng.html',
  styleUrls: ['./troubleshoot.scss'],
})
export class TroubleshootComponent {
  contactEmail?: string;
  contactPhone?: string[];
  contactWebsite?: string;
  troubleshootingInformation: string;

  constructor() {
    if (IT_CONTACT_EMAIL.length > 0) {
      this.contactEmail = IT_CONTACT_EMAIL;
    }

    if (IT_CONTACT_PHONE.length > 0) {
      this.contactPhone = IT_CONTACT_PHONE;
    }

    if (IT_CONTACT_WEBSITE.length > 0) {
      this.contactWebsite = IT_CONTACT_WEBSITE;
    }

    if (TROUBLESHOOTING_INFORMATION.length > 0) {
      this.troubleshootingInformation = TROUBLESHOOTING_INFORMATION;
    } else {
      this.troubleshootingInformation =
          'Contact your IT department for assistance.';
    }
  }
}
