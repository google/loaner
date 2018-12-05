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

"""Base class for tests in loaner.example.com."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import datetime

import mock

from google.appengine.api import taskqueue
from google.appengine.api import users
from google.appengine.ext import testbed

from absl.testing import absltest
import endpoints

from loaner.web_app import constants
from loaner.web_app.backend.lib import action_loader
from loaner.web_app.backend.lib import events
from loaner.web_app.backend.models import user_model

USER_DOMAIN = constants.APP_DOMAINS[0]
USER_EMAIL = 'user@{}'.format(USER_DOMAIN)
SUPER_ADMIN_EMAIL = 'super_admin@{}'.format(USER_DOMAIN)
TECHNICAL_ADMIN_EMAIL = 'technical-admin@{}'.format(USER_DOMAIN)
TECHNICIAN_EMAIL = 'technician@{}'.format(USER_DOMAIN)

TEST_DIR_DEVICE_DEFAULT = {
    # A test device response from the Cloud Directory API in the Default OU.
    'deviceId': 'unique_id',
    'serialNumber': '123456',
    'status': 'ACTIVE',
    'lastSync': datetime.datetime.utcnow(),
    'model': 'HP Chromebook 13 G1',
    'orgUnitPath': constants.ORG_UNIT_DICT['DEFAULT'],
}

TEST_DIR_DEVICE_GUEST = {
    # A test device response from the Cloud Directory API in the Default OU.
    'deviceId': 'unique_id',
    'serialNumber': '123456',
    'status': 'ACTIVE',
    'lastSync': datetime.datetime.utcnow(),
    'model': 'HP Chromebook 13 G1',
    'orgUnitPath': constants.ORG_UNIT_DICT['GUEST'],
}

TEST_DIR_DEVICE1 = {
    # A test device response from the Cloud Directory API to test OU moves.
    'deviceId': 'unique_id',
    'serialNumber': '123456',
    'status': 'ACTIVE',
    'lastSync': datetime.datetime.utcnow(),
    'model': 'HP Chromebook 13 G1',
    'orgUnitPath': '/',
}

TEST_DIR_DEVICE2 = {
    # A second test device response from the Cloud Directory API.
    'deviceId': 'unique_id2',
    'serialNumber': '654321',
    'status': 'ACTIVE',
    'lastSync': datetime.datetime.utcnow(),
    'model': 'HP Chromebook 13 G1',
    'orgUnitPath': constants.ORG_UNIT_DICT['DEFAULT'],
}


class TestCase(absltest.TestCase):
  """Base test case."""

  def setUp(self):
    """Set up the environment for testing."""
    super(TestCase, self).setUp()
    self.testbed = testbed.Testbed()
    self.testbed.activate()
    self.testbed.init_datastore_v3_stub()
    self.testbed.init_memcache_stub()
    self.testbed.init_user_stub()
    self.testbed.init_search_stub()
    self.testbed.init_taskqueue_stub()
    self.login_user()

    taskqueue_patcher = mock.patch.object(taskqueue, 'add')
    self.addCleanup(taskqueue_patcher.stop)
    self.taskqueue_add = taskqueue_patcher.start()
    self.taskqueue_stub = self.testbed.get_stub(testbed.TASKQUEUE_SERVICE_NAME)

    # The events.raise_event method raises an exception if there are no events
    # in datastore. It's called often in the model methods, many of which are
    # used in testing. When you want to test raise_event specifically, first run
    # stop() on this patcher; be sure to run start() again before end of test.
    def side_effect(event_name, device=None, shelf=None):
      """Side effect for raise_event that returns the model."""
      del event_name  # Unused.
      if device:
        return device
      else:
        return shelf

    self.testbed.mock_raiseevent = mock.Mock(side_effect=side_effect)
    self.testbed.raise_event_patcher = mock.patch.object(
        events, 'raise_event', self.testbed.mock_raiseevent)
    self.addCleanup(self.testbed.raise_event_patcher.stop)
    self.testbed.raise_event_patcher.start()

  def login_user(
      self, email=USER_EMAIL, user_id='1', organization=None, is_admin=False):
    """Login a User for return of mocked users.get_current_user."""
    self.logout_user()
    if organization is None:
      organization = email.split('@')[-1] if email else ''

    self.testbed.setup_env(
        user_email=email,
        user_id=user_id,
        user_organization=organization,
        user_is_admin=('1' if is_admin else '0'),
        overwrite=True)

  def logout_user(self):
    """Logs out the current user."""
    self.testbed.setup_env(
        user_email='',
        user_id='',
        overwrite=True)

  def tearDown(self):
    """Tear down the testing environment."""
    self.logout_user()
    self.testbed.deactivate()
    super(TestCase, self).tearDown()


class EndpointsTestCase(TestCase):
  """Base test case for Endpoints."""

  def setUp(self):
    super(EndpointsTestCase, self).setUp()

    patcher = mock.patch.object(endpoints, 'get_current_user')
    self.mock_endpoints_get_current_user = patcher.start()
    self.mock_endpoints_get_current_user.return_value = None
    self.addCleanup(patcher.stop)

  def login_endpoints_user(self, email=USER_EMAIL):
    """Logs in a User for return of mocked endpoints.get_current_user."""
    self.mock_endpoints_get_current_user.return_value = users.User(email)
    user_model.User.get_user(email=email)

  def login_admin_endpoints_user(self, email=SUPER_ADMIN_EMAIL):
    """Logs in an admin with all roles."""
    self.mock_endpoints_get_current_user.return_value = users.User(email)
    admin_user = user_model.User.get_user(email=email)
    admin_user.update(superadmin=True)


class ActionTestCase(TestCase):
  """Base test caser for action modules."""

  def setUp(self):
    """Checks imported modules for an action module and includes class."""
    super(ActionTestCase, self).setUp()
    try:
      self.testing_action
    except AttributeError:
      raise EnvironmentError(
          'Create a TestCase setUp method that sets a variable named '
          'self.testing_action containing the name of the action module you '
          'wish to test, then runs the superclass setUp method.')
    actions = action_loader.load_actions([self.testing_action])  # pylint: disable=no-member
    if not (actions.get('sync') or actions.get('async')):
      raise EnvironmentError(
          'The unit test must import at least one valid action module. Verify '
          'that self.testing_action is a string that is the name of a module '
          'in the actions directory.')
    self.action = (
        actions['sync'].get(self.testing_action) or
        actions['async'].get(self.testing_action))


def main():
  absltest.main()


if __name__ == '__main__':
  absltest.main()
