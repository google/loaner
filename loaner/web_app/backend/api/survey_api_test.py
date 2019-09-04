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

"""Tests for backend.api.survey_api."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import itertools

from absl.testing import parameterized
import mock

from protorpc import message_types

import endpoints

from loaner.web_app.backend.api import root_api  # pylint: disable=unused-import
from loaner.web_app.backend.api import survey_api
from loaner.web_app.backend.api.messages import survey_messages
from loaner.web_app.backend.models import survey_models
from loaner.web_app.backend.testing import loanertest


_QUESTION = 'TEST SURVEY QUESTION NUMBER {num}, DO NOT USE'


def _generate_message_parameters(want_permutations=False):
  """Generate message parameters for test cases.

  Args:
    want_permutations: bool, whether or not to run the messages through various
        permutations.

  Yields:
    A list containing the list of messages.
  """
  answer_message = survey_messages.Answer(
      text='Left my laptop at home.',
      more_info_enabled=False,
      placeholder_text=None)
  survey_messages_1 = survey_messages.Question(
      question_type=survey_models.QuestionType.ASSIGNMENT,
      question_text=_QUESTION.format(num=1),
      answers=[answer_message],
      rand_weight=1,
      required=True)
  survey_messages_2 = survey_messages.Question(
      question_type=survey_models.QuestionType.ASSIGNMENT,
      question_text=_QUESTION.format(num=2),
      answers=[answer_message],
      rand_weight=1,
      enabled=False,
      required=False)
  survey_messages_3 = survey_messages.Question(
      question_type=survey_models.QuestionType.RETURN,
      question_text=_QUESTION.format(num=3),
      answers=[answer_message],
      rand_weight=1,
      enabled=True)
  messages = [
      survey_messages_1, survey_messages_2,
      survey_messages_3]
  if want_permutations:
    for p in itertools.permutations(messages):
      yield [p]
  else:
    yield [messages]


class QuestionEndpointsTest(
    parameterized.TestCase, loanertest.EndpointsTestCase):
  """Test the Question endpoints api."""

  def setUp(self):
    super(QuestionEndpointsTest, self).setUp()
    self.service = survey_api.SurveyApi()
    self.login_admin_endpoints_user()

  def tearDown(self):
    super(QuestionEndpointsTest, self).tearDown()
    self.service = None

  def create_test_models(self, iterations):
    """Creates models directly for testing.

    Args:
      iterations: int, The number of Answers and Questions to create.

    Returns:
      Two ndb.Key lists for the manually created Answers and Questions.
    """
    question_keys = []
    answers = []
    for i in xrange(iterations):
      answers.append(survey_models.Answer.create(
          text='Answer {num}'.format(num=i),
          more_info_enabled=True,
          placeholder_text='PlaceHolder {num}'.format(num=i)))
      question_keys.append(survey_models.Question(
          question_type=survey_models.QuestionType.ASSIGNMENT,
          question_text=_QUESTION.format(num=i),
          enabled=True,
          rand_weight=1,
          answers=answers).put())
    return answers, question_keys

  @parameterized.parameters(_generate_message_parameters())
  @mock.patch('__main__.survey_models.Question.create')
  @mock.patch('__main__.root_api.Service.check_xsrf_token')
  def test_create(
      self, messages, mock_xsrf_token, mock_survey_create):
    """Test the creation of a new survey question via the API method."""
    for message in messages:
      response = self.service.create(message)
      self.assertEqual(mock_survey_create.call_count, 1)
      mock_survey_create.reset_mock()
      self.assertIsInstance(response, message_types.VoidMessage)
      self.assertEqual(mock_xsrf_token.call_count, 1)
      mock_xsrf_token.reset_mock()

  @mock.patch('__main__.root_api.Service.check_xsrf_token')
  def test_create_not_enough_answers(self, mock_xsrf_token):
    """Creating a survey without enough answers, raises BadRequestException."""
    del mock_xsrf_token  # Unused.
    request = survey_messages.Question(
        question_type=survey_models.QuestionType.ASSIGNMENT,
        question_text='How are you today?')
    with self.assertRaisesRegexp(
        endpoints.BadRequestException,
        survey_api._NOT_ENOUGH_ANSWERS_MSG):
      self.service.create(request)

  @mock.patch('__main__.root_api.Service.check_xsrf_token')
  def test_create_no_more_info_enabled(self, mock_xsrf_token):
    """Create question when more_info_text, placeholder_text not both there."""
    del mock_xsrf_token  # Unused.
    malformed_answer_message_1 = survey_messages.Answer(
        text='This is a malformed message, do not use.',
        more_info_enabled=True,
        placeholder_text=None)
    malformed_answer_message_2 = survey_messages.Answer(
        text='This is a malformed message, do not use.',
        more_info_enabled=False,
        placeholder_text='False place holder text.')
    request = survey_messages.Question(
        question_type=survey_models.QuestionType.ASSIGNMENT,
        question_text=_QUESTION.format(num=1),
        rand_weight=1,
        enabled=True)

    # Test that more info without place holder text raises an exception.
    with self.assertRaisesRegexp(
        endpoints.BadRequestException,
        survey_models._MORE_INFO_MSG):
      request.answers = [malformed_answer_message_1]
      self.service.create(request)

    # Test that place holder text without more info raises an exception.
    with self.assertRaisesRegexp(
        endpoints.BadRequestException,
        survey_models._MORE_INFO_MSG):
      request.answers = [malformed_answer_message_2]
      self.service.create(request)

  @parameterized.parameters(
      _generate_message_parameters(want_permutations=True))
  def test_request(self, messages):
    """Test the request survey api method returns the correct survey."""
    for message in messages:
      self.service.create(message)
    response = self.service.request(
        survey_messages.QuestionRequest(
            question_type=survey_models.QuestionType.ASSIGNMENT))
    self.assertEqual(
        response.question_type, survey_models.QuestionType.ASSIGNMENT)
    self.assertEqual(response.question_text, _QUESTION.format(num=1))

  def test_request_no_survey_found(self):
    """Test request method when no survey exists, raises NotFoundException."""
    request = survey_messages.QuestionRequest(
        question_type=survey_models.QuestionType.ASSIGNMENT)
    with self.assertRaisesRegexp(
        endpoints.NotFoundException,
        survey_api._NO_QUESTION_FOR_TYPE_MSG % request.question_type):
      self.service.request(request)

  @mock.patch('__main__.survey_models.Question.submit')
  def test_survey_submission(self, mock_submit):
    """Test the survey submission api method."""
    more_info_text = 'More info!'
    answers, question_keys = self.create_test_models(1)
    answer_message = survey_messages.Answer(
        text=answers[0].text, more_info_enabled=answers[0].more_info_enabled,
        placeholder_text=answers[0].placeholder_text)
    expected_answer = survey_models.Answer.create(
        text=answer_message.text,
        more_info_enabled=answer_message.more_info_enabled,
        placeholder_text=answer_message.placeholder_text)
    request = survey_messages.QuestionSubmission(
        question_urlsafe_key=question_keys[0].urlsafe(),
        selected_answer=answer_message, more_info_text=more_info_text)
    response = self.service.submit(request)
    self.assertIsInstance(response, message_types.VoidMessage)
    mock_submit.assert_called_once_with(
        acting_user=loanertest.SUPER_ADMIN_EMAIL,
        selected_answer=expected_answer, more_info_text=more_info_text)

  def test_list_surveys(self):
    """Test the list surveys api method."""
    _, question_keys = self.create_test_models(3)
    request = survey_messages.ListQuestionsRequest(
        question_type=survey_models.QuestionType.ASSIGNMENT)
    response = self.service.list(request)
    self.assertEqual(len(question_keys), len(response.questions))

  @parameterized.parameters(
      {'num_surveys': 3, 'page_size': 1},
      {'num_surveys': 4, 'page_size': 2},
      {'num_surveys': 7, 'page_size': 3},
  )
  def test_list_surveys_with_page(self, num_surveys, page_size):
    """Test the list surveys api method when a next page exists."""
    i = 0
    _, question_keys = self.create_test_models(num_surveys)
    request = survey_messages.ListQuestionsRequest(
        question_type=survey_models.QuestionType.ASSIGNMENT,
        page_size=page_size)
    response = self.service.list(request)
    while response.page_token or response.more:
      for question in response.questions:
        self.assertEqual(
            question.question_text,
            question_keys[i].get().question_text)
        i += 1
      request.page_token = response.page_token
      response = self.service.list(request)
    self.assertEqual(i, num_surveys)

  @mock.patch('__main__.root_api.Service.check_xsrf_token')
  def test_patch_survey_with_answers_to_be_added(self, mock_xsrf_token):
    """Test patch survey api method with new answers."""
    # Create test objects.
    _, question_keys = self.create_test_models(1)
    question_key = question_keys[0]
    # New Answer to be added.
    new_answer_message1 = survey_messages.Answer(
        text='NEW TEXT, DO NOT USE',
        more_info_enabled=True,
        placeholder_text='PLACEHOLDER TEXT')
    new_answer_message2 = survey_messages.Answer(
        text='NEW TEXT, DO NOT USE',
        more_info_enabled=False)
    request = survey_messages.PatchQuestionRequest(
        question_urlsafe_key=question_key.urlsafe(),
        answers=[new_answer_message1, new_answer_message2])
    self.service.patch(request)
    self.assertEqual(mock_xsrf_token.call_count, 1)
    # Ensure the new answer was created.
    self.assertLen(question_key.get().answers, 2)


if __name__ == '__main__':
  loanertest.main()
