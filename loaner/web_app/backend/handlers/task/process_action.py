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

from google.appengine.api import taskqueue
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
        str(sorted(self.actions['async'].keys())))

  def post(self):
    """Process an async Action task with the correct Action class."""
    payload = pickle.loads(self.request.body)
    async_actions = payload.pop('async_actions')
    action_name = async_actions.pop(0)
    action_instance = self.actions['async'].get(action_name)
    if action_instance:
      try:
        action_instance.run(**payload)
      # pylint: disable=broad-except, because this logic, in which tasks are
      # responsible for spawning subsequent tasks, creates a chain that could be
      # interrupted by any conceivable exception in an action's run method. This
      # handling ensures any further tasks will run.
      except Exception as error:
        logging.exception(
            'Failed to run async Action %r due to error: %r',
            action_name, str(error))
      # pylint: enable=broad-except
    else:
      logging.error('No async Action named %s found.', action_name)

    if async_actions:
      payload['async_actions'] = async_actions
      taskqueue.add(
          queue_name='process-action',
          payload=pickle.dumps(payload),
          target='default')
