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

"""Tests for backend.handlers.frontend."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import httplib
import mock

from loaner.web_app import constants
from loaner.web_app.backend.clients import directory  # pylint: disable=unused-import
from loaner.web_app.backend.handlers import frontend
from loaner.web_app.backend.lib import bootstrap  # pylint: disable=unused-import
from loaner.web_app.backend.models import config_model
from loaner.web_app.backend.testing import handlertest


class FrontendHandlerTestAuth(handlertest.HandlerTestCase):
  """Test FrontendHandler with various auth errors."""

  def test_no_user(self):
    self.logout_user()

    response = self.testapp.get(r'/', expect_errors=True)

    self.assertEqual(response.status_int, httplib.UNAUTHORIZED)

  def test_wrong_domain(self):
    current_domains = constants.APP_DOMAINS
    def _reset_app_domain():
      constants.APP_DOMAINS = current_domains
    self.addCleanup(_reset_app_domain)
    constants.APP_DOMAINS = ['not-example.com']
    self.testbed.setup_env(
        user_email='user@example.com',
        user_id='1',
        user_is_admin='0',
        overwrite=True)

    response = self.testapp.get(r'/', expect_errors=True)

    self.assertEqual(response.status_int, httplib.FORBIDDEN)


class FrontendHandlerTestComplete(handlertest.HandlerTestCase):
  """Test FrontendHandler initialized with bootstrap already done."""

  def setUp(self, *args, **kwargs):
    self.patcher_isbootstrapcompleted = mock.patch(
        '__main__.bootstrap.is_bootstrap_completed', return_value=True)
    self.patcher_redirect = mock.patch.object(
        frontend.FrontendHandler, 'redirect')
    self.mock_isbootstrapcompleted = self.patcher_isbootstrapcompleted.start()
    self.mock_redirect = self.patcher_redirect.start()

    self.patcher_directory = mock.patch(
        '__main__.directory.DirectoryApiClient')
    self.mock_directoryclass = self.patcher_directory.start()

    self.addCleanup(self.patcher_directory.stop)
    self.addCleanup(self.patcher_isbootstrapcompleted.stop)
    self.addCleanup(self.patcher_redirect.stop)

    super(FrontendHandlerTestComplete, self).setUp(*args, **kwargs)

  def test_load(self):
    response = self.testapp.get(r'/')
    self.assertEqual(response.status_int, 200)
    self.assertEqual(response.content_type, 'text/html')
    self.mock_redirect.assert_not_called()

  def test_load_javascript(self):
    response = self.testapp.get(r'/application.js')
    self.assertEqual(response.status_int, 200)
    self.assertEqual(response.content_type, 'application/javascript')


class FrontendHandlerTestIncomplete(handlertest.HandlerTestCase):
  """Test FrontendHandler initialized with bootstrap not completed."""

  def setUp(self, *args, **kwargs):
    self.patcher_isbootstrapcompleted = mock.patch(
        '__main__.bootstrap.is_bootstrap_completed', return_value=False)
    self.patcher_redirect = mock.patch.object(
        frontend.FrontendHandler, 'redirect')
    self.mock_isbootstrapcompleted = self.patcher_isbootstrapcompleted.start()
    self.mock_redirect = self.patcher_redirect.start()

    self.patcher_directory = mock.patch(
        '__main__.directory.DirectoryApiClient')
    self.mock_directoryclass = self.patcher_directory.start()

    self.addCleanup(self.patcher_directory.stop)
    self.addCleanup(self.patcher_isbootstrapcompleted.stop)
    self.addCleanup(self.patcher_redirect.stop)

    super(FrontendHandlerTestIncomplete, self).setUp(*args, **kwargs)

  def test_load(self):
    self.testapp.get(r'/')
    self.mock_redirect.assert_called_once_with('/bootstrap')

  def test_load_bootstrap_flow(self):
    self.testapp.get(r'/bootstrap')
    self.mock_redirect.assert_not_called()

  @mock.patch.object(bootstrap, 'is_bootstrap_started', autospec=True)
  @mock.patch.object(bootstrap, 'is_bootstrap_completed', autospec=True)
  @mock.patch('__main__.frontend.logging.info')
  @mock.patch('__main__.frontend.sync_users.sync_user_roles')
  def test_sync_roles_if_necessary(
      self, mock_sync_user_roles, mock_logging, mock_bootcompleted,
      mock_bootstarted):
    mock_bootstarted.return_value = False
    mock_bootcompleted.return_value = False
    self.testapp.get(r'/')
    assert mock_logging.call_count == 1
    assert mock_sync_user_roles.call_count == 1

    mock_sync_user_roles.reset_mock()

    mock_bootstarted.return_value = True
    mock_bootcompleted.return_value = True
    self.testapp.get(r'/')
    assert mock_sync_user_roles.call_count == 0


class FrontendHandlerTestChangeBootstrapStatus(handlertest.HandlerTestCase):
  """Test FrontendHandler initialized with bootstrap completed after init."""

  def setUp(self, *args, **kwargs):
    self.patcher_isbootstrapcompleted = mock.patch(
        '__main__.bootstrap.is_bootstrap_completed', return_value=False)
    self.patcher_redirect = mock.patch.object(
        frontend.FrontendHandler, 'redirect')
    self.mock_isbootstrapcompleted = self.patcher_isbootstrapcompleted.start()
    self.mock_redirect = self.patcher_redirect.start()

    self.patcher_directory = mock.patch(
        '__main__.directory.DirectoryApiClient')
    self.mock_directoryclass = self.patcher_directory.start()

    self.addCleanup(self.patcher_directory.stop)
    self.addCleanup(self.patcher_isbootstrapcompleted.stop)
    self.addCleanup(self.patcher_redirect.stop)

    super(FrontendHandlerTestChangeBootstrapStatus, self).setUp(*args, **kwargs)

  def test_load(self):
    self.testapp.get(r'/')
    config_model.Config.set('bootstrap_completed', True)
    config_model.Config.set('bootstrap_started', True)
    self.mock_redirect.assert_called_once_with('/bootstrap')

    self.mock_isbootstrapcompleted.return_value = True  # change from init value

    self.mock_redirect.reset_mock()
    response2 = self.testapp.get(r'/')

    self.assertEqual(response2.status_int, 200)
    self.assertEqual(response2.content_type, 'text/html')
    self.mock_redirect.assert_not_called()


if __name__ == '__main__':
  handlertest.main()
