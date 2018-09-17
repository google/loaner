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

"""This library provides a random password generator."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import random

from absl import flags
from absl import logging

_MIN = 8
_MAX = 100

FLAGS = flags.FLAGS

flags.DEFINE_integer(
    'password_length', _MAX,
    'The length of the password to be generated for the Grab n Go Role Account.'
    '\nNOTE: The length must be between 8 and 100 and must be compliant with '
    'the G Suite Admin password settings.\nThe Security Settings can be found '
    'in the Google Admin console: admin.google.com'
)

flags.register_validator(
    'password_length', lambda length: length >= _MIN and length <= _MAX,
    'Password length must be between {} and {} characters.'.format(_MIN, _MAX),
)


def generate(length):
  """Generates a new password of a given length.

  Args:
    length: int, the length of the password to generate.

  Returns:
    A random password of type string with the given length.

  Raises:
    ValueError: if the length provided is invalid.
  """
  if length < _MIN or length > _MAX:
    raise ValueError(
        'password length must be between {!r} and {!r} characters length '
        'provided was: {!r}'.format(_MIN, _MAX, length))

  logging.debug('Generating a password with length: %r.', length)

  chars = (
      'abcdefghijklmnopqrstuvwxyz'
      'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
      '0123456789'
      '!$%^&*()-_=+@:;~#,.<>? '
  )
  password = ''
  rand = random.SystemRandom()
  while len(password) < length:
    password += rand.choice(chars)
  return password
