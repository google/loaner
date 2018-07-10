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

"""The entry point for the Bootstrap methods."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from protorpc import message_types

from loaner.web_app.backend.api import auth
from loaner.web_app.backend.api import permissions
from loaner.web_app.backend.api import root_api
from loaner.web_app.backend.api.messages import bootstrap_messages
from loaner.web_app.backend.lib import bootstrap


@root_api.ROOT_API.api_class(resource_name='bootstrap', path='bootstrap')
class BootstrapApi(root_api.Service):
  """Bootstrap API service class."""

  @auth.method(
      bootstrap_messages.RunBootstrapRequest,
      bootstrap_messages.BootstrapStatusResponse,
      name='run',
      path='run',
      http_method='POST',
      permission=permissions.Permissions.BOOTSTRAP)
  def run(self, request):
    """Runs request for the Bootstrap API."""
    self.check_xsrf_token(self.request_state)
    requested_tasks = {}
    for task in request.requested_tasks:
      requested_tasks[task.name] = {}
      for kwarg in task.kwargs:
        requested_tasks[task.name][kwarg.name] = kwarg.value

    run_status_dict = bootstrap.run_bootstrap(requested_tasks)

    response_message = bootstrap_messages.BootstrapStatusResponse()
    for name, description in run_status_dict.iteritems():
      response_message.tasks.append(
          bootstrap_messages.BootstrapTask(name=name, description=description))
    return response_message

  @auth.method(
      message_types.VoidMessage,
      bootstrap_messages.BootstrapStatusResponse,
      name='get_status',
      path='get_status',
      http_method='GET',
      permission=permissions.Permissions.BOOTSTRAP)
  def get_status(self, request):
    """Gets general bootstrap status, and task status if not yet completed."""
    self.check_xsrf_token(self.request_state)
    response_message = bootstrap_messages.BootstrapStatusResponse()
    response_message.enabled = bootstrap.is_bootstrap_enabled()
    response_message.started = bootstrap.is_bootstrap_started()
    response_message.completed = bootstrap.is_bootstrap_completed()
    for name, status in bootstrap.get_bootstrap_task_status().iteritems():
      response_message.tasks.append(
          bootstrap_messages.BootstrapTask(
              name=name,
              description=status.get('description'),
              success=status.get('success'),
              timestamp=status.get('timestamp'),
              details=status.get('details')))
    return response_message
