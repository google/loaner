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

"""Module for exporting a backup of Datstore to GCP bucket in a cron job."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import datetime
import httplib
import json
import logging
import webapp2

from google.appengine.api import app_identity
from google.appengine.api import urlfetch

from loaner.web_app import constants
from loaner.web_app.backend.models import config_model

_DATASTORE_API_URL = 'https://datastore.googleapis.com/v1/projects/%s:export'
_DESTINATION_URL = 'gs://{}/{}_datastore_backup'


class DatastoreExport(webapp2.RequestHandler):
  """Handler for exporting Datastore to GCP bucket."""

  def get(self):
    bucket_name = config_model.Config.get('gcp_cloud_storage_bucket')
    if config_model.Config.get('enable_backups') and bucket_name:
      access_token, _ = app_identity.get_access_token(
          'https://www.googleapis.com/auth/datastore')

      # We strip the first 2 characters because os.environ.get returns the
      # application id with a partitiona separated by tilde, eg `s~`, which is
      # not needed here.
      app_id = constants.APPLICATION_ID.split('~')[1]

      request = {
          'project_id': app_id,
          'output_url_prefix': _format_full_path(bucket_name),
      }
      headers = {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ' + access_token
      }

      logging.info(
          'Attempting to export cloud datastore to bucket %r.', bucket_name)
      try:
        result = urlfetch.fetch(
            url=_DATASTORE_API_URL % app_id,
            payload=json.dumps(request),
            method=urlfetch.POST,
            deadline=60,
            headers=headers)
        if result.status_code == httplib.OK:
          logging.info('Cloud Datastore export completed.')
          logging.info(result.content)
        elif result.status_code >= 500:
          logging.error(result.content)
        else:
          logging.warning(result.content)
        self.response.status_int = result.status_code
      except urlfetch.Error:
        logging.error('Failed to initiate datastore export.')
        self.response.status_int = httplib.INTERNAL_SERVER_ERROR
    else:
      logging.info('Backups are not enabled, skipping.')


def _format_full_path(bucket_name):
  """Formats the full output URL with proper datetime stamp.

  Args:
    bucket_name: str, the Google Cloud Storage bucket name.

  Returns:
    A formatted string URL.
  """
  if bucket_name.startswith('gs://'):
    bucket_name = bucket_name[5:]

  return _DESTINATION_URL.format(
      bucket_name, datetime.datetime.now().strftime('%Y_%m_%d-%H%M%S'))
