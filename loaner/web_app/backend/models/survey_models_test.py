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

"""Tests for backend.models.survey_models."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import mock

from loaner.web_app.backend.models import survey_models
from loaner.web_app.backend.testing import loanertest


class QuestionTest(loanertest.TestCase):

  def setUp(self):
    super(QuestionTest, self).setUp()
    self.answer1_text = 'Left my laptop at home.'
    self.answer1_more_info_enabled = False
    self.answer2_text = 'Convenience.'
    self.answer2_more_info_enabled = True
    self.answer2_placeholder_text = 'I don\'t carry my laptop into the office.'
    self.answer3_text = 'Borrowing for a meeting.'
    self.answer3_more_info_enabled = None
    self.answer4_text = 'For an interview.'
    self.answer4_more_info_enabled = True
    self.answer4_placeholder_text = 'What type of interview?'
    self.question_text1 = 'Why did you borrow this loaner?'
    self.question_text2 = 'Who are you?'
    self.question_text3 = 'What is the meaning of life?'
    self.question_text4 = 'What company do you work for?'
    self.create_test_questions()

  def create_test_answers(self):
    """Create the test answers to use in survey tests."""
    self.answer1 = survey_models.Answer.create(
        text=self.answer1_text,
        more_info_enabled=self.answer1_more_info_enabled,
        placeholder_text=None)
    self.answer2 = survey_models.Answer.create(
        text=self.answer2_text,
        more_info_enabled=self.answer2_more_info_enabled,
        placeholder_text=self.answer2_placeholder_text)
    self.answer3 = survey_models.Answer.create(
        text=self.answer3_text,
        more_info_enabled=self.answer3_more_info_enabled,
        placeholder_text=None)
    self.answer4 = survey_models.Answer.create(
        text=self.answer4_text,
        more_info_enabled=self.answer4_more_info_enabled,
        placeholder_text=self.answer4_placeholder_text)

  def test_answer_validation(self):
    """Tests that more_info_enabled validation works."""
    self.assertRaisesRegexp(
        survey_models.Answer.create,
        survey_models._MORE_INFO_MSG,
        text='Answer text',
        more_info_enabled=True)
    self.assertRaisesRegexp(
        survey_models.Answer.create,
        survey_models._MORE_INFO_MSG,
        text='Answer text',
        more_info_enabled=False,
        placeholder_text='Forbidden placeholder text')

  def create_test_questions(self):
    """Create the test surveys to use in other tests."""
    self.create_test_answers()
    self.question1 = survey_models.Question.create(
        question_type=survey_models.QuestionType.ASSIGNMENT,
        question_text=self.question_text1,
        enabled=True,
        rand_weight=1,
        answers=[self.answer1, self.answer2])
    self.question2 = survey_models.Question.create(
        # The following line verifies we can specify enum items by string.
        question_type='RETURN',
        question_text=self.question_text2,
        enabled=True,
        rand_weight=2,
        answers=[self.answer2])
    self.question3 = survey_models.Question.create(
        question_type=survey_models.QuestionType.ASSIGNMENT,
        question_text=self.question_text3,
        enabled=False,
        rand_weight=3,
        answers=[self.answer3, self.answer4])
    self.question4 = survey_models.Question.create(
        question_type=survey_models.QuestionType.RETURN,
        question_text=self.question_text4,
        enabled=False,
        rand_weight=4,
        answers=[self.answer4])

  def test_create_surveys(self):
    """Test the creation of surveys."""
    self.assertEqual(
        self.question1.question_type,
        survey_models.QuestionType.ASSIGNMENT)
    self.assertEqual(self.question1.question_text, self.question_text1)
    self.assertTrue(self.question1.enabled)
    self.assertEqual(self.question1.rand_weight, 1)
    self.assertListEqual(
        self.question1.answers, [self.answer1, self.answer2])

    self.assertEqual(
        self.question2.question_type,
        survey_models.QuestionType.RETURN)
    self.assertEqual(self.question2.question_text, self.question_text2)
    self.assertTrue(self.question2.enabled)
    self.assertEqual(self.question2.rand_weight, 2)
    self.assertListEqual(self.question2.answers, [self.answer2])

    self.assertEqual(
        self.question3.question_type,
        survey_models.QuestionType.ASSIGNMENT)
    self.assertEqual(self.question3.question_text, self.question_text3)
    self.assertFalse(self.question3.enabled)
    self.assertEqual(self.question3.rand_weight, 3)
    self.assertListEqual(
        self.question3.answers, [self.answer3, self.answer4])

    self.assertEqual(
        self.question4.question_type,
        survey_models.QuestionType.RETURN)
    self.assertEqual(self.question4.question_text, self.question_text4)
    self.assertFalse(self.question4.enabled)
    self.assertEqual(self.question4.rand_weight, 4)
    self.assertListEqual(self.question4.answers, [self.answer4])

  def test_get_survey_random(self):
    """Test the get survey with a random choice."""
    self.question2.rand_weight = 1
    self.question2.put()
    self.question4.enabled = True
    self.question4.rand_weight = 100
    self.question4.put()
    questions = []
    for _ in xrange(50):
      questions.append(
          survey_models.Question.get_random(
              question_type=survey_models.QuestionType.RETURN))
    survey2_count = 0
    survey4_count = 0
    for question in questions:
      if question == self.question2:
        survey2_count += 1
      elif question == self.question4:
        survey4_count += 1
    self.assertGreater(survey4_count, survey2_count)

  def test_get_survey_random_none(self):
    """Test getting a random survey when none match the filters."""
    self.question2.enabled = False
    self.question2.put()
    self.assertIsNone(survey_models.Question.get_random(
        question_type=survey_models.QuestionType.RETURN))

  def test_list_surveys_minimal_filters(self):
    """Test the listing of surveys with minimal filters applied."""
    self.question3.enabled = True
    self.question3.put()
    surveys = survey_models.Question.list(
        question_type=survey_models.QuestionType.ASSIGNMENT)
    self.assertListEqual(
        surveys[0], [self.question1, self.question3])

  def test_list_surveys_filtered(self):
    """Test the listing of surveys with filters applied."""
    self.question3.enabled = True
    self.question3.put()
    surveys = survey_models.Question.list(
        question_type=survey_models.QuestionType.ASSIGNMENT,
        question_text=self.question_text1)
    self.assertListEqual(surveys[0], [self.question1])

  def test_patch_new_answers(self):
    """Test patching answers on a survey question."""
    self.assertEqual(self.question2.answers, [self.answer2])
    self.question2.patch(answers=[self.answer3, self.answer4])
    question = self.question2.key.get()
    self.assertListEqual(question.answers, [self.answer3, self.answer4])

  def test_patch_new_settings(self):
    """Test the patching settings on a question."""
    self.question1.patch(enabled=False, rand_weight=3)
    question = survey_models.Question.query(
        survey_models.Question.question_text ==
        self.question_text1).get()
    self.assertFalse(question.enabled)
    self.assertEqual(question.rand_weight, 3)

  def test_submit_survey_anonymously(self):
    """Test the submission of a survey anonymously."""
    survey_models.config_model.Config.set('anonymous_surveys', True)
    with mock.patch.object(
        self.question1, 'stream_to_bq', autospec=True) as mock_stream:
      self.question1.submit(
          selected_answer=self.answer1, acting_user=loanertest.USER_EMAIL)
      self.assertEqual(self.question1.response, self.answer1)
      mock_stream.assert_called_once_with(
          survey_models.constants.DEFAULT_ACTING_USER,
          'Filing survey question response.')

    with mock.patch.object(
        self.question2, 'stream_to_bq', autospec=True) as mock_stream:
      self.question2.submit(
          selected_answer=self.answer2,
          acting_user=survey_models.constants.DEFAULT_ACTING_USER,
          more_info_text='More info!')
      self.assertEqual(self.question2.response, self.answer2)
      mock_stream.assert_called_once_with(
          survey_models.constants.DEFAULT_ACTING_USER,
          'Filing survey question response.')

  def test_submit_survey(self):
    """Test the submission of a question."""
    survey_models.config_model.Config.set('anonymous_surveys', False)
    with mock.patch.object(
        self.question1, 'stream_to_bq', autospec=True) as mock_stream:
      self.question1.submit(
          selected_answer=self.answer1, acting_user=loanertest.USER_EMAIL)
      self.assertEqual(self.question1.response, self.answer1)
      mock_stream.assert_called_once_with(
          loanertest.USER_EMAIL, 'Filing survey question response.')

    with mock.patch.object(
        self.question2, 'stream_to_bq', autospec=True) as mock_stream:
      self.question2.submit(
          selected_answer=self.answer2,
          acting_user=loanertest.USER_EMAIL,
          more_info_text='More info!')
      self.assertEqual(self.question2.response, self.answer2)
      mock_stream.assert_called_once_with(
          loanertest.USER_EMAIL, 'Filing survey question response.')


if __name__ == '__main__':
  loanertest.main()
