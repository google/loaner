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

"""Tests for backend.models.fleet_model."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from loaner.web_app.backend.models import config_model
from loaner.web_app.backend.models import fleet_model
from loaner.web_app.backend.testing import loanertest


class FleetModelTest(loanertest.TestCase):

  def setUp(self):
    super(FleetModelTest, self).setUp()
    self.config1 = config_model.Config(
        id='string_config', string_value='config value 1').put()
    self.config2 = config_model.Config(
        id='integer_config', integer_value=1).put()

  def test_fleet_name(self):
    """Fleet name should be returned as a string."""
    expected_name = 'empty_example'
    empty_fleet = fleet_model.Fleet.create(
        loanertest.TECHNICAL_ADMIN_EMAIL, expected_name, None, None)
    actual_name = empty_fleet.name
    self.assertEqual(actual_name, expected_name)

  def test_create_fleet(self):
    """Test creating a nominal fleet object."""
    expected_name = 'example_fleet'
    expected_desc = 'A newly created fleet used in a test.'
    expected_configs = [self.config1, self.config2]
    created_fleet = fleet_model.Fleet.create(loanertest.TECHNICAL_ADMIN_EMAIL,
                                             expected_name,
                                             expected_configs,
                                             expected_desc)
    self.assertEqual(created_fleet.name, expected_name)
    self.assertEqual(created_fleet.config, expected_configs)
    self.assertEqual(created_fleet.description, expected_desc)
    self.assertEqual(created_fleet.display_name, expected_name)

  def test_create_fleet__display_name(self):
    """Test defining an alternate display_name for Fleet."""
    expected_display_name = 'something_else'
    created_fleet = fleet_model.Fleet.create(
        loanertest.TECHNICAL_ADMIN_EMAIL, 'example_fleet', None,
        display_name=expected_display_name)
    self.assertEqual(created_fleet.display_name, expected_display_name)

  def test_create_fleet__name_exists(self):
    """Creating a fleet with a duplicate name should raise CreateFleetError."""
    fleet_model.Fleet.create(loanertest.TECHNICAL_ADMIN_EMAIL,
                             'example_fleet', None)
    self.assertRaises(fleet_model.CreateFleetError,
                      fleet_model.Fleet.create,
                      loanertest.TECHNICAL_ADMIN_EMAIL,
                      'example_fleet', None)

  def test_create_fleet__name_blank(self):
    """Creating a fleet with an blank name should raise CreateFleetError."""
    self.assertRaises(fleet_model.CreateFleetError,
                      fleet_model.Fleet.create,
                      loanertest.TECHNICAL_ADMIN_EMAIL, '', None)
    self.assertRaises(fleet_model.CreateFleetError,
                      fleet_model.Fleet.create,
                      loanertest.TECHNICAL_ADMIN_EMAIL, None, None)

  def test_create_fleet__name_invalid(self):
    """Creating a fleet with a non-str name should raise CreateFleetError."""
    self.assertRaises(fleet_model.CreateFleetError,
                      fleet_model.Fleet.create,
                      loanertest.TECHNICAL_ADMIN_EMAIL, 10, None)

  def test_fleet_get_by_name(self):
    """Test fetching a fleet object by name."""
    expected_name = 'empty_example'
    expected_fleet = fleet_model.Fleet.create(
        loanertest.TECHNICAL_ADMIN_EMAIL, expected_name, None)
    actual_fleet = fleet_model.Fleet.get_by_name(expected_name)
    self.assertEqual(actual_fleet, expected_fleet)
    self.assertEqual(actual_fleet.name, expected_name)

  def test_list_all_fleets(self):
    """Test fetching a list of all fleet objects."""
    expected_fleet_names = ['larry', 'curly', 'moe']
    expected_fleets = []
    for name in expected_fleet_names:
      expected_fleets.append(fleet_model.Fleet.create(
          loanertest.TECHNICAL_ADMIN_EMAIL, name, None, None))
    actual_fleets = fleet_model.Fleet.list_all_fleets()
    self.assertCountEqual(actual_fleets, expected_fleets)

  def test_create_default_fleet(self):
    """Test creating the default fleet object."""
    expected_display_name = 'Google'
    actual_fleet = fleet_model.Fleet.default(loanertest.TECHNICAL_ADMIN_EMAIL,
                                             expected_display_name)
    self.assertEqual(actual_fleet.name, 'default')
    self.assertEqual(actual_fleet.config, [])
    self.assertEqual(actual_fleet.description, 'The default fleet organization')
    self.assertEqual(actual_fleet.display_name, expected_display_name)

  def test_create_default_fleet__repeated(self):
    """Recreating the default fleet object should raise CreateFleetError."""
    fleet_model.Fleet.default(loanertest.TECHNICAL_ADMIN_EMAIL, 'example')
    self.assertRaises(fleet_model.CreateFleetError,
                      fleet_model.Fleet.default,
                      loanertest.TECHNICAL_ADMIN_EMAIL, 'another example')


if __name__ == '__main__':
  loanertest.main()
