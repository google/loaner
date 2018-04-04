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

"""Module for the core frontend handler."""

import logging
import os
import re

import webapp2

from loaner.web_app import constants
from loaner.web_app.backend.lib import bootstrap
from loaner.web_app.backend.lib import sync_users

if os.environ.get('TEST_WORKSPACE') == 'gng':
  # The following mocks are here to stub out the npm compiled frontend since
  # Bazel cannot easily build an npm package during tests.
  _ANGULAR_TEMPLATE = 'angular bazel test template'
  _COMPILED_JS = 'compiled_js_during_bazel_tests'
else:
  _ANGULAR_TEMPLATE = open(constants.ANGULAR_TEMPLATE_PATH, 'r').read()
  _COMPILED_JS = open(constants.COMPILED_JS_PATH, 'r').read()
BOOTSTRAP_URL = '/bootstrap'


class FrontendHandler(webapp2.RequestHandler):
  """Handler for serving the Angular frontend or displaying bootstrap status."""

  def __init__(self, *args, **kwargs):
    """Override RequestHandler init to track app readiness."""
    super(FrontendHandler, self).__init__(*args, **kwargs)
    self.bootstrap_started = bootstrap.is_bootstrap_started()
    self.bootstrap_completed = bootstrap.is_bootstrap_completed()

  def get(self, path):
    if path == '/application.js':
      self._serve_frontend_javascript()
      return

    if self.bootstrap_completed or re.match(
        r'^/(bootstrap|authorization)', path):
      self._serve_frontend()
    else:
      self._sync_roles_if_necessary()
      # Re-checks if the bootstrap status did not change since the handler was
      # first loaded.
      self.bootstrap_completed = bootstrap.is_bootstrap_completed()
      if self.bootstrap_completed:
        self.redirect(path)
      else:
        self.redirect(BOOTSTRAP_URL)

  def _serve_frontend(self):
    """Writes Angular Frontend to the response and sets the right content type.
    """
    self.response.headers['Content-Type'] = 'text/html'
    self.response.write(_ANGULAR_TEMPLATE)

  def _serve_frontend_javascript(self):
    """Determines if the javascript to be served is the GAE compiled or dev."""
    self.response.headers['Content-Type'] = 'application/javascript'
    self.response.body_file.write(_COMPILED_JS)

  def _sync_roles_if_necessary(self):
    """Determines if user roles need to be synced before starting bootstrap."""
    if not self.bootstrap_started and not self.bootstrap_completed:
      logging.info(
          'Attempting to sync user roles before bootstrap takes place.')
      sync_users.sync_user_roles()
