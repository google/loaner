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

"""Tests for backend.lib.datastore_yaml_import."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import datetime
import mock

from loaner.web_app import constants  # pylint: disable=unused-import
from loaner.web_app.backend.clients import directory  # pylint: disable=unused-import
from loaner.web_app.backend.lib import datastore_yaml
from loaner.web_app.backend.models import device_model
from loaner.web_app.backend.models import event_models
from loaner.web_app.backend.models import shelf_model
from loaner.web_app.backend.models import survey_models
from loaner.web_app.backend.models import template_model
from loaner.web_app.backend.models import user_model
from loaner.web_app.backend.testing import loanertest

SHELF_YAML = """
shelves:
  - location: 'TEST-LOCATION-1'
    capacity: 24
    friendly_name: 'TEST-1'
    responsible_for_audit: inventory
  - location: 'TEST-LOCATION-2'
    capacity: 24
    friendly_name: 'TEST-2'
    responsible_for_audit: inventory
"""
DEVICE_YAML = """
devices:
  - serial_number: '123456'
  - serial_number: '654321'
"""
CORE_EVENT_YAML = """
core_events:
  - name: device_assign
    description: Event run when a device is assigned
    enabled: True
    actions:
      - action_1
      - action_2
"""
SHELF_AUDIT_EVENT_YAML = """
shelf_audit_events:
  - enabled: True
    actions:
      - action_1
      - action_2
"""
CUSTOM_EVENT_YAML = """
custom_events:
  - name: stale_device
    description: Event to act on a stale device
    model: Device
    enabled: True
    actions:
      - stale_action_1
      - stale_action_2
    conditions:
      - name: last_update
        opsymbol: <
        value: 'TIME:-3d'
"""
REMINDER_EVENT_YAML = """
reminder_events:
  - level: 0
    description: Device due
    enabled: True
    actions:
      - due_action_1
      - due_action_2
    conditions:
      - name: due_date
        opsymbol: <=
        value: 'TIME:+1d'
"""
SURVEY_QUESTION_YAML = """
survey_questions:
  - question_type: ASSIGNMENT
    question_text: 'Do you like this machine you have, you borrower of things?'
    enabled: true
    rand_weight: 42
    answers:
      - text: 'Yes, I do.'
        more_info_enabled: true
        placeholder_text: 'Tell us about why you do, borrower of things.'
      - text: 'No, I do not.'
"""
TEMPLATE_YAML = """
templates:
  - name: loaner_due
    title: 'Your loaner is due on {{day_of_week}}'
    body: 'Hello, {{user_email}}. Your loaner with serial number {{serial}} is
          due on {{date}}. Return it by then if you ever want to see your
          pet turtle, {{turtle_name}}, again.'
"""
USER_YAML = """
users:
  - id: daredevil@{}
  - id: jessicajones@{}
