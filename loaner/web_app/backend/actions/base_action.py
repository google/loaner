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

"""Base action module."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import inspect

_NO_ACTION_NAME_MSG = (
    'Action class %s has no ACTION_NAME attribute or it is not a string.')
_BAD_ACTION_TYPE_MSG = (
    'Action class %s has an ACTION_TYPE of %s, but it should be either '
    '"sync" or "async".')
_NO_FRIENDLY_NAME_MSG = (
    'Action class %s has no FRIENDLY_NAME attribute or it is not a string.')
_NO_RUN_METHOD_MSG = 'Action class %s has no method named run.'
_BAD_SYNC_RUN_MSG = (
    'Action class %s has a run method that does not return the model. All sync '
    'Actions should return the model passed to it.')
_BAD_ASYNC_RUN_MSG = (
    'Action class %s has a run method that returns an object. All async '
    'Actions should return None (i.e., they should not have a return).')


class Error(Exception):
  """General Error class for this module."""


class MissingModelError(Error):
  """Base error raised when a BaseAction subclass doesn't receive a model."""


class BadModelError(Error):
  """Base error raised when a BaseAction subclass receives a bad model."""


class RedundantModelError(Error):
  """Error raised when a baseaction subclass receives both device and shelf."""


class MissingDeviceError(MissingModelError):
  """Error raised when a BaseAction subclass doesn't receive a device model."""


class MissingShelfError(MissingModelError):
  """Error raised when a BaseAction subclass doesn't receive a shelf model."""


class BadDeviceError(BadModelError):
  """Error raised when a BaseAction subclass receives a bad device model."""


class BadShelfError(BadModelError):
  """Error raised when a BaseAction subclass receives a bad shelf model."""


class RunError(Error):
  """Error raised when a BaseAction subclass run method fails."""


class ActionType(object):
  SYNC = 'sync'
  ASYNC = 'async'


class BaseAction(object):
  """A superclass for Actions.

  When creating new Actions, sublcass this class in a new class named Action.*
  and provide a run method, an ACTION_NAME string, and a FRIENDLY_NAME string.

  For example:

    class MySyncAction(base_action.BaseAction):

      ACTION_NAME = 'my_sync_action'
      FRIENDLY_NAME = 'My Sync Action'
      ACTION_TYPE = ActionType.SYNC

      def run(self, shelf=None):
        if not shelf:
          raise Exception('Need a shelf.')
        shelf.attribute = 42
        return shelf

    class MyAsyncAction(base_action.BaseAction):

      ACTION_NAME = 'my_async_action'
      FRIENDLY_NAME = 'My Async Action'
      ACTION_TYPE = ActionType.ASYNC

      def run(self, device=None):
        if not device:
          raise Exception('Need a device.')
        device.attribute = 'ZZ9 Plural Z Alpha'
        device.put()

  Models of the "sync" Action type must have a run method that returns
  the (possibly altered) model; async Actions must not return. The lack of an
  ACTION_TYPE defaults to async for backwards compatibility.

  These subclasses can have arbitrary names, as can the modules containing them.
  """

  def __init__(self):
    """Validates required attributes for Action subclasses."""
    if not isinstance(getattr(self, 'ACTION_NAME', None), basestring):
      raise AttributeError(_NO_ACTION_NAME_MSG % self.__class__.__name__)
    if not isinstance(getattr(self, 'FRIENDLY_NAME', None), basestring):
      raise AttributeError(_NO_FRIENDLY_NAME_MSG % self.__class__.__name__)
    try:
      if not inspect.ismethod(super(BaseAction, self).__getattribute__('run')):
        raise AttributeError()
    except AttributeError:
      raise AttributeError(_NO_RUN_METHOD_MSG % self.__class__.__name__)
    self.action_type = getattr(self, 'ACTION_TYPE', ActionType.ASYNC)
    if self.action_type not in (ActionType.SYNC, ActionType.ASYNC):
      raise AttributeError(
          _BAD_ACTION_TYPE_MSG %
          (self.__class__.__name__, str(self.action_type)))

  def __getattribute__(self, attr):
    if attr == 'run':
      return super(BaseAction, self).__getattribute__(
          '_validate_and_execute_run')
    return super(BaseAction, self).__getattribute__(attr)

  def _validate_and_execute_run(self, **action_kwargs):
    """Executes a subclass's run method and returns result if sync."""
    actual_run = super(BaseAction, self).__getattribute__('run')
    run_return = actual_run(**action_kwargs)  # pylint: disable=no-member
    if self.action_type == ActionType.SYNC:
      if run_return.__class__.__name__ not in ('Device', 'Shelf'):
        raise TypeError(_BAD_SYNC_RUN_MSG % self.__class__.__name__)
      return run_return
    else:
      if run_return is not None:
        raise TypeError(_BAD_ASYNC_RUN_MSG % self.__class__.__name__)
