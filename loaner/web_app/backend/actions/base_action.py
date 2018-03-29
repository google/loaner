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

import inspect

_NO_ACTION_NAME_MSG = (
    'Action class %s has no ACTION_NAME attribute or it is not a string.')
_NO_FRIENDLY_NAME_MSG = (
    'Action class %s has no FRIENDLY_NAME attribute or it is not a string.')
_NO_RUN_METHOD_MSG = 'Action class %s has no method named run.'


class BaseAction(object):
  """A superclass for Actions.

  When creating new Actions, sublcass this class in a new class named Action.*
  and provide a run method, an ACTION_NAME string, and a FRIENDLY_NAME string.

  For example:

    class MyAction(base_action.BaseAction):

      ACTION_NAME = 'my_action'
      FRIENDLY_NAME = 'My Action'

      def run(self):
        return 'foo'

  These subclasses can have arbitrary names, as can the modules containing them.
  """

  def __init__(self):
    """Validates required attributes for Action subclasses."""
    if not isinstance(getattr(self, 'ACTION_NAME', None), basestring):
      raise AttributeError(_NO_ACTION_NAME_MSG % self.__class__.__name__)
    if not isinstance(getattr(self, 'FRIENDLY_NAME', None), basestring):
      raise AttributeError(_NO_FRIENDLY_NAME_MSG % self.__class__.__name__)
    if not inspect.ismethod(getattr(self, 'run', None)):
      raise AttributeError(_NO_RUN_METHOD_MSG % self.__class__.__name__)
