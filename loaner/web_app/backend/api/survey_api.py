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

"""The entry point for the Survey Question methods."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from protorpc import message_types

import endpoints

from loaner.web_app.backend.api import auth
from loaner.web_app.backend.api import permissions
from loaner.web_app.backend.api import root_api
from loaner.web_app.backend.api.messages import survey_messages
from loaner.web_app.backend.lib import api_utils
from loaner.web_app.backend.lib import user as user_lib
from loaner.web_app.backend.models import config_model
from loaner.web_app.backend.models import survey_models

_NOT_ENOUGH_ANSWERS_MSG = 'Not enough possible answers provided.'
_NO_QUESTION_FOR_TYPE_MSG = (
    'There is no survey question configured for type %s.')


@root_api.ROOT_API.api_class(resource_name='survey', path='survey')
class SurveyApi(root_api.Service):
  """This class is for the Survey API."""

  @auth.method(
      survey_messages.Question,
      message_types.VoidMessage,
      name='create',
      path='create',
      http_method='POST',
      permission=permissions.Permissions.MODIFY_SURVEY)
  def create(self, request):
    """Creates a new survey question and insert instance into datastore."""
    self.check_xsrf_token(self.request_state)
    if len(request.answers) < 1:
      raise endpoints.BadRequestException(_NOT_ENOUGH_ANSWERS_MSG)

    answers = []
    for answer_message in request.answers:
      try:
        answers.append(survey_models.Answer.create(
            text=answer_message.text,
            more_info_enabled=answer_message.more_info_enabled,
            placeholder_text=answer_message.placeholder_text))
      except ValueError as e:
        raise endpoints.BadRequestException(e.message)

    survey_models.Question.create(
        question_type=request.question_type,
        question_text=request.question_text,
        enabled=request.enabled,
        rand_weight=request.rand_weight,
        answers=answers)

    return message_types.VoidMessage()

  @auth.method(
      survey_messages.QuestionRequest,
      survey_messages.Question,
      name='request',
      path='request',
      http_method='GET')
  def request(self, request):
    """Requests a survey by type and shows that survey to a Chrome App user."""
    question = survey_models.Question.get_random(
        request.question_type)
    if not question:
      raise endpoints.NotFoundException(
          _NO_QUESTION_FOR_TYPE_MSG % request.question_type)
    return _build_survey_messages(question)

  @auth.method(
      survey_messages.QuestionSubmission,
      message_types.VoidMessage,
      name='submit',
      path='submit',
      http_method='POST')
  def submit(self, request):
    """Submits a response to a survey question."""
    user_email = user_lib.get_user_email()
    question = api_utils.get_ndb_key(
        urlsafe_key=request.question_urlsafe_key).get()
    selected_answer = survey_models.Answer.create(
        text=request.selected_answer.text,
        more_info_enabled=request.selected_answer.more_info_enabled,
        placeholder_text=request.selected_answer.placeholder_text)
    question.submit(
        acting_user=user_email,
        selected_answer=selected_answer,
        more_info_text=request.more_info_text)
    return message_types.VoidMessage()

  @auth.method(
      survey_messages.ListQuestionsRequest,
      survey_messages.QuestionList,
      name='list',
      path='list',
      http_method='GET',
      permission=permissions.Permissions.READ_SURVEYS)
  def list(self, request):
    """Lists survey questions."""
    cursor = None
    if request.page_token:
      cursor = api_utils.get_datastore_cursor(urlsafe_cursor=request.page_token)

    questions, next_cursor, more = (
        survey_models.Question.list(
            question_type=request.question_type,
            enabled=request.enabled,
            page_size=request.page_size,
            next_cursor=cursor))
    response = survey_messages.QuestionList()
    for question in questions:
      response.questions.append(
          _build_survey_messages(question))
    if next_cursor or more:
      response.page_token = next_cursor.urlsafe()
      response.more = more
    return response

  @auth.method(
      survey_messages.PatchQuestionRequest,
      message_types.VoidMessage,
      name='patch',
      path='patch',
      http_method='POST',
      permission=permissions.Permissions.MODIFY_SURVEY)
  def patch(self, request):
    """Patches a given survey question."""
    self.check_xsrf_token(self.request_state)
    question = api_utils.get_ndb_key(
        urlsafe_key=request.question_urlsafe_key).get()
    answers = []
    for answer in request.answers:
      try:
        new_answer = survey_models.Answer.create(
            text=answer.text,
            more_info_enabled=answer.more_info_enabled,
            placeholder_text=answer.placeholder_text)
        answers.append(new_answer)
      except ValueError as e:
        raise endpoints.BadRequestException(e.message)
    survey_kwargs = api_utils.to_dict(request, survey_models.Question)
    survey_kwargs['answers'] = answers
    question.patch(**survey_kwargs)
    return message_types.VoidMessage()


def _build_survey_messages(question_model):
  """Builds a Question message from a Question NDB model instance.

  Args:
    question_model: survey_models.Question, An instance of the
        Question NDB model from datastore.

  Returns:
    A populated survey question message.
  """
  message = survey_messages.Question(
      question_type=question_model.question_type,
      question_text=question_model.question_text,
      enabled=question_model.enabled,
      rand_weight=question_model.rand_weight,
      question_urlsafe_key=question_model.key.urlsafe(),
      required=config_model.Config.get('require_surveys'),
  )
  for answer in question_model.answers:
    message.answers.append(survey_messages.Answer(
        text=answer.text,
        more_info_enabled=answer.more_info_enabled,
        placeholder_text=answer.placeholder_text))
  return message
