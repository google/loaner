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

"""Tests for deployments.lib.config."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from absl.testing import absltest
from loaner.deployments.lib import app_constants


class AppConstantsTest(absltest.TestCase):

  def test_app_constants(self):
    instance = app_constants.AppConstants(
        'PROJECT', 'APP_NAME', ['APP_DOMAIN'], 'MY_CUSTOMER',
        'CHROME_CLIENT_ID', 'WEB_CLIENT_ID', 'SECRETS_FILE', 'ADMIN_EMAIL',
        'EMAIL_FROM', 'SUPERADMINS_GROUP',
    )
    self.assertEqual("'AppConstants' for project: 'PROJECT'", str(instance))
    self.assertEqual(
        "<AppConstants(PROJECT, APP_NAME, ['APP_DOMAIN'], MY_CUSTOMER, "
        "CHROME_CLIENT_ID, WEB_CLIENT_ID, SECRETS_FILE, ADMIN_EMAIL, "
        "EMAIL_FROM, SUPERADMINS_GROUP)>",
        repr(instance))
    duplicate = app_constants.AppConstants(
        'PROJECT', 'APP_NAME', ['APP_DOMAIN'], 'MY_CUSTOMER',
        'CHROME_CLIENT_ID', 'WEB_CLIENT_ID', 'SECRETS_FILE', 'ADMIN_EMAIL',
        'EMAIL_FROM', 'SUPERADMINS_GROUP',
    )
    self.assertEqual(instance, duplicate)
    self.assertEqual(instance.to_json(), duplicate.to_json())
    duplicate._project = ''
    self.assertNotEqual(instance, duplicate)


if __name__ == '__main__':
  absltest.main()
