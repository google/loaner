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

# Lint as: python3
"""Tests for web_app.backend.api.messages.bootstrap_messages."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from loaner.web_app.backend.api.messages import bootstrap_messages
from absl.testing import absltest


class BootstrapMessagesPy23MigrationTest(absltest.TestCase):

  def setUp(self):
    super(BootstrapMessagesPy23MigrationTest, self).setUp()
    self.bootstrap_task_kwarg = bootstrap_messages.BootstrapTaskKwarg(
        name='abc', value='def')
    self.bootstrap_task = bootstrap_messages.BootstrapTask(
        name='name_abc', description='description_abc', success=True,
        details='details_abc', kwargs=[self.bootstrap_task_kwarg])

  def testBootstrapTaskKwarg(self):
    bootstrap_task_kwarg = self.bootstrap_task_kwarg
    self.assertEqual('abc', bootstrap_task_kwarg.name)
    self.assertEqual('def', bootstrap_task_kwarg.value)

  def testBootstrapTask(self):
    bootstrap_task = self.bootstrap_task
    self.assertEqual('name_abc', bootstrap_task.name)
    self.assertEqual('description_abc', bootstrap_task.description)
    self.assertTrue(bootstrap_task.success)
    self.assertEqual(None, bootstrap_task.timestamp)
    self.assertEqual('details_abc', bootstrap_task.details)
    self.assertEqual('abc', bootstrap_task.kwargs[0].name)
    self.assertEqual('def', bootstrap_task.kwargs[0].value)

  def testRunBootstrapRequest(self):
    request = bootstrap_messages.RunBootstrapRequest(requested_tasks=[
        self.bootstrap_task])
    self.assertEqual('name_abc', request.requested_tasks[0].name)

  def testRunBootstrapResponse(self):
    response = bootstrap_messages.BootstrapStatusResponse(
        tasks=[self.bootstrap_task], started=True, completed=False,
        app_version='25', running_version='11', is_update=True)
    self.assertEqual('name_abc', response.tasks[0].name)
    self.assertEqual('abc', response.tasks[0].kwargs[0].name)
    self.assertTrue(response.started)
    self.assertFalse(response.completed)
    self.assertEqual('25', response.app_version)
    self.assertEqual('11', response.running_version)
    self.assertTrue(response.is_update)


if __name__ == '__main__':
  absltest.main()
