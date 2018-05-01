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

"""Action to send a shelf audit e-mail."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from loaner.web_app.backend.actions import base_action
from loaner.web_app.backend.lib import send_email


class Error(Exception):
  """General Error class for this module."""


class SendAuditError(Error):
  """Error raised when we cannot send a shelf audit request email."""


class RequestShelfAudit(base_action.BaseAction):
  """Action class to request a shelf audit."""

  ACTION_NAME = 'request_shelf_audit'
  FRIENDLY_NAME = 'Request shelf audit'

  def run(self, **kwargs):
    """Request a shelf audit."""
    shelf = kwargs.get('shelf')
    if not shelf:
      raise SendAuditError(
          'Cannot send audit request. Task did not receive a shelf; only '
          'kwargs: {}'.format(str(kwargs)))
    send_email.send_shelf_audit_email(shelf)
    shelf.audit_requested = True
    shelf.put()
