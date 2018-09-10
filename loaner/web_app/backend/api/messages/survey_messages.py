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

"""Survey Question messages for the Survey Question API."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from protorpc import messages

from loaner.web_app.backend.models import survey_models


class Answer(messages.Message):
  """Answer ProtoRPC Message to encapsulate the survey_models.Answer.

  Attributes:
    text: str, The text to be displayed for the answer.
    more_info_enabled: bool, Indicating whether or not more info can be provided
        for this answer.
    placeholder_text: str, The text to be displayed in the more info box as a
        place holder.
  """
  text = messages.StringField(1)
  more_info_enabled = messages.BooleanField(2)
  placeholder_text = messages.StringField(3)


class Question(messages.Message):
  """Question ProtoRPC Message for survey_models.Question.

  Attributes:
    question_type: survey_models.QuestionType, The type of survey
        this is.
    question_text: str, The text displayed as the question for this survey.
    enabled: bool, Whether or not this survey should be enabled.
    rand_weight: int, The weight to be applied to this survey when using the
        get method survey with random.
    answers: List of Answer, The list of answers possible for this survey.
    question_urlsafe_key: str, The ndb.Key.urlsafe() for the survey.
    required: bool, Whether or not the survey is required.
  """
  question_type = messages.EnumField(
      survey_models.QuestionType, 1, required=True)
  question_text = messages.StringField(2, required=True)
  enabled = messages.BooleanField(3, default=True)
  rand_weight = messages.IntegerField(4, default=1)
  answers = messages.MessageField(Answer, 5, repeated=True)
  question_urlsafe_key = messages.StringField(6)
  required = messages.BooleanField(7, required=True)


class PatchQuestionRequest(messages.Message):
  """PatchSurveyRequest ProtoRPC Message.

  Attributes:
    question_urlsafe_key: str, The ndb.Key.urlsafe() for the survey.
    answers: List of Answer, The list of answers possible for this survey.
    question_type: survey_models.QuestionType, The type of survey
        question this is.
    question_text: str, The text displayed as the question for this survey.
    enabled: bool, Whether or not this survey should be enabled.
    rand_weight: int, The weight to be applied to this survey when using the
        get method survey with random.
  """
  question_urlsafe_key = messages.StringField(1, required=True)
  answers = messages.MessageField(Answer, 2, repeated=True)
  question_type = messages.EnumField(
      survey_models.QuestionType, 4)
  question_text = messages.StringField(5)
  enabled = messages.BooleanField(6)
  rand_weight = messages.StringField(7)


class QuestionList(messages.Message):
  """QuestionList ProtoRPC Message.

  Attributes:
    questions: List[Question], The list of questions to return.
    page_token: str, The urlsafe representation of the page token.
    more: bool, Whether or not there are more results to be queried.
  """
  questions = messages.MessageField(Question, 1, repeated=True)
  page_token = messages.StringField(2)
  more = messages.BooleanField(3)


class QuestionRequest(messages.Message):
  """QuestionRequest ProtoRPC Message.

  Attributes:
    question_type: survey_models.SurveyType, The type of survey being
        requested.
  """
  question_type = messages.EnumField(
      survey_models.QuestionType, 1, required=True)


class QuestionSubmission(messages.Message):
  """QuestionSubmission ProtoRPC Message.

  Attributes:
    question_urlsafe_key: str, The urlsafe ndb.Key for a
        survey_models.Survey instace.
    selected_answer: Answer, The answer a user selected.
    more_info_text: str, the extra info optionally provided for the given
        Answer.
  """
  question_urlsafe_key = messages.StringField(1, required=True)
  selected_answer = messages.MessageField(Answer, 2, required=True)
  more_info_text = messages.StringField(3)


class ListQuestionsRequest(messages.Message):
  """ListQuestionsRequest ProtoRPC Message.

  Attributes:
    question_type: survey_models.QuestionType, The type of survey
        to list.
    enabled: bool, True for only enabled surveys, False to view disabled
        surveys.
    page_size: int, The size of the page to return.
    page_token: str, The urlsafe representation of the page token.
  """
  question_type = messages.EnumField(
      survey_models.QuestionType, 1, required=True)
  enabled = messages.BooleanField(2, default=True)
  page_size = messages.IntegerField(3, default=100)
  page_token = messages.StringField(4)
