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

"""Tests for backend.handlers.task.process_action."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import pickle

from absl import logging

import mock

from loaner.web_app.backend.lib import action_loader  # pylint: disable=unused-import
from loaner.web_app.backend.models import device_model
from loaner.web_app.backend.testing import handlertest


class ProcessActionHandlerTest(handlertest.HandlerTestCase):
  """Test the ProcessActionHandler."""

  @mock.patch.object(logging, 'info')
  @mock.patch('__main__.action_loader.load_actions')
  def test_process_action_handler(self, mock_importactions, mock_loginfo):
    """Test the ProcessActionHandler, which imports the sample action."""

    class ActionSample(object):
      ACTION_NAME = 'sample'
      FRIENDLY_NAME = 'Sample action'

      def run(self, device=None, shelf=None):
        """Run the action."""
        del shelf  # Unused.
        info = 'Action with a %s.' % device.__class__.__name__
        logging.info(info)

    mock_importactions.return_value = {
        'async': {
            'sample1': ActionSample(),
            'sample2': ActionSample()
        }}
    test_device = device_model.Device()
    payload = pickle.dumps({
        'device': test_device, 'shelf': None,
        'async_actions': ['sample1', 'sample2']})
    response = self.testapp.post(r'/_ah/queue/process-action', payload)

    self.assertEqual(response.status_int, 200)
    expected_calls = [
        mock.call('ProcessActionHandler loaded %d async actions: %s', 2,
                  "['sample1', 'sample2']"),
        mock.call('Action with a Device.')
    ]
    mock_loginfo.assert_has_calls(expected_calls)

    # Task for sample1 Action created a task for sample2 Action.
    self.assertLen(self.taskqueue_add.mock_calls, 1)
    task_payload = pickle.loads(
        self.taskqueue_add.call_args_list[0][1]['payload'])
    self.assertEqual(task_payload['async_actions'], ['sample2'])

if __name__ == '__main__':
  handlertest.main()
