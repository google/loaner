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

from absl.testing import parameterized
import mock

from protorpc import message_types

from google.appengine.api import search

import endpoints

from loaner.web_app.backend.api import root_api
from loaner.web_app.backend.api.messages import shelf_messages
from loaner.web_app.backend.lib import xsrf
from loaner.web_app.backend.models import shelf_model
from loaner.web_app.backend.testing import loanertest


@root_api.ROOT_API.api_class(resource_name='fake', path='fake')
class FakeApi(root_api.Service):

  @endpoints.method(message_types.VoidMessage, http_method='POST')
  def do_something(self, request):
    self.check_xsrf_token(self.request_state)
    return message_types.VoidMessage()


class RootServiceTest(loanertest.EndpointsTestCase, parameterized.TestCase):

  def setUp(self):
    super(RootServiceTest, self).setUp()
    self.service = FakeApi()
    self.root_api_service = root_api.Service()

  def test_check_xsrf_token(self):
    request = message_types.VoidMessage()

    with mock.patch.object(xsrf, 'validate_request') as mock_validate_request:
      mock_validate_request.return_value = True
      self.service.do_something(request)
      assert mock_validate_request.called

      mock_validate_request.return_value = False
      self.assertRaisesRegexp(
          endpoints.ForbiddenException, 'XSRF',
          self.service.do_something, request)

  def test_to_dict(self):
    message = shelf_messages.Shelf(
        location='NY', capacity=50, friendly_name='The_Big_Apple',
        audit_requested=False, responsible_for_audit='daredevils',
        last_audit_by=loanertest.USER_EMAIL, enabled=True)
    expected_dict = {
        'location': 'NY', 'capacity': 50, 'friendly_name': 'The_Big_Apple',
        'audit_requested': False, 'responsible_for_audit': 'daredevils',
        'last_audit_by': loanertest.USER_EMAIL, 'enabled': True}
    filters = self.root_api_service.to_dict(message, shelf_model.Shelf)
    self.assertEqual(filters, expected_dict)

  @parameterized.parameters(
      (shelf_messages.Shelf(location='NY', capacity=50),
       'location:NY capacity:50',),
      (shelf_messages.Shelf(location='NY', capacity=50, enabled=True),
       'location:NY capacity:50 enabled:True',))
  def test_to_qery(self, message, expected_query):
    query = self.root_api_service.to_query(message, shelf_model.Shelf)
    #  The query is split because ndb properties are unordered when called by
    #  model_class._properties. This test would be flaky otherwise.
    self.assertCountEqual(query.split(' '), expected_query.split(' '))

  @mock.patch.object(root_api, 'logging', autospec=True)
  def test_document_to_message(self, mock_logging):
    test_search_document = search.ScoredDocument(
        doc_id='test_doc_id',
        fields=[
            search.NumberField(name='capacity', value=20.0),
            search.TextField(name='location', value='US MTV'),
            search.AtomField(name='location', value='US-MTV'),
            search.AtomField(name='enabled', value='True'),
            search.GeoField(
                name='lat_long', value=search.GeoPoint(52.37, 4.88)),
            search.TextField(name='not_present', value='MTV')])
    expected_message = shelf_messages.Shelf(
        location='US-MTV', capacity=20, latitude=52.37, longitude=4.88)

    response_message = self.root_api_service.document_to_message(
        shelf_messages.Shelf(), test_search_document)
    self.assertEqual(response_message.location, expected_message.location)
    self.assertEqual(response_message.capacity, expected_message.capacity)
    self.assertEqual(response_message.latitude, expected_message.latitude)
    self.assertEqual(response_message.longitude, expected_message.longitude)
    self.assertTrue(response_message.enabled)
    assert mock_logging.error.call_count == 1

  def test_get_search_cursor(self):
    expected_cursor = 'False:ODUxODBhNTgyYTQ2ZmI0MDU'
    test_search_result = search.SearchResults(
        results=[search.ScoredDocument(
            doc_id='test_doc_id',
            fields=[search.NumberField(name=u'capacity', value=10.0)])],
        number_found=3,
        cursor=search.Cursor(web_safe_string=expected_cursor))
    actual_cursor, actual_cursor_bool = (
        self.root_api_service.get_search_cursor(test_search_result))
    self.assertEqual(expected_cursor, actual_cursor)
    self.assertTrue(actual_cursor_bool)

  def test_get_search_cursor_search_result_none(self):
    actual_cursor, actual_cursor_bool = (
        self.root_api_service.get_search_cursor(None))
    self.assertIsNone(actual_cursor)
    self.assertFalse(actual_cursor_bool)

  def test_get_ndb_key_not_found(self):
    """Test the get of an ndb.Key, raises endpoints.BadRequestException."""
    with self.assertRaisesRegexp(
        endpoints.BadRequestException,
        root_api._CORRUPT_KEY_MSG):
      root_api.get_ndb_key('corruptKey')

  def test_get_datastore_cursor_not_found(self):
    """Test the get of a datastore.Cursor, raises endpoints.BadRequestException.
    """
    with self.assertRaisesRegexp(
        endpoints.BadRequestException,
        root_api._MALFORMED_PAGE_TOKEN_MSG):
      self.root_api_service.get_datastore_cursor('malformedPageToken')


if __name__ == '__main__':
  loanertest.main()
