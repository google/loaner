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

"""Grab n Go environment specific constants.

Each one of the constants defined below is an environment specific constant.
A unique value will be required for every unique Google Cloud Project. These
will be stored in Google Cloud Storage in the bucket configured in the
loaner/deployments/config.yaml file for this project.

When adding a configurable project level constant the following procedure must
be used:
  1. Add the name of the constant below, the value must be the name that is used
     for the flag.
  2. Create the flag with a default, no flag should be marked as required using
     the `flags` package.
  3. Add the name of the constant to the loaner/web_app/constants.py file.
  4. (Optional) add a `Parser` object for the name in the `_PARSERS` dictionary.
     The `parse` method on the `Parser` object will be used to validate the
     current value of the constant, whether the default or a user provided
     value. If the value is invalid, a ValueError is raised and the flag message
     is used to prompt the user, only ever accepting a value that passes through
     the `parse` method. If the manager is run in scripted mode an invalid value
     for any constant defined below will cause an error and the script will
     exit.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys

from absl import flags

from loaner.deployments.lib import utils

FLAGS = flags.FLAGS

# Constant Names #
# These are the configurable constants, the name of the constant matches the
# name in the constants.py file and the value is used as the name of the flag
# and used as the key for getting the respective `utils.Parser` object in the
# `_PARSERS` dictionary below.
APP_DOMAINS = 'app_domains'
CHROME_CLIENT_ID = 'chrome_client_id'
WEB_CLIENT_ID = 'web_client_id'
ADMIN_EMAIL = 'admin_email'
SEND_EMAIL_AS = 'send_email_as'
SUPERADMINS_GROUP = 'superadmins_group'
CUSTOMER_ID = 'customer_id'

# Required to be provided either by flag or by prompt.
flags.DEFINE_list(
    APP_DOMAINS, [],
    'A comma separated list of second-level domains that will be authorized to '
    'access the application. Only add domain names that you want to have access'
    ' to the web application. Domains should be in the following format: '
    "'example.com'"
)
flags.DEFINE_string(
    CHROME_CLIENT_ID, '',
    'The Chrome App OAuth2 Client ID.\n'
    'In order for the Chrome companion application to be able to make API calls'
    ' to the management backend an OAuth2 Client ID must be provided. This can '
    'be created in the Google Cloud Console at: '
    "https://console.cloud.google.com/apis/credentials. The 'Application Type' "
    "for this credential is 'Chrome App'.\n"
    'Further instructions can be found here: https://support.google.com'
    '/cloud/answer/6158849?hl=en#installedapplications&chrome'
)
flags.DEFINE_string(
    WEB_CLIENT_ID, '',
    'The Web App OAuth2 Client ID.\n'
    'In order for the Web application to be able to make API calls to the '
    'management backend an OAuth2 Client ID must be provided. This can '
    'be created in the Google Cloud Console at: '
    "https://console.cloud.google.com/apis/credentials. The 'Application Type' "
    "for this credential is 'Web Application'.\n"
    'Further instructions can be found here: https://support.google.com'
    '/cloud/answer/6158849?hl=en'
)
flags.DEFINE_string(
    ADMIN_EMAIL, '',
    'The email address to use to access the Google Admin SDK Directory API.\n'
    'If this address does not exist we will attempt to create it with a strong '
    'password, which we will provide you. In order to create this account '
    'programmatically you will need to be a Super Admin in the G Suite domain '
    'this account is being created in.\nTo create this manually see the '
    'setup_guide in the Grab n Go documentation: '
    'https://github.com/google/loaner/blob/master/docs/setup_guide.md'
)
flags.DEFINE_string(
    SEND_EMAIL_AS, '',
    'The email address from which application related emails will come from. '
    'Often a noreply address is used, e.g. noreply@example.com'
)
flags.DEFINE_string(
    SUPERADMINS_GROUP, '',
    'The name of the group for whom to grant super admin privileges to. '
    'This should include anyone you want to be able to administer Grab n Go '
    'from the web application. This gives access to all in app data.'
)

# Not required to be provided either by flag or by prompt.
flags.DEFINE_string(
    CUSTOMER_ID, 'my_customer',
    'The G Suite customer ID.\nIf you are an administrator of the organization '
    'this application is running in leave the default. If you are a reseller '
    'you can get the customer ID by making a get user request: '
    'https://developers.google.com/admin-sdk/directory/v1/guides/manage-users'
    '.html#get_user'
)

# Dictionary where the flag name is the key and the value is a parser, an object
# that has `parse` as a public instance method. A parser is not required,
# without one any value will be accepted.
_PARSERS = {
    APP_DOMAINS: utils.ListParser(allow_empty_list=False),
    CHROME_CLIENT_ID: utils.ClientIDParser(),
    WEB_CLIENT_ID: utils.ClientIDParser(),
    ADMIN_EMAIL: utils.EmailParser(),
    SEND_EMAIL_AS: utils.EmailParser(),
    SUPERADMINS_GROUP: utils.StringParser(allow_empty_string=False),
    CUSTOMER_ID: utils.StringParser(allow_empty_string=False),
}


def get_constants_from_flags(module=__name__):
  """Returns a dictionary of all constants from flags.

  This should only be used when skipping user validation (e.g. scripting) since
  it does not validate the provided values with the custom parsers until the
  value is requested. If the flag provided does not meet the `Parser`
  requirements an error will be raised when attempting to retrieve the value.

  Args:
    module: str, the name of the module to get the constants from.

  Returns:
    A dictionary of all constants with the flag value as the constant value.
        The key for each constant is the name of the constant.

  Raises:
    ValueError: when any of the flag values does not meet the parsing
        requirements.
  """
  def _from_flag(name):
    """Gets the value of a flag given the name.

    If flags have not been parsed, the default value will be used.

    Args:
      name: str, the name of the flag.

    Returns:
      The value of the flag.
    """
    if FLAGS.is_parsed():
      return getattr(FLAGS, name)
    return FLAGS[name].default
  return _get_all_constants(module=module, func=_from_flag)


def get_default_constants(module=__name__):
  """Returns a dictionary of all constants with the default flag value.

  This is used to initialize project level constants for a new project from
  user prompts.

  Args:
    module: str, the name of the module to get the constants from.

  Returns:
    A dictionary of all constants with the default flag value as the constant
        value. The key for each constant is the name of the constant.
  """
  return _get_all_constants(module=module, func=None)


def _get_all_constants(module=__name__, func=None):
  """Returns a dictionary of all constants.

  This function will return all of the flags configured above as `Constant`
  objects. By default, the default value of the flag will be used.

  Args:
    module: str, the name of the module to get the constants from.
    func: Callable, a function that returns the value of each constant given the
        name of the flag.

  Returns:
    A dictionary of all key flags in this module represented as Constants,
        keyed by the name of the constant.
  """
  constants = {}

  for flag in FLAGS.get_key_flags_for_module(sys.modules[module]):
    value = FLAGS[flag.name].default
    if func:
      value = func(flag.name)
    constants[flag.name] = Constant(
        flag.name, flag.help, value, _PARSERS.get(flag.name))
  return constants


class Constant(object):
  """Grab n Go project level constant.

  Attributes:
    name: str, the unique key to reference this constant by (this is identical
        to the name of the flag above).
    message: str, the message shown to the user when they are being prompted
        to provide the value of this constant (this is identical to the help
        message for the flag).
    valid: bool, whether or not the current value is valid.
    value: Any, the value of this constant.
  """

  def __init__(self, name, message, default, parser=None):
    """Initializes the constant.

    Args:
      name: str, the unique key to reference this constant by (this should be
          identical to the name of the flag above).
      message: str, the message shown to the user when they are being prompted
          to provide the value of this constant (this is identical to the help
          message for the flag).
      default: Any, the default value of this constant.
      parser: Callable, an object to validate and parse the provided input.
          A parser must meet the following requirements:
            1) The object must have a parse() method that accepts a single
               string as input and returns the parsed output.
            2) Any error that occurs during parse() should raise a ValueError to
               indicate bad user input with a helpful error message.
          An example can be found in the utils module in this package.
    """
    self._name = name
    self._message = message
    self._value = default
    self._parser = parser

  def __str__(self):
    return '{}: {}'.format(self.name, self._value)

  def __repr__(self):
    return '<{0}({1!r}, {2!r}, {3!r}, {4!r})>'.format(
        self.__class__.__name__, self.name, self.message, self._value,
        self._parser)

  def __eq__(self, other):
    return self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not self.__eq__(other)

  @property
  def name(self):
    """Getter for the name."""
    return self._name

  @property
  def message(self):
    """Getter for the user message."""
    return self._message

  @property
  def value(self):
    """Getter for the current value."""
    return self._value

  @value.setter
  def value(self, value):
    """Setter for the current value."""
    self._value = value if self._parser is None else self._parser.parse(value)

  @property
  def valid(self):
    """Getter for whether or not the current value is valid."""
    if self._parser is None:
      return True

    try:
      self._parser.parse(self.value)
    except ValueError:
      return False
    return True

  def prompt(self):
    """Prompts the user for a new value."""
    self.value = utils.prompt(
        self.message, default=self.value, parser=self._parser)
