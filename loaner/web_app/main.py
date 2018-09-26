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

"""Main WSGI app module for loaner project."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import webapp2

from loaner.web_app import constants
from loaner.web_app.backend.handlers import frontend
from loaner.web_app.backend.handlers import maintenance
from loaner.web_app.backend.handlers.cron import run_custom_events
from loaner.web_app.backend.handlers.cron import run_reminder_events
from loaner.web_app.backend.handlers.cron import run_shelf_audit_events
from loaner.web_app.backend.handlers.cron import sync_user_roles
from loaner.web_app.backend.handlers.task import process_action
from loaner.web_app.backend.handlers.task import stream_to_bigquery


web_app_routes = [
    (r'/_ah/queue/process-action', process_action.ProcessActionHandler),
    (r'/_ah/queue/stream-bq', stream_to_bigquery.StreamToBigQueryHandler),
    (r'/_cron/run_custom_events', run_custom_events.RunCustomEventsHandler),
    (r'/_cron/run_reminder_events',
     run_reminder_events.RunReminderEventsHandler),
    (r'/_cron/run_shelf_audit_events',
     run_shelf_audit_events.RunShelfAuditEventsHandler),
    (r'/_cron/sync_user_roles', sync_user_roles.SyncUserRolesHandler),
    (r'(/.*)', frontend.FrontendHandler),
]

if constants.MAINTENANCE:
  web_app_routes = [(r'/.*', maintenance.MaintenanceHandler)]


web_app = webapp2.WSGIApplication(web_app_routes, debug=True)