""".format(loanertest.USER_DOMAIN, loanertest.USER_DOMAIN)
ALL_YAML = (
    SHELF_YAML + DEVICE_YAML + CORE_EVENT_YAML + SHELF_AUDIT_EVENT_YAML +
    CUSTOM_EVENT_YAML + REMINDER_EVENT_YAML + SURVEY_QUESTION_YAML +
    TEMPLATE_YAML + USER_YAML)


class ImportYamlTest(loanertest.TestCase):
  """Tests for the datastore YAML importer lib."""

  @mock.patch('__main__.directory.DirectoryApiClient', autospec=True)
  def test_yaml_import(self, mock_directoryclass):
    """Tests basic YAML importing."""
    mock_directoryclient = mock_directoryclass.return_value
    mock_directoryclient.get_chrome_device_by_serial.side_effect = [
        loanertest.TEST_DIR_DEVICE1, loanertest.TEST_DIR_DEVICE2
    ]
    mock_directoryclient.move_chrome_device_org_unit.side_effect = [
        loanertest.TEST_DIR_DEVICE_DEFAULT, loanertest.TEST_DIR_DEVICE2
    ]
    datastore_yaml.import_yaml(ALL_YAML, loanertest.USER_EMAIL)
    self.assertEqual(len(shelf_model.Shelf.query().fetch()), 2)
    self.assertEqual(len(device_model.Device.query().fetch()), 2)
    self.assertEqual(len(event_models.CoreEvent.query().fetch()), 1)
    self.assertEqual(len(event_models.ShelfAuditEvent.query().fetch()), 1)
    self.assertEqual(len(event_models.CustomEvent.query().fetch()), 1)
    self.assertEqual(len(event_models.ReminderEvent.query().fetch()), 1)
    self.assertEqual(len(survey_models.Question.query().fetch()), 1)
    self.assertEqual(len(template_model.Template.query().fetch()), 1)
    self.assertEqual(len(user_model.User.query().fetch()), 2)

  @mock.patch('__main__.directory.DirectoryApiClient', autospec=True)
  def test_yaml_import_with_randomized_shelves(self, mock_directoryclass):
    """Tests YAML importing with devices randomly assigned to shelves."""
    mock_directoryclient = mock_directoryclass.return_value
    mock_directoryclient.get_chrome_device_by_serial.side_effect = [
        loanertest.TEST_DIR_DEVICE1, loanertest.TEST_DIR_DEVICE2
    ]
    mock_directoryclient.move_chrome_device_org_unit.side_effect = [
        loanertest.TEST_DIR_DEVICE_DEFAULT, loanertest.TEST_DIR_DEVICE2
    ]
    datastore_yaml.import_yaml(
        SHELF_YAML + DEVICE_YAML, loanertest.USER_EMAIL,
        randomize_shelving=True)
    devices = device_model.Device.query().fetch()
    shelves = shelf_model.Shelf.query().fetch()
    self.assertEqual(len(devices), 2)
    self.assertEqual(len(shelves), 2)
    for device in devices:
      self.assertTrue(device.shelf in [shelf.key for shelf in shelves])

  @mock.patch('__main__.directory.DirectoryApiClient', autospec=True)
  @mock.patch('__main__.constants.BOOTSTRAP_ENABLED', True)
  def test_yaml_import_with_wipe(self, mock_directoryclass):
    """Tests YAML importing with a datastore wipe."""
    mock_directoryclient = mock_directoryclass.return_value
    mock_directoryclient.get_chrome_device_by_serial.return_value = (
        loanertest.TEST_DIR_DEVICE1)
    mock_directoryclient.move_chrome_device_org_unit.return_value = (
        loanertest.TEST_DIR_DEVICE_DEFAULT)
    test_device = device_model.Device.enroll(
        serial_number='0987654321', user_email=loanertest.USER_EMAIL)
    test_shelf = shelf_model.Shelf.enroll(
        user_email='test@{}'.format(loanertest.USER_DOMAIN),
        location='Somewhere',
        capacity=42,
        friendly_name='Nice shelf',
        responsible_for_audit='inventory')
    test_event = event_models.CoreEvent.create('test_event')
    test_event.description = 'A test event'
    test_event.enabled = True
    test_event.actions = ['some_action', 'another_action']
    test_event.put()

    datastore_yaml.import_yaml(ALL_YAML, loanertest.USER_EMAIL, wipe=True)

    # Datastore wiped, new devices/shelves from YAML.
    devices = device_model.Device.query().fetch()
    shelves = shelf_model.Shelf.query().fetch()
    core_events = event_models.CoreEvent.query().fetch()
    shelf_audit_events = event_models.ShelfAuditEvent.query().fetch()
    custom_events = event_models.CustomEvent.query().fetch()
    reminder_events = event_models.ReminderEvent.query().fetch()
    survey_questions = survey_models.Question.query().fetch()
    templates = template_model.Template.query().fetch()
    users = user_model.User.query().fetch()

    self.assertEqual(len(shelves), 2)
    self.assertEqual(len(devices), 2)
    self.assertEqual(len(core_events), 1)
    self.assertEqual(len(shelf_audit_events), 1)
    self.assertEqual(len(custom_events), 1)
    self.assertEqual(len(reminder_events), 1)
    self.assertEqual(len(survey_questions), 1)
    self.assertEqual(len(templates), 1)
    self.assertEqual(len(users), 2)

    self.assertTrue(test_device.serial_number not in
                    [device.serial_number for device in devices])
    self.assertTrue(
        test_shelf.location not in [shelf.location for shelf in shelves])
    self.assertTrue(
        test_event.name not in [event.name for event in core_events])
    self.assertTrue(isinstance(
        custom_events[0].conditions[0].value, datetime.timedelta))

  @mock.patch('__main__.constants.BOOTSTRAP_ENABLED', False)
  def test_datastore_wipe_without_enablement(self):
    """Tests that an exception is raised when datastore can't be wiped."""
    self.assertRaises(
        datastore_yaml.DatastoreWipeError,
        datastore_yaml.import_yaml,
        ALL_YAML,
        loanertest.USER_EMAIL,
        wipe=True)


if __name__ == '__main__':
  loanertest.main()
