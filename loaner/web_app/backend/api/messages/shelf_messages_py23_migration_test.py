# Copyright 2018 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Lint as: python3
"""Tests for web_app.backend.api.messages.shelf_messages."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import datetime

from loaner.web_app.backend.api.messages import shelf_messages
from absl.testing import absltest


class ShelfMessagesPy23MigrationTest(absltest.TestCase):

  def testShelfRequest(self):
    shelf_req = shelf_messages.ShelfRequest(
        location='FAKE-LOCATION', urlsafe_key='FAKE-URL-SAFE-KEY')
    self.assertEqual(shelf_req.location, 'FAKE-LOCATION')
    self.assertEqual(shelf_req.urlsafe_key, 'FAKE-URL-SAFE-KEY')

  def testShelf(self):
    last_audit_date = datetime.datetime.now()
    shelf = shelf_messages.Shelf(
        enabled=True,
        friendly_name='FAKE-FRIENDLY-NAME',
        location='FAKE-LOCATION',
        identifier='FAKE-IDENTIFIER',
        latitude=20.45,
        longitude=30.85,
        altitude=25.3,
        capacity=10,
        audit_notification_enabled=True,
        audit_requested=False,
        responsible_for_audit='FAKE-AUDIT-PERSON',
        last_audit_time=last_audit_date,
        last_audit_by='FAKE-LAST-AUDIT-PERSON',
        page_token='FAKE-PAGE-TOKEN',
        page_size=50,
        audit_interval_override=20,
        audit_enabled=True)

    self.assertTrue(shelf.enabled)
    self.assertTrue(shelf.audit_enabled)
    self.assertFalse(shelf.audit_requested)
    self.assertTrue(shelf.audit_notification_enabled)

    self.assertEqual(shelf.capacity, 10)
    self.assertEqual(shelf.page_size, 50)
    self.assertEqual(shelf.altitude, 25.3)
    self.assertEqual(shelf.latitude, 20.45)
    self.assertEqual(shelf.longitude, 30.85)
    self.assertEqual(shelf.audit_interval_override, 20)

    self.assertEqual(shelf.last_audit_time, last_audit_date)

    self.assertEqual(shelf.location, 'FAKE-LOCATION')
    self.assertEqual(shelf.identifier, 'FAKE-IDENTIFIER')
    self.assertEqual(shelf.page_token, 'FAKE-PAGE-TOKEN')
    self.assertEqual(shelf.friendly_name, 'FAKE-FRIENDLY-NAME')
    self.assertEqual(shelf.last_audit_by, 'FAKE-LAST-AUDIT-PERSON')
    self.assertEqual(shelf.responsible_for_audit, 'FAKE-AUDIT-PERSON')

  def testEnrollShelfRequest(self):
    enroll_shelf_req = shelf_messages.EnrollShelfRequest(
        friendly_name='FAKE-FRIENDLY-NAME',
        location='FAKE-LOCATION',
        latitude=10.2,
        longitude=5.3,
        altitude=15.7,
        capacity=28,
        audit_notification_enabled=False,
        responsible_for_audit='FAKE-RESPONSIBLE',
        audit_interval_override=34)

    self.assertEqual(enroll_shelf_req.capacity, 28)
    self.assertEqual(enroll_shelf_req.latitude, 10.2)
    self.assertEqual(enroll_shelf_req.longitude, 5.3)
    self.assertEqual(enroll_shelf_req.altitude, 15.7)
    self.assertEqual(enroll_shelf_req.audit_interval_override, 34)

    self.assertFalse(enroll_shelf_req.audit_notification_enabled)

    self.assertEqual(enroll_shelf_req.location, 'FAKE-LOCATION')
    self.assertEqual(enroll_shelf_req.friendly_name, 'FAKE-FRIENDLY-NAME')
    self.assertEqual(enroll_shelf_req.responsible_for_audit, 'FAKE-RESPONSIBLE')

  def testUpdateShelfRequest(self):
    update_shelf_req = shelf_messages.UpdateShelfRequest(
        friendly_name='FAKE-FRIENDLY-NAME',
        location='FAKE-LOCATION',
        capacity=50,
        latitude=20.2,
        longitude=10.3,
        altitude=44.1,
        audit_interval_override=9,
        responsible_for_audit='FAKE-RESPONSIBLE',
        audit_notification_enabled=True)

    self.assertEqual(update_shelf_req.capacity, 50)
    self.assertEqual(update_shelf_req.altitude, 44.1)
    self.assertEqual(update_shelf_req.latitude, 20.2)
    self.assertEqual(update_shelf_req.longitude, 10.3)
    self.assertEqual(update_shelf_req.audit_interval_override, 9)

    self.assertTrue(update_shelf_req.audit_notification_enabled)

    self.assertEqual(update_shelf_req.location, 'FAKE-LOCATION')
    self.assertEqual(update_shelf_req.friendly_name, 'FAKE-FRIENDLY-NAME')
    self.assertEqual(update_shelf_req.responsible_for_audit, 'FAKE-RESPONSIBLE')

  def testListShelfResponse(self):
    list_shelf_resp = shelf_messages.ListShelfResponse(
        shelves=[],
        has_additional_results=True,
        page_token='FAKE-PAGE-TOKEN')

    self.assertListEqual(list_shelf_resp.shelves, [])
    self.assertTrue(list_shelf_resp.has_additional_results)
    self.assertEqual(list_shelf_resp.page_token, 'FAKE-PAGE-TOKEN')

  def testShelfAuditRequest(self):
    shelf_audit_req = shelf_messages.ShelfAuditRequest(
        shelf_request=None,
        device_identifiers=['FAKE-IDENTIFIER-1', 'FAKE-IDENTIFIER-2'])

    self.assertIsNone(shelf_audit_req.shelf_request)
    self.assertListEqual(
        shelf_audit_req.device_identifiers,
        ['FAKE-IDENTIFIER-1', 'FAKE-IDENTIFIER-2'])


if __name__ == '__main__':
  absltest.main()
