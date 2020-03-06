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
"""Tests for web_app.backend.models.bootstrap_status_model_py23_migration."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from datetime import datetime    # pylint: disable=g-importing-member
import mock
from loaner.web_app.backend.models import bootstrap_status_model
from absl.testing import absltest


class BootstrapStatusModelPy23MigrationTest(absltest.TestCase):

  def test_get_bootstrap_status(self):
    mock_date = mock.Mock(return_value=datetime(2020, 3, 1))
    bootstrap_object = bootstrap_status_model.BootstrapStatus(
        description='test_description',
        success=True,
        timestamp=mock_date(),
        details='test_details')
    self.assertIsInstance(bootstrap_object,
                          bootstrap_status_model.BootstrapStatus)
    self.assertEqual(True, bootstrap_object.success)
    self.assertEqual('test_description', bootstrap_object.description)
    self.assertEqual('test_details', bootstrap_object.details)
    self.assertEqual(mock_date(), bootstrap_object.timestamp)


if __name__ == '__main__':
  absltest.main()
