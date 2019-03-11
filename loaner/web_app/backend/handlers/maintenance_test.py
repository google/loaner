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

"""Tests loaner.web_app.backend.handlers.maintenance."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import jinja2
import mock

from loaner.web_app import constants
from loaner.web_app.backend.lib import bootstrap
constants.MAINTENANCE = True
# constants.MAINTENANCE before import main; pylint: disable=g-import-not-at-top
from loaner.web_app.backend.testing import handlertest


class MaintenanceHandlerTest(handlertest.HandlerTestCase):
  """Tests the handler when all traffic should be served to static page."""

  def test_get_constants_maintenance_set(self):
    """Test handler for GET."""
    with mock.patch.object(
        jinja2.Environment, 'get_template') as mock_get_template:
      response = self.testapp.get('/')
      self.assertEqual(response.status_int, 200)
      self.assertEqual(response.content_type, 'text/html')
      mock_get_template.assert_called_once_with('maintenance.html')


constants.MAINTENANCE = False
# Reimport handlertest to set constants.MAINTENANCE to false this time; pylint: disable=g-import-not-at-top, reimported
from loaner.web_app.backend.testing import handlertest


class MaintenanceHandlerUpdateTest(handlertest.HandlerTestCase):
  """Tests the handler when serving traffic during application updates."""

  @mock.patch.object(bootstrap, 'is_bootstrap_completed', return_value=False)
  def test_get_during_app_updates(self, mock_is_bootstrap_started):
    """Test handler for GET while application is being updated."""
    with mock.patch.object(
        jinja2.Environment, 'get_template') as mock_get_template:
      response = self.testapp.get('/maintenance')
      self.assertEqual(response.status_int, 200)
      self.assertEqual(response.content_type, 'text/html')
      mock_get_template.assert_called_once_with('maintenance.html')

  @mock.patch.object(bootstrap, 'is_bootstrap_completed', return_value=True)
  def test_get_no_app_updates(self, mock_is_bootstrap_started):
    """Test handler for GET while application is not being being updated."""
    response = self.testapp.get('/maintenance')
    self.assertEqual(response.status_int, 302)
    self.assertIn('/user', response.location)


if __name__ == '__main__':
  handlertest.main()
