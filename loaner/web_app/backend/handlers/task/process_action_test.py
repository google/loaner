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

      def run(self, **kwargs):  # pylint: disable=unused-argument, invalid-name
        """Run the action."""
        other_arg = kwargs.get('other_arg')
        logging.info('Action complete, and other_arg is %d.', other_arg)

    mock_importactions.return_value = {'sample': ActionSample()}
    payload = pickle.dumps({'action_name': 'sample', 'other_arg': 42})
    response = self.testapp.post(r'/_ah/queue/process-action', payload)

    self.assertEqual(response.status_int, 200)
    self.assertEqual(mock_loginfo.call_count, 2)
    expected_calls = [
        mock.call('ProcessActionHandler loaded %d actions: %s', 1,
                  "['sample']"),
        mock.call('Action complete, and other_arg is %d.', 42)
    ]
    mock_loginfo.assert_has_calls(expected_calls)


if __name__ == '__main__':
  handlertest.main()
