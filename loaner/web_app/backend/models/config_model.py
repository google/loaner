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

"""A model representing configuration config."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from google.appengine.api import memcache
from google.appengine.ext import ndb

from loaner.web_app.backend.lib import utils


_CONFIG_NOT_FOUND_MSG = 'No such name "%s" exists in default configurations.'


class Config(ndb.Model):
  """Datastore model representing a config name.

  The default values are stored in the config_defaults.yaml file. A config name
  has an option to store a value of type string, integer, boolean, or list as
  its value. The same config name can not have a value of multiple types.

  Attributes:
    string_value: str, value for a given config name.
    integer_value: int, value for a given config name.
    bool_value: bool, value for a given config name.
    list_value: list, value for a given config name.
  """
  string_value = ndb.StringProperty()
  integer_value = ndb.IntegerProperty()
  bool_value = ndb.BooleanProperty()
  list_value = ndb.StringProperty(repeated=True)

  @classmethod
  def get(cls, name):
    """Checks memcache for name, if not available, check datastore.

    Args:
      name: str, name of config name.

    Returns:
      The config value from memcache, datastore, or config file.

    Raises:
      KeyError: An error occurred when name does not exist.
    """
    config_defaults = utils.load_config_from_yaml()
    memcache_config = memcache.get(name)
    cached_config = None
    if memcache_config:
      return memcache_config
    else:
      stored_config = cls.get_by_id(name, use_memcache=False)
      if stored_config:
        if stored_config.string_value:
          cached_config = stored_config.string_value
        elif stored_config.integer_value:
          cached_config = stored_config.integer_value
        elif stored_config.bool_value is not None:
          cached_config = stored_config.bool_value
        elif stored_config.list_value:
          cached_config = stored_config.list_value
      # Conversion from use_asset_tags to device_identifier_mode.
      if name == 'device_identifier_mode' and not cached_config:
        if cls.get('use_asset_tags'):
          cached_config = DeviceIdentifierMode.BOTH_REQUIRED
          cls.set(name, cached_config)
          memcache.set(name, cached_config)
      if cached_config is not None:
        memcache.set(name, cached_config)
        return cached_config
      elif name in config_defaults:
        return config_defaults[name]

    raise KeyError(_CONFIG_NOT_FOUND_MSG, name)

  @classmethod
  def set(cls, name, value, validate=True):
    """Stores values for a config name in memcache and datastore.

    Args:
      name: str, name of the config setting.
      value: str, int, bool, list value to set or change config setting.
      validate: bool, checks keys against config_defaults if enabled.
    Raises:
      KeyError: Error raised when name does not exist in config.py file.
    """
    if validate:
      config_defaults = utils.load_config_from_yaml()
      if name not in config_defaults:
        raise KeyError(_CONFIG_NOT_FOUND_MSG % name)

    if isinstance(value, basestring):
      stored_config = cls.get_or_insert(name)
      stored_config.string_value = value
      stored_config.put()
    if isinstance(value, bool) and isinstance(value, int):
      stored_config = cls.get_or_insert(name)
      stored_config.bool_value = value
      stored_config.put()
    if isinstance(value, int) and not isinstance(value, bool):
      stored_config = cls.get_or_insert(name)
      stored_config.integer_value = value
      stored_config.put()
    if isinstance(value, list):
      stored_config = cls.get_or_insert(name)
      stored_config.list_value = value
      stored_config.put()

    memcache.set(name, value)


class DeviceIdentifierMode(object):
  """Constants defining supported means of identifying devices."""
  ASSET_TAG = 'asset_tag'
  SERIAL_NUMBER = 'serial_number'
  BOTH_REQUIRED = 'both_required'
