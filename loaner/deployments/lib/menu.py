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

"""Menu contains menu options for the Grab n Go Manager."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


class Option(object):
  """Option represents a menu option in the Grab n Go Manager.

  Attributes:
    name: str, the name of the option. This will be what the user types into the
        menu to select this option.
    description: str, a short description of what this option is and what it
        enables the user to do.
    callback: Optional[Callable], a callback method to execute when this option
        is selected. This callback must return an updated instance of the
        calling object.
  """

  def __init__(self, name, description, callback=None):
    """Initializes a new option.

    Args:
      name: str, the name of the option. This will be what the user types into
          the menu to select this option.
      description: str, a short description of what this option is and what it
          enables the user to do.
      callback: Optional[Callable], a callback method to execute when this
          option is selected. This callback must return an updated instance of
          the calling object.
    """
    self._name = name
    self._description = description
    self._callback = callback

  def __repr__(self):
    return '<{0}({1}, {2}, {3})>'.format(
        self.__class__.__name__, self.name, self.description, self.callback)

  def __eq__(self, other):
    return self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not self.__eq__(other)

  @property
  def name(self):
    return self._name

  @property
  def description(self):
    return self._description

  @property
  def callback(self):
    return self._callback
