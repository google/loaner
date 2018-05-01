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

"""Tests for backend.lib.xsrf."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import mock

from loaner.web_app import constants
from loaner.web_app.backend.lib import user
from loaner.web_app.backend.lib import xsrf
from loaner.web_app.backend.testing import loanertest


class XsrfTest(loanertest.EndpointsTestCase):

  def setUp(self):
    super(XsrfTest, self).setUp()
    self._reset_xsrf_secret()

    self.request_webapp = mock.MagicMock(spec=xsrf.webapp2.Request)
    self.request_webapp.headers = {}
    self.request_webapp.params = {}
    self.request_webapp.method = 'POST'

    self.response = mock.MagicMock()
    self.get_user = mock.patch.object(user, 'get_user_email')
    self.get_user_stub = self.get_user.start()

  def tearDown(self):
    super(XsrfTest, self).tearDown()
    self.get_user.stop()

  def _reset_xsrf_secret(self):
    for model in xsrf._XsrfSecretKey.query():
      model.key.delete()
    xsrf._xsrf_secret = None

  def test_generate_token_using_user_id_and_secret(self):
    self.get_user_stub.return_value = 'test@{}'.format(loanertest.USER_DOMAIN)
    token1 = xsrf._generate_token(time=42)
    token2 = xsrf._generate_token(time=42)
    self.assertEqual(token1, token2)
    # Force a reload from datastore.
    xsrf._xsrf_secret = None
    token3 = xsrf._generate_token(time=42)
    self.assertEqual(token1, token3)
    # Different user.
    self.get_user_stub.return_value = 'test2@{}'.format(loanertest.USER_DOMAIN)
    token4 = xsrf._generate_token(time=42)
    self.assertNotEqual(token1, token4)
    # Reset secret key.
    self._reset_xsrf_secret()
    self.get_user_stub.return_value = 'test@{}'.format(loanertest.USER_DOMAIN)
    token5 = xsrf._generate_token(time=42)
    self.assertNotEqual(token1, token5)

  def test_generate_token_returns_empty_string_when_no_current_user(self):
    self.get_user_stub.return_value = None
    self.assertEqual('', xsrf._generate_token(time=6))

  def test_validate_request_returns_true_when_not_on_gae(self):
    xsrf.constants.ON_GAE = False
    self.assertTrue(
        xsrf.validate_request(
            request=self.request_webapp, response=self.response))

  def test_validate_request_returns_false_when_token_is_missing(self):
    xsrf.constants.ON_GAE = True
    self.get_user_stub.return_value = 'test@{}'.format(loanertest.USER_DOMAIN)
    self.assertFalse(
        xsrf.validate_request(
            request=self.request_webapp, response=self.response))

  def test_validate_request_returns_false_when_user_not_logged_in(self):
    xsrf.constants.ON_GAE = True
    self.get_user_stub.return_value = None
    self.assertFalse(
        xsrf.validate_request(
            request=self.request_webapp, response=self.response))

  def test_validate_request_returns_true_when_method_is_safe(self):
    self.get_user_stub.return_value = 'test@{}'.format(loanertest.USER_DOMAIN)
    self.request_webapp.method = 'GET'
    self.assertTrue(
        xsrf.validate_request(
            request=self.request_webapp, response=self.response))

  def test_validate_request_returns_true_when_valid_token_in_headers(self):
    self.get_user_stub.return_value = 'test@{}'.format(loanertest.USER_DOMAIN)
    self.request_webapp.headers[constants.XSRF_HEADER] = (
        xsrf._generate_token())
    self.assertTrue(xsrf.validate_request(request=self.request_webapp))

  def test_validate_request_returns_true_when_valid_token_in_params(self):
    self.get_user_stub.return_value = 'test2@{}'.format(loanertest.USER_DOMAIN)
    self.request_webapp.params[constants.XSRF_PARAM] = (xsrf._generate_token())
    self.assertTrue(
        xsrf.validate_request(
            request=self.request_webapp, response=self.response))

  def test_validate_request_returns_false_when_users_differ(self):
    xsrf.constants.ON_GAE = True
    self.get_user_stub.return_value = 'test@{}'.format(loanertest.USER_DOMAIN)
    self.request_webapp.headers[constants.XSRF_HEADER] = (
        xsrf._generate_token())
    self.get_user_stub.return_value = 'test2@{}'.format(loanertest.USER_DOMAIN)
    self.assertFalse(
        xsrf.validate_request(
            request=self.request_webapp, response=self.response))
    self.response.delete_cookie.assert_called_once_with(
        constants.XSRF_COOKIE_NAME)

  def test_validate_request_calls_handler_when_from_endpoints(self):
    # Calls Handler when coming from endpoints.
    xsrf.constants.ON_GAE = True
    self.get_user_stub.return_value = 'test@{}'.format(loanertest.USER_DOMAIN)
    self.assertFalse(
        xsrf.validate_request(
            request=self.request_webapp, response=self.response))
    self.request_webapp.service_path = '/_ah/api/ChromeApi.heartbeat'
    self.assertTrue(
        xsrf.validate_request(
            request=self.request_webapp, response=self.response))

  def test_add_xsrf_token_cookie_without_previouse_token(self):
    self.request_webapp.cookies.get.return_value = None
    xsrf.add_xsrf_token_cookie(self.response)
    self.response.set_cookie.assert_called_once_with(
        constants.XSRF_COOKIE_NAME, mock.ANY, expires=mock.ANY, overwrite=True)

  def test_add_xsrf_token_cookie_with_previous_token(self):
    mock_token = 'd928-Y-Vmpar9IJiJOfJTToxMzk2NTQ5NzcwOTE5ODY5'
    self.request_webapp.cookies.get.return_value = mock_token
    xsrf.add_xsrf_token_cookie(self.response)
    self.response.set_cookie.assert_called_once_with(
        constants.XSRF_COOKIE_NAME, mock.ANY, expires=mock.ANY, overwrite=True)
    returned_token = self.response.set_cookie.call_args[0][1]
    self.assertNotEqual(mock_token, returned_token)


if __name__ == '__main__':
  loanertest.main()
