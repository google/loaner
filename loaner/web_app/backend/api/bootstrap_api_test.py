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
from loaner.web_app.backend.api.messages import bootstrap_messages
from loaner.web_app.backend.testing import loanertest


class BootstrapEndpointsTest(loanertest.EndpointsTestCase):
  """Test the Bootstrap Endpoints API."""

  def setUp(self):
    super(BootstrapEndpointsTest, self).setUp()

    self.service = bootstrap_api.BootstrapApi()
    self.login_admin_endpoints_user()

  def tearDown(self):
    super(BootstrapEndpointsTest, self).tearDown()
    self.service = None

  @mock.patch('__main__.bootstrap_api.bootstrap.run_bootstrap')
  @mock.patch('__main__.bootstrap_api.root_api.Service.check_xsrf_token')
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
    self.assertTrue(mock_runbootstrap.called)
    self.assertEqual(mock_xsrf_token.call_count, 1)
    self.assertCountEqual(
        ['task1', 'task2'], [task.name for task in response.tasks])
    self.assertCountEqual(
        ['Running a task.', 'Running another task'],
        [task.description for task in response.tasks])

  @mock.patch(
      '__main__.bootstrap_api.bootstrap.constants.BOOTSTRAP_ENABLED', True)
  @mock.patch('__main__.bootstrap_api.bootstrap.get_bootstrap_task_status')
  @mock.patch('__main__.bootstrap_api.bootstrap.is_bootstrap_enabled')
  @mock.patch('__main__.bootstrap_api.bootstrap.is_bootstrap_started')
  @mock.patch('__main__.bootstrap_api.bootstrap.is_bootstrap_completed')
  @mock.patch('__main__.bootstrap_api.root_api.Service.check_xsrf_token')
  def test_get_status(
      self, mock_xsrf_token, mock_is_completed, mock_is_started,
      mock_is_enabled, mock_get_task_status):
    """Tests get_status for general status and task details."""
    yesterday = datetime.datetime.utcnow() - datetime.timedelta(days=-1)
    task1_status = {
        'description': 'Bootstrap foo',
        'success': False,
        'timestamp': yesterday,
        'details': 'Task failed'
    }
    task2_status = {
        'description': 'Bootstrap bar',
        'success': True,
        'timestamp': yesterday,
        'details': ''}
    mock_get_task_status.return_value = {
        'task1': task1_status,
        'task2': task2_status
    }
    mock_is_started.return_value = True
    request = message_types.VoidMessage()

    mock_is_enabled.return_value = True
    mock_is_completed.return_value = True
    response = self.service.get_status(request)

    self.assertTrue(response.enabled)
    self.assertTrue(response.started)
    self.assertTrue(response.completed)
    self.assertEqual(mock_xsrf_token.call_count, 1)

    mock_xsrf_token.reset_mock()

    # Enabled False and completed True, so no tasks in response.
    mock_is_enabled.return_value = False
    mock_is_completed.return_value = True
    response = self.service.get_status(request)

    self.assertFalse(response.enabled)
    self.assertTrue(response.completed)
    self.assertEqual(mock_xsrf_token.call_count, 1)

    mock_xsrf_token.reset_mock()

    # Enabled True and completed False, so yes tasks in response.
    mock_is_enabled.return_value = True
    mock_is_completed.return_value = False
    response = self.service.get_status(request)

    self.assertTrue(response.enabled)
    self.assertFalse(response.completed)
    self.assertEqual(mock_xsrf_token.call_count, 1)

    task1_success = [
        task.success for task in response.tasks if task.name == 'task1'][0]
    task2_success = [
        task.success for task in response.tasks if task.name == 'task2'][0]
    self.assertFalse(task1_success)
    self.assertTrue(task2_success)

    mock_xsrf_token.reset_mock()

    # Enabled False and completed False, so yes tasks in response.
    mock_is_enabled.return_value = False
    mock_is_completed.return_value = False
    response = self.service.get_status(request)

    self.assertFalse(response.enabled)
    self.assertFalse(response.completed)
    self.assertEqual(mock_xsrf_token.call_count, 1)

    task1_success = [
        task.success for task in response.tasks if task.name == 'task1'][0]
    task2_success = [
        task.success for task in response.tasks if task.name == 'task2'][0]
    self.assertFalse(task1_success)
    self.assertTrue(task2_success)


if __name__ == '__main__':
  loanertest.main()
