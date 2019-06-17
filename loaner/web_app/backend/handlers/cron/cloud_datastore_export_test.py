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

"""Tests for backend.handlers.cron.cloud_datastore_export."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import datetime
import httplib
import json
import logging

from absl.testing import parameterized
import freezegun
import mock

from google.appengine.api import app_identity
from google.appengine.api import urlfetch

from loaner.web_app import constants
from loaner.web_app.backend.handlers.cron import cloud_datastore_export
from loaner.web_app.backend.models import config_model
from loaner.web_app.backend.testing import handlertest


class DatastoreExportTest(parameterized.TestCase, handlertest.HandlerTestCase):

  _CRON_URL = '/_cron/cloud_datastore_export'

  def setUp(self):
    super(DatastoreExportTest, self).setUp()
    self.testbed.init_app_identity_stub()
    self.testbed.init_urlfetch_stub()
    self.test_application_id = 'test_application_id'
    # Adding `s~` here because os.environ.get returns the application id with
    # a partition followed by the tilde character.
    constants.APPLICATION_ID = 's~' + self.test_application_id

  @mock.patch.object(logging, 'info')
  @mock.patch.object(
      app_identity, 'get_access_token', return_value=('mock_token', None))
  @mock.patch.object(urlfetch, 'fetch')
  @mock.patch.object(config_model.Config, 'get')
  def test_get(
      self, mock_config, mock_urlfetch, mock_app_identity, mock_logging):
    test_destination_url = cloud_datastore_export._DESTINATION_URL
    test_bucket_name = 'gcp_bucket_name'
    mock_config.side_effect = [test_bucket_name, True]
    expected_url = (
        cloud_datastore_export._DATASTORE_API_URL % self.test_application_id)
    mock_urlfetch.return_value.status_code = httplib.OK
    now = datetime.datetime(
        year=2017, month=1, day=1, hour=1, minute=1, second=15)
    with freezegun.freeze_time(now):
      self.testapp.get(self._CRON_URL)
      mock_urlfetch.assert_called_once_with(
          url=expected_url,
          payload=json.dumps({
              'project_id': self.test_application_id,
              'output_url_prefix': test_destination_url.format(
                  test_bucket_name, now.strftime('%Y_%m_%d-%H%M%S'))
          }),
          method=urlfetch.POST,
          deadline=60,
          headers={
              'Content-Type': 'application/json',
              'Authorization': 'Bearer mock_token'})
      self.assertEqual(mock_logging.call_count, 3)

  @mock.patch.object(logging, 'info')
  @mock.patch.object(config_model.Config, 'get', return_value=False)
  def test_get_backups_not_enabled(self, mock_config, mock_logging):
    self.testapp.get(self._CRON_URL)
    mock_logging.assert_called_once_with('Backups are not enabled, skipping.')

  @mock.patch.object(urlfetch, 'fetch', side_effect=urlfetch.Error)
  @mock.patch.object(config_model.Config, 'get')
  def test_get_urlfetch_error(self, mock_config, mock_urlfetch):
    mock_config.side_effect = ['gcp_bucket_name', True]
    response = self.testapp.get(self._CRON_URL, expect_errors=True)
    self.assertEqual(response.status_int, httplib.INTERNAL_SERVER_ERROR)

  @parameterized.named_parameters(
      ('>= 500', httplib.NOT_IMPLEMENTED, 0, 1),
      ('unknown', httplib.METHOD_NOT_ALLOWED, 1, 0),
  )
  @mock.patch.object(cloud_datastore_export, 'logging')
  @mock.patch.object(urlfetch, 'fetch')
  @mock.patch.object(config_model.Config, 'get', return_value=False)
  def test_get_status_code(
      self, status_code, warning_count, error_count, mock_config,
      mock_urlfetch, mock_logging):
    mock_config.side_effect = ['test_bucket_name', True]
    mock_urlfetch.return_value.status_code = status_code
    self.testapp.get(self._CRON_URL, expect_errors=True)
    self.assertEqual(mock_logging.error.call_count, error_count)
    self.assertEqual(mock_logging.warning.call_count, warning_count)

  @parameterized.named_parameters(
      ('bucket_with_prefix', 'gs://test_bucket'),
      ('bucket_without_prefix', 'test_bucket'),
  )
  def test_format_full_path(self, mock_bucket):
    now = datetime.datetime(
        year=2017, month=1, day=1, hour=1, minute=1, second=15)
    with freezegun.freeze_time(now):
      self.assertEqual(
          cloud_datastore_export._format_full_path(mock_bucket),
          'gs://test_bucket/2017_01_01-010115_datastore_backup')


if __name__ == '__main__':
  handlertest.main()
