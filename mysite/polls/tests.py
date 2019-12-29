import datetime

from django.utils import timezone
from django.test import TestCase
from django.urls import reverse

from .models import Question
# Create your tests here.

def create_question(question_text,days):
    """
    Create a question with the given `question_text` and published the
    fiven number of days offfset to now (negative for question published
    in the past and positive for the question that have yet to be published).
    """
    time = timezone.now()+datetime.timedelta(days = days)
    return Question.objects.create(question_text=question_text,pub_date=time)

class QuestonIndexViewTests(TestCase):
    def test_no_questions(self):
        """
        If no questions exist, an appropriate messsage os displayed.
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code,200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'],[])

    def test_past_question(self):
        """
        question with a pub_date in past are displayed on the
        index page.
        """
        create_question(question_text="Past question.",days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code,200)
        self.assertQuerysetEqual(response.context['latest_question_list'],['<Question: Past question.>'])

    def test_future_question(self):
        """
        question with a pub_date in future aren't displayed on
        the index page
        """
        create_question(question_text="Future question.",days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code,200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'],[])

    def test_future_question_and_past_question(self):
        """
        question with a pub_date in future aren't displayed on
        the index page
        """
        create_question(question_text="Past question.",days=-30)
        create_question(question_text="Future question.",days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code,200)
        self.assertQuerysetEqual(response.context['latest_question_list'],['<Question: Past question.>'])

    def test_two_past_questions(self):
        """
        The Question index page may display multiple questions.
        """
        create_question(question_text="Past question 1.",days=-30)
        create_question(question_text="Past question 2.",days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code,200)
        self.assertQuerysetEqual(response.context['latest_question_list'],
            ['<Question: Past question 2.>','<Question: Past question 1.>'])

class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future
        returns a 404 not found
        """
        future_question = create_question(question_text="Future question.",days=30)
        url = reverse('polls:detail',args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code,404)

    def test_past_question(self):
        """
        question with a pub_date in past are displayed on the
        detail page.
        """
        past_question=create_question(question_text="Past question.",days=-30)
        url = reverse('polls:detail',args=(past_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code,200)
        self.assertContains(response,past_question.question_text)


class QuestionModelTests(TestCase):

    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future.
        """
        time = timezone.now() + datetime.timedelta(days = 30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(),False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is older than 1 day
        """
        time = timezone.now() - datetime.timedelta(days = 1,seconds=1)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(),False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is with in the last day
        """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(),True)
