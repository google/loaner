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

"""Bootstrap messages for Bootstrap API."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from protorpc import message_types
from protorpc import messages


class BootstrapTaskKwarg(messages.Message):
  """Bootstrap Task Keyword Arg ProtoRPC message.

  Attributes:
    name: str, The name of the task.
    value: str, The value of the task.
  """
  name = messages.StringField(1, required=True)
  value = messages.StringField(2, required=True)


class BootstrapTask(messages.Message):
  """Bootstrap Task ProtoRPC message.

  Attributes:
    name: str, The name of the task.
    kwargs: BootstrapTaskKwarg, Name and value kwarg.
    description: str, Friendly description of the bootstrap task function.
    success: bool, Indicate whether the task is successful.
    timestamp: datetime, The time the task was completed.
    details: str, Contains the details of the task.
  """
  name = messages.StringField(1, required=True)
  kwargs = messages.MessageField(BootstrapTaskKwarg, 2, repeated=True)
  description = messages.StringField(3)
  success = messages.BooleanField(4)
  timestamp = message_types.DateTimeField(5)
  details = messages.StringField(6)


class RunBootstrapRequest(messages.Message):
  """Bootstrap run request ProtoRPC message.

  Attributes:
    requested_tasks: BootstrapTask, A list of the requested tasks.
  """
  requested_tasks = messages.MessageField(BootstrapTask, 1, repeated=True)


class BootstrapStatusResponse(messages.Message):
  """Bootstrap status response ProtoRPC message.

  Attributes:
    enabled: bool, Indicates if the bootstrap is enabled.
    started: bool, Indicated if the bootstrap has been started.
    completed: bool, Indicated if the bootstrap is completed.
    tasks: BootstrapTask, A list of all of the tasks to be displayed.
  """
  enabled = messages.BooleanField(1)
  started = messages.BooleanField(2)
  completed = messages.BooleanField(3)
  tasks = messages.MessageField(BootstrapTask, 4, repeated=True)
