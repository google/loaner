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

"""Base model class for the loaner project."""

import datetime
import inspect
import pickle

from protorpc import messages

from google.appengine.api import taskqueue
from google.appengine.ext import ndb

from loaner.web_app.backend.lib import utils


class BaseModel(ndb.Model):  # pylint: disable=too-few-public-methods
  """Base model class for the loaner project."""

  def stream_to_bq(self, user, summary, timestamp=None):
    """Creates a task to stream an update to BigQuery.

    Args:
      user: string user email of the acting user.
      summary: string summary of the action being performed.
      timestamp: datetime, if not provided current time will be used.
    """
    if not timestamp:
      timestamp = datetime.datetime.utcnow()
    calling_function = inspect.stack()[1][3]
    task_params = {
        'model_instance': self,
        'timestamp': timestamp,
        'actor': user,
        'method': calling_function,
        'summary': summary,
    }
    taskqueue.add(
        queue_name='stream-bq',
        payload=pickle.dumps(task_params),
        target='default')

  def to_json_dict(self):
    """Converts entity to a JSON-friendly dict.

    Returns:
      The entity as a dictionary with only JSON-friendly values.
    """
    return _sanitize_dict(self.to_dict())


def _sanitize_dict(entity_dict):
  """Sanitize select values of an entity-derived dictionary."""
  for key, value in entity_dict.iteritems():
    if isinstance(value, dict):
      entity_dict[key] = _sanitize_dict(value)
    elif isinstance(value, list):
      entity_dict[key] = [_serialize(s_value) for s_value in value]
    else:
      entity_dict[key] = _serialize(value)

  return entity_dict


def _serialize(value):
  """Serializes a complex ndb type.

  Args:
    value: A ndb type to be serialized.

  Returns:
    Value serialized to simple data type such as integer or string.
  """
  if isinstance(value, datetime.datetime):
    return utils.datetime_to_unix(value)
  elif isinstance(value, (ndb.Key, ndb.GeoPt, messages.Enum)):
    return str(value)
  else:
    return value
