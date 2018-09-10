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

"""Tests for backend.models.bootstrap_status_model."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from loaner.web_app.backend.models import bootstrap_status_model
from loaner.web_app.backend.testing import loanertest


class BootStrapStatusModelTest(loanertest.TestCase):

  def test_get_bootstrap_status(self):
    """Tests the BootstrapStatus model."""
    # No entity exists.
    status = bootstrap_status_model.BootstrapStatus.get_by_id('bootstrap_1')
    self.assertEqual(status, None)

    # Put and retrieve.
    status = bootstrap_status_model.BootstrapStatus.get_or_insert('bootstrap_1')
    status.description = 'Bootstrap the foo'
    status.success = True
    status.details = "We're all fine here now, thank you. How are you? "
    status.put()
    status2 = bootstrap_status_model.BootstrapStatus.get_by_id('bootstrap_1')
    self.assertEqual(status, status2)
    self.assertEqual(status.details, status2.details)


if __name__ == '__main__':
  loanertest.main()
