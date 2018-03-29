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

"""Module to enforce authentication on endpoints.method.

Usage:
-----
 # configuration of an endpoints method with enforced user auth check only.
@loaner_endpoints.authed_method(
    chrome_message.ChromeRequest,
    chrome_message.ChromeResponse,
    name='heartbeat',
    path='heartbeat',
    http_method='GET',
    user_auth_only=True)
def do_something(self, request):
    ...

The above method will execute if the current user is authenticated properly.

 # configuration of an endpoints method with enforced permission.
@loaner_endpoints.authed_method(
    chrome_message.ChromeRequest,
    chrome_message.ChromeResponse,
    name='heartbeat',
    path='heartbeat',
    http_method='GET',
    permission='view')
def do_something(self, request):
    ...

The above method will only execute if the current user's role has the permission
"view".

Note:
-----
Please see permission module for more information on how the check_auth()
decorator works.
"""

import endpoints

from loaner.web_app.backend.auth import permissions


class Error(Exception):
  """Default error class for this module."""


class AuthCheckNotPresent(Error):
  """Raised when auth_method was called without auth check."""


def authed_method(*args, **kwargs):
  """Configures an endpoint method and enforces permissions."""

  def auth_method_decorator(auth_function):
    """Decorator for auth_method."""
    kwarg_auth = None
    kwarg_permission = None
    for key in kwargs:
      if key is 'permission':
        kwarg_permission = kwargs.pop('permission')
        auth_function = permissions.check_auth(
            permission=kwarg_permission)(auth_function)
        break
      elif key is 'user_auth_only':
        kwarg_auth = kwargs.pop('user_auth_only')
        auth_function = permissions.check_auth(
            user_auth_only=kwarg_auth)(auth_function)
        break
    if not kwarg_auth and not kwarg_permission:
      raise AuthCheckNotPresent(
          'No permission or user_auth_only was passed. Authentication on this '
          'method cannot run.')
    # Always apply the standard `endpoints.method` decorator.
    return endpoints.method(*args, **kwargs)(auth_function)

  return auth_method_decorator
