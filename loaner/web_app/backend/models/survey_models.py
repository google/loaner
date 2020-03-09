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

"""Model representing a single-question survey and its answers."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import collections
import random

from protorpc import messages

from google.appengine.ext import ndb
from google.appengine.ext.ndb import msgprop

from loaner.web_app import constants
from loaner.web_app.backend.models import base_model
from loaner.web_app.backend.models import config_model

_MORE_INFO_MSG = (
    'If more_info_enabled or placeholder_text are provided then both are '
    'required.')
_NO_KEY_ERROR_MSG = 'The Answer Key "%s" does not belong to this survey.'

RandomChoice = collections.namedtuple('RandomChoice', ['question', 'weight'])


class QuestionType(messages.Enum):
  """An Enum to identify the type of question."""
  ASSIGNMENT = 0
  RETURN = 1


class Answer(ndb.Model):
  """Database model representing a survey question_text's answer.

  Attributes:
    text: str, The text to be displayed for the answer.
    more_info_enabled: bool, Indicating whether or not more info can be provided
        for this answer.
    placeholder_text: str, The text to be displayed in the more info box as a
        place holder.
  """
  text = ndb.StringProperty()
  more_info_enabled = ndb.BooleanProperty()
  placeholder_text = ndb.StringProperty()

  @classmethod
  def create(cls, text, more_info_enabled=False, placeholder_text=None):
    """Creates a new answer to a survey.

    Args:
      text: str, The text to be displayed for the answer.
      more_info_enabled: bool, Indicating whether or not more info can be
          provided for this answer.
      placeholder_text: str, The text to be displayed in the more info box as a
          place holder.

    Returns:
      The newly created instance of the Answer.

    Raises:
      ValueError: if more_info_enabled is True but there is no placeholder_text,
          or if the latter exists but more_info_enabled is False.
    """
    if bool(more_info_enabled) ^ bool(placeholder_text):
      raise ValueError(_MORE_INFO_MSG)
    return cls(
        text=text, more_info_enabled=more_info_enabled,
        placeholder_text=placeholder_text)


class Question(base_model.BaseModel):
  """Database model representing a queation asked as a question.

  Attributes:
    question_type: QuestionType, The type of question this is.
    question_text: str, The text displayed for this question.
    enabled: bool, Whether or not this question should be enabled.
    rand_weight: int, The weight to be applied to this question when using the
        get method question with random.
    answers: List of possible answers for this survey question.
    more_info_text: str, The more_info_text provided in a response.
    response: Answer, The response to the question by the user.
  """
  question_type = msgprop.EnumProperty(QuestionType, required=True)
  question_text = ndb.StringProperty(required=True)
  enabled = ndb.BooleanProperty(default=True)
  rand_weight = ndb.IntegerProperty(required=True)
  answers = ndb.StructuredProperty(Answer, repeated=True)
  more_info_text = ndb.StringProperty()
  response = ndb.StructuredProperty(Answer)

  @classmethod
  def create(cls, question_type, question_text, enabled, rand_weight, answers):
    """Creates a new question.

    Args:
      question_type: QuestionType, or str, The type of question this is,
          or a string referring to the item in the object.
      question_text: str, The text displayed for this question.
      enabled: bool, Whether or not this question is enabled.
      rand_weight: int, The weight applied to the question when using random
          question.
      answers: list, A list of Answer models for this survey question.

    Returns:
      The newly created instance of the Question.
    """
    if isinstance(question_type, basestring):
      question_type = getattr(QuestionType, question_type)
    question = cls(
        question_type=question_type,
        question_text=question_text,
        enabled=enabled,
        rand_weight=rand_weight,
        answers=answers)
    question.put()
    return question

  @classmethod
  def get_random(cls, question_type):
    """Get a random survey question by type.

    Args:
      question_type: QuestionType, The type of question requested.

    Returns:
      An instance of the Question, returns None if no questions of the
      provided type are found.
    """
    total_weight = 0
    questions = []
    active_questions = cls.query(ndb.AND(
        cls.enabled == True, cls.question_type == question_type)).fetch()  # pylint: disable=g-explicit-bool-comparison,singleton-comparison
    for question in active_questions:
      total_weight += question.rand_weight
      questions.append(
          RandomChoice(question, question.rand_weight))
    value = random.uniform(0, total_weight)
    upto = 0
    for question, weight in questions:
      if upto + weight >= value:
        return question
      upto += weight
    return None

  @classmethod
  def list(
      cls, question_type=None, enabled=True, page_size=100, next_cursor=None,
      **kwargs):
    """List all questions with filters.

    Args:
      question_type: QuestionType, The type of question to be queried for.
      enabled: bool, True to retrieve enabled surveys.
      page_size: int, The number of answers to return.
      next_cursor: datastore_query.Cursor, Next page of results.
      **kwargs: each kwarg name is the name of a Question property by
          which to filter the query and its value (string, integer, boolean,
          etc.).

    Returns:
      A tuple of a list of Question instances, datastore_query.Cursor
      instance, and a boolean representing whether or not there are more to
      retrieve.
    """
    query = cls.query(
        cls.enabled == enabled,  # pylint: disable=g-explicit-bool-comparison
        ndb.AND(cls.question_type == question_type))
    for filters, values in kwargs.items():
      if not isinstance(values, (list, tuple)):
        values = (values,)
      for value in values:
        query = query.filter(ndb.GenericProperty(filters) == value)
    return query.fetch_page(page_size=page_size, start_cursor=next_cursor)

  def patch(self, **kwargs):
    """Patch a change to a question.

    Args:
      **kwargs: A kwarg of the key/value pairs to patch.
    """
    self.populate(**kwargs)
    self.put()

  def submit(self, acting_user, selected_answer, more_info_text=None):
    """Submit the user-selected answer to a survey question.

    Args:
      acting_user: str, The email address of the user submitting the question.
      selected_answer: An Answer representing the answer the user selected.
      more_info_text: str, The optional more_info_text for the answer provided.
    """
    if config_model.Config.get('anonymous_surveys'):
      acting_user = constants.DEFAULT_ACTING_USER
    self.response = selected_answer
    self.more_info_text = more_info_text
    self.stream_to_bq(acting_user, 'Filing survey question response.')
    # The instance is not self.put() on purpose: it is meant to be a container
    # for the stream_to_bq when it receives a response.
