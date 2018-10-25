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

"""Module for processing Shelf Audit Events in a cron job."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import datetime
import logging
import webapp2

from loaner.web_app.backend.lib import events
from loaner.web_app.backend.models import config_model
from loaner.web_app.backend.models import shelf_model


class RunShelfAuditEventsHandler(webapp2.RequestHandler):
  """Handler for processing Shelf Audit Events."""

  def get(self):
    """Process an Action task with the correct Action class."""
    if config_model.Config.get('shelf_audit'):
      audit_hours = config_model.Config.get('shelf_audit_interval')
      earliest_time = (
          datetime.datetime.utcnow() - datetime.timedelta(hours=audit_hours))
      # pylint: disable=g-explicit-bool-comparison, g-equals-none
      global_setting_query = shelf_model.Shelf.query(
          shelf_model.Shelf.audit_notification_enabled == True,  # pylint: disable=singleton-comparison
          shelf_model.Shelf.audit_requested == False,  # pylint: disable=singleton-comparison
          shelf_model.Shelf.last_audit_time != None,
          shelf_model.Shelf.last_audit_time < earliest_time,
          shelf_model.Shelf.audit_interval_override == None)  # pylint: disable=singleton-comparison

      override_query = shelf_model.Shelf.query(
          shelf_model.Shelf.audit_interval_override != None,
          shelf_model.Shelf.audit_notification_enabled == True,  # pylint: disable=singleton-comparison
          shelf_model.Shelf.audit_requested == False)  # pylint: disable=singleton-comparison
      # pylint: enable=g-explicit-bool-comparison, g-equals-none

      override_shelves = []
      for shelf in override_query.fetch():
        override_earliest_time = (
            datetime.datetime.utcnow() - datetime.timedelta(
                hours=shelf.audit_interval_override))
        if (
            shelf.last_audit_time and
            shelf.last_audit_time < override_earliest_time):
          override_shelves.append(shelf)

      for shelf in override_shelves + global_setting_query.fetch():
        try:
          events.raise_event(event_name='shelf_needs_audit', shelf=shelf)
        except events.EventActionsError as err:
          # We catch the event error and only log that error so that a single
          # shelf will not disrupt requesting audit on all other shelves that
          # may need to be audited.
          logging.error(
              'Failed to request audit for shelf %r because the following '
              'error occurred: %s', shelf.identifier, err)

    else:
      logging.warning('Shelf audit reminders are currently disabled.')
