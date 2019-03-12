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

"""Tests for backend.api.bootstrap_api."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import datetime

import mock

from protorpc import message_types

from loaner.web_app.backend.api import bootstrap_api
from loaner.web_app.backend.api import root_api
from loaner.web_app.backend.api.messages import bootstrap_messages
from loaner.web_app.backend.lib import bootstrap
from loaner.web_app.backend.testing import loanertest


class BootstrapEndpointsTest(loanertest.EndpointsTestCase):
  """Test the Bootstrap Endpoints API."""

  def setUp(self):
    super(BootstrapEndpointsTest, self).setUp()
    self.service = bootstrap_api.BootstrapApi()
    self.login_admin_endpoints_user()

    self.task1_status = {
        'description': 'Bootstrap foo',
        'success': True,
        'timestamp': datetime.datetime.utcnow(),
        'details': 'Task failed'
    }
    self.task2_status = {
        'description': 'Bootstrap bar',
        'success': True,
        'timestamp': datetime.datetime.utcnow(),
        'details': ''}

  def tearDown(self):
    super(BootstrapEndpointsTest, self).tearDown()
    self.service = None

  @mock.patch.object(bootstrap, 'run_bootstrap', autospec=True)
  @mock.patch.object(root_api.Service, 'check_xsrf_token', autospec=True)
  def test_run(self, mock_xsrf_token, mock_runbootstrap):
    """Test bootstrap init."""
    mock_runbootstrap.return_value = {
        'task1': 'Running a task.',
        'task2': 'Running another task'}
    request = bootstrap_messages.RunBootstrapRequest()

    task1 = bootstrap_messages.BootstrapTask(name='task1')
    task1.kwargs = [
        bootstrap_messages.BootstrapTaskKwarg(name='kwarg1', value='42'),
        bootstrap_messages.BootstrapTaskKwarg(
            name='kwarg2', value='This must be Thursday.'),
    ]
    task2 = bootstrap_messages.BootstrapTask(name='task2')
    task2.kwargs = [
        bootstrap_messages.BootstrapTaskKwarg(name='kwarg1', value='1024'),
    ]
    request.requested_tasks = [task1, task2]

    response = self.service.run(request)
    self.assertEqual(mock_runbootstrap.call_count, 1)
    self.assertEqual(mock_xsrf_token.call_count, 1)
    self.assertCountEqual(
        ['task1', 'task2'], [task.name for task in response.tasks])
    self.assertCountEqual(
        ['Running a task.', 'Running another task'],
        [task.description for task in response.tasks])

  @mock.patch.object(bootstrap, 'get_bootstrap_task_status', autospec=True)
  @mock.patch.object(
      bootstrap, 'is_bootstrap_started', autospec=True, return_value=True)
  @mock.patch.object(
      bootstrap, 'is_bootstrap_completed', autospec=True, return_value=True)
  @mock.patch.object(bootstrap, 'is_update', autospec=True, return_value=False)
  @mock.patch.object(root_api.Service, 'check_xsrf_token', autospec=True)
  def test_get_status(
      self, mock_xsrf_token, mock_is_update, mock_is_completed,
      mock_is_started, mock_get_task_status):
    """Tests get_status for general status and task details."""
    mock_get_task_status.return_value = {
        'task1': self.task1_status,
        'task2': self.task2_status
    }

    request = message_types.VoidMessage()
    response = self.service.get_status(request)

    self.assertTrue(response.started)
    self.assertTrue(response.completed)
    self.assertFalse(response.is_update)
    self.assertEqual(response.running_version, '0.0')
    self.assertEqual(response.app_version, bootstrap_api.constants.APP_VERSION)
    for task in response.tasks:
      self.assertTrue(task.success)
    self.assertEqual(mock_xsrf_token.call_count, 1)
    mock_xsrf_token.reset_mock()


if __name__ == '__main__':
  loanertest.main()
