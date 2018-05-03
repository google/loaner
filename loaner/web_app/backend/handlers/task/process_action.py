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

"""Module for processing an action in a task queue."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import pickle

from absl import logging
import webapp2

from loaner.web_app.backend.lib import action_loader


class ProcessActionHandler(webapp2.RequestHandler):
  """Handler for processing Actions."""

  def initialize(self, *args, **kwargs):  # pylint: disable=arguments-differ
    """Overridden initializer that imports all available Actions."""
    super(ProcessActionHandler, self).initialize(*args, **kwargs)

    self.actions = action_loader.load_actions()
    logging.info(
        'ProcessActionHandler loaded %d async actions: %s',
        len(self.actions['async']),
        str(self.actions['async'].keys()))

  def post(self):
    """Process an Action task with the correct Action class."""
    payload = pickle.loads(self.request.body)
    action_name = payload.pop('action_name')
    action_instance = self.actions['async'].get(action_name)
    if action_instance:
      action_instance.run(**payload)
    else:
      logging.error('No async Action named %s found.', action_name)
