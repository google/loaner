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

"""Module for processing the email task queues."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import logging
import webapp2

from google.appengine.api import mail


class EmailTaskHandler(webapp2.RequestHandler):
  """A task to send out an email."""

  def post(self):
    """Processes POST request."""
    kwargs = self.request.params.items()
    email_dict = {}
    for key, value in kwargs:
      email_dict[key] = value

    try:
      mail.send_mail(**email_dict)
    except mail.InvalidEmailError as error:
      logging.error(
          'Email helper failed to send mail due to an error: %s. (Kwargs: %s)',
          error.message, kwargs)
