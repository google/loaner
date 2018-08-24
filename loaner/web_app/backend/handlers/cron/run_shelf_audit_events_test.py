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

"""Tests for backend.handlers.cron.run_shelf_audit_events."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import datetime

import mock

from loaner.web_app.backend.clients import directory  # pylint: disable=unused-import
from loaner.web_app.backend.lib import events  # pylint: disable=unused-import
from loaner.web_app.backend.models import config_model
from loaner.web_app.backend.models import event_models
from loaner.web_app.backend.models import shelf_model
from loaner.web_app.backend.testing import handlertest
from loaner.web_app.backend.testing import loanertest

_NOW = datetime.datetime.utcnow()


class RunShelfAuditEventsHandlerTest(handlertest.HandlerTestCase):
  """Test the RunShelfAuditEventsHandler."""

  def setUp(self, *args, **kwargs):
    super(RunShelfAuditEventsHandlerTest, self).setUp(*args, **kwargs)
    event_models.ShelfAuditEvent.create()

  def setup_shelves(self):
    self.shelf1 = shelf_model.Shelf.enroll(
        'test@{}'.format(loanertest.USER_DOMAIN), 'US-AUS', 16, 'Alamo',
        40.6892534, -74.0466891, 1.0, loanertest.USER_EMAIL)
    self.shelf2 = shelf_model.Shelf.enroll(
        'test@{}'.format(loanertest.USER_DOMAIN), 'US-BLD', 24,
        'Overlook Hotel', 40.6892534, -74.0466891, 1.0, loanertest.USER_EMAIL)
    self.shelf3 = shelf_model.Shelf.enroll(
        'test@{}'.format(loanertest.USER_DOMAIN), 'US-CAM', 24, 'Freedom Trail',
        40.6892534, -74.0466891, 1.0, loanertest.USER_EMAIL)
    self.shelf4 = shelf_model.Shelf.enroll(
        'test@{}'.format(loanertest.USER_DOMAIN), 'US-NYC', 24,
        'Statue of Liberty', 40.6892534, -74.0466891, 1.0,
        loanertest.USER_EMAIL)

  def test_no_shelves(self):
    """Tests with no entities in datastore."""
    response = self.testapp.get(r'/_cron/run_shelf_audit_events')

    self.assertEqual(response.status_int, 200)
    self.assertFalse(self.testbed.mock_raiseevent.called)

  def test_shelves(self):
    """Tests with two shelves, and only one raises the event."""
    shelf_audit_interval = 24
    config_model.Config.set('shelf_audit_interval', shelf_audit_interval)
    self.setup_shelves()

    # Shelf ready for notifications but recently audited.
    self.shelf1.audit_notification_enabled = True
    self.shelf1.audit_requested = False
    self.shelf1.last_audit_time = _NOW - datetime.timedelta(
        hours=shelf_audit_interval - 1)
    self.shelf1.put()

    # Shelf ready for notifications and not audited in a while.
    self.shelf2.audit_notification_enabled = True
    self.shelf2.audit_requested = False
    self.shelf2.last_audit_time = _NOW - datetime.timedelta(
        hours=shelf_audit_interval + 1)
    self.shelf2.put()

    # Shelf disabled for notifications
    self.shelf3.audit_notification_enabled = False
    self.shelf3.audit_requested = False
    self.shelf3.put()

    # Shelf already notified.
    self.shelf4.audit_notification_enabled = True
    self.shelf4.audit_requested = True
    self.shelf4.put()

    # Shelf ready for notifications but has not been audited ever.
    shelf5 = shelf_model.Shelf.enroll(
        'test@{}'.format(loanertest.USER_DOMAIN), 'US-WAS', 24,
        'Washington', 40.6892534, -74.0466891, 1.0,
        loanertest.USER_EMAIL)
    shelf5.audit_notification_enabled = True
    shelf5.audit_requested = False
    shelf5.last_audit_time = None

    self.testbed.mock_raiseevent.reset_mock()

    response = self.testapp.get(r'/_cron/run_shelf_audit_events')

    self.assertEqual(response.status_int, 200)
    self.assertTrue(self.testbed.mock_raiseevent.called)
    expected_calls = [
        mock.call(event_name='shelf_needs_audit', shelf=self.shelf2)
    ]
    self.assertListEqual(
        self.testbed.mock_raiseevent.mock_calls, expected_calls)

  def test_shelves_with_overrides(self):
    """Tests with two shelves, both have overrides, reversing results."""
    shelf_audit_interval = 24
    config_model.Config.set('shelf_audit_interval', shelf_audit_interval)
    self.setup_shelves()

    # Shelf ready for notifications but recently audited.
    self.shelf1.audit_notification_enabled = True
    self.shelf1.audit_requested = False
    self.shelf1.last_audit_time = _NOW - datetime.timedelta(
        hours=shelf_audit_interval - 1)
    self.shelf1.audit_interval_override = 22  # Override makes it more strict.
    self.shelf1.put()

    # Shelf ready for notifications and not audited in a while.
    self.shelf2.audit_notification_enabled = True
    self.shelf2.audit_requested = False
    self.shelf2.last_known_healthy = _NOW - datetime.timedelta(
        hours=shelf_audit_interval + 1)
    self.shelf2.audit_interval_override = 26  # Override makes it more lenient.
    self.shelf2.put()

    # Shelf disabled for notifications
    self.shelf3.audit_notification_enabled = False
    self.shelf3.audit_requested = False
    self.shelf3.put()

    # Shelf already notified.
    self.shelf4.audit_notification_enabled = True
    self.shelf4.audit_requested = True
    self.shelf4.put()

    self.testbed.mock_raiseevent.reset_mock()

    response = self.testapp.get(r'/_cron/run_shelf_audit_events')

    self.assertEqual(response.status_int, 200)
    self.assertTrue(self.testbed.mock_raiseevent.called)
    expected_calls = [
        mock.call(event_name='shelf_needs_audit', shelf=self.shelf1)
    ]
    self.assertListEqual(
        self.testbed.mock_raiseevent.mock_calls, expected_calls)


if __name__ == '__main__':
  handlertest.main()
