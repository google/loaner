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

"""Tests for backend.api.root_api."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import mock

from protorpc import message_types

import endpoints

from loaner.web_app.backend.api import root_api
from loaner.web_app.backend.lib import xsrf
from loaner.web_app.backend.testing import loanertest


@root_api.ROOT_API.api_class(resource_name='fake', path='fake')
class FakeApi(root_api.Service):

  @endpoints.method(message_types.VoidMessage, http_method='POST')
  def do_something(self, request):
    self.check_xsrf_token(self.request_state)
    return message_types.VoidMessage()


class RootServiceTest(loanertest.EndpointsTestCase):

  def setUp(self):
    super(RootServiceTest, self).setUp()
    self.service = FakeApi()
    self.root_api_service = root_api.Service()

  def test_check_xsrf_token(self):
    request = message_types.VoidMessage()

    with mock.patch.object(xsrf, 'validate_request') as mock_validate_request:
      mock_validate_request.return_value = True
      self.service.do_something(request)
      self.assertTrue(mock_validate_request.called)

      mock_validate_request.return_value = False
      self.assertRaisesRegexp(
          endpoints.ForbiddenException, 'XSRF',
          self.service.do_something, request)


if __name__ == '__main__':
  loanertest.main()
