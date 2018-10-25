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

"""Module for processing Reminder Events in a cron job."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import datetime
from absl import logging
import webapp2

from loaner.web_app.backend.lib import events
from loaner.web_app.backend.models import config_model
from loaner.web_app.backend.models import device_model
from loaner.web_app.backend.models import event_models

_NO_REMINDER_EVENTS_MSG = 'No enabled reminder events.'
_DEVICE_ALREADY_NOTED_MSG = (
    'Device %s already marked to be reminded for level %d.')
_DEVICE_MARKED_RETURNED_MSG = (
    'Device %s is marked returned, and so will not be reminded for level %d.')
_DEVICE_REPEAT_WAITING_MSG = (
    'Device %s already reminded for level %d, and repeat interval '
    'of %d days has not yet elapsed.')
_DEVICE_SET_REMINDER_MSG = (
    'Device %s will get a reminder level %d after %s.')
_DEVICE_REMINDING_NOW_MSG = 'Reminding for Device %s at level %s.'
_EVENT_ACTION_ERROR_MSG = (
    'The following error occurred while trying to set a device reminder: %s')


class RunReminderEventsHandler(webapp2.RequestHandler):
  """Handler for processing Reminder Events."""

  def __init__(self, *args, **kwargs):
    super(RunReminderEventsHandler, self).__init__(*args, **kwargs)
    self.reminder_delay_delta = datetime.timedelta(
        hours=config_model.Config.get('reminder_delay'))

  def get(self):
    """Process the Reminder Action task if need be."""
    self.reminder_events = event_models.ReminderEvent.get_all_enabled()
    if self.request.GET.get('find_remindable_devices') == 'true':
      self._find_remindable_devices()
    if self.request.GET.get('remind_for_devices') == 'true':
      self._remind_for_devices()

  def _find_remindable_devices(self):
    """Find devices in a remindable state and mark them so."""
    if not self.reminder_events:
      logging.error(_NO_REMINDER_EVENTS_MSG)
    for reminder_event in self.reminder_events:
      for device in reminder_event.get_matching_entities():

        # Device has been marked pending return within the grace period.
        if device.mark_pending_return_date:
          logging.info(
              _DEVICE_MARKED_RETURNED_MSG, device.identifier,
              reminder_event.level)
          continue

        # Device already marked for a reminder at this level.
        if device.next_reminder and (
            device.next_reminder.level == reminder_event.level):
          logging.info(
              _DEVICE_ALREADY_NOTED_MSG, device.identifier,
              reminder_event.level)
          continue

        # Device already had a reminder at this level.
        if (
            device.last_reminder and
            device.last_reminder.level == reminder_event.level):

          # We shouldn't remind again.
          if not reminder_event.repeat_interval:
            continue
          else:

            # We shouldn't remind again if insufficient time has elapsed.
            time_since_reminder = (
                datetime.datetime.utcnow() - device.last_reminder.time)
            if (
                time_since_reminder.total_seconds() <
                reminder_event.interval * 86400):
              logging.info(
                  _DEVICE_REPEAT_WAITING_MSG, device.identifier,
                  reminder_event.level, reminder_event.repeat_interval)
              continue

        # We should set a reminder with the delay from configuration settings.
        device.set_next_reminder(
            reminder_event.level, self.reminder_delay_delta)
        logging.info(
            _DEVICE_SET_REMINDER_MSG, device.identifier,
            reminder_event.level, str(device.next_reminder.time))

  def _remind_for_devices(self):
    """Find devices marked as being in a remindable state and raise event."""
    for device in device_model.Device.query(
        device_model.Device.next_reminder.time <= datetime.datetime.utcnow()
    ).fetch():
      logging.info(
          _DEVICE_REMINDING_NOW_MSG, device.identifier,
          device.next_reminder.level)
      try:
        events.raise_event(
            event_name=event_models.ReminderEvent.make_name(
                device.next_reminder.level),
            device=device)
      except events.EventActionsError as err:
        # We log the error so that a single device does not disrupt all other
        # devices that need reminders set.
        logging.error(_EVENT_ACTION_ERROR_MSG, err)
