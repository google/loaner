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

"""Module for processing Custom Events in a cron job."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import logging
import webapp2

from loaner.web_app.backend.lib import events
from loaner.web_app.backend.models import device_model  # pylint: disable=unused-import
from loaner.web_app.backend.models import event_models
from loaner.web_app.backend.models import shelf_model  # pylint: disable=unused-import


class RunCustomEventsHandler(webapp2.RequestHandler):
  """Handler for processing Custom Events."""

  def get(self):
    """Process an Action task with the correct Action class."""
    custom_events = event_models.CustomEvent.get_all_enabled()
    for custom_event in custom_events:
      for entity in custom_event.get_matching_entities():
        device = (entity if custom_event.model.lower() == 'device' else None)
        shelf = (entity if custom_event.model.lower() == 'shelf' else None)
        try:
          events.raise_event(
              event_name=custom_event.name, device=device, shelf=shelf)
        except events.EventActionsError as err:
          # We log the error instead of raising an error so that we do not
          # disrupt the handler for executing other devices/shelves when one of
          # them fails.
          logging.error(
              'The following error occurred while trying to perform the event '
              '%r: %s', custom_event.name, err)
