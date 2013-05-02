# -*- encoding: utf-8 -*-

"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

import datetime
from django.test import TestCase
from django.db import IntegrityError
from survey.models import Survey, Question


class SurveySaveTest(TestCase):
    """Tests for the Survey save override method"""
    t = "New Year's Resolutions"
    sd = datetime.date(2009, 12, 28)

    def testClosesAutoset(self):
        """Verify closes is autoset correctly"""
        s = Survey.objects.create(title=self.t, opens=self.sd)
        self.assertEqual(s.closes, datetime.date(2010, 1, 4),
                         "closes not autoset to 7 days after opens, expected %s, "
                         "actually %s" %
                         (datetime.date(2010, 1, 4), s.closes))

    def testClosesHonored(self):
        """Verify closes is honered if specified"""
        s = Survey.objects.create(title=self.t, opens=self.sd,
                                  closes=self.sd)
        self.assertEqual(s.closes, self.sd)

    def testClosesReset(self):
        """Verify that closes is only autoset during initial create"""
        s = Survey.objects.create(title=self.t, opens=self.sd)
        s.closes = None
        self.assertRaises(IntegrityError, s.save)

    def testTitleOnly(self):
        """Verify correct exception is raised in error case"""
        self.assertRaises(IntegrityError, Survey.objects.create,
                          title=self.t)


class SurveyUnicodeTest(TestCase):
    def testUnicode(self):
        t = u'¿Como est󠁠á usted?'
        sd = datetime.date(2009, 12, 28)
        s = Survey.objects.create(title=t, opens=sd)
        self.assertEqual(unicode(s),
            u'¿Como est󠁠á usted? (Opens 2009-12-28, closes 2010-01-04)')


class QuestionWinningAnswersTest(TestCase):

    fixtures = ['test_winning_answers.json']

    def testClearWinner(self):
        q = Question.objects.get(question='Clear Winner')
        wa_qs = q.winning_answers()
        self.assertEqual(wa_qs.count(), 1)
        winner = wa_qs[0]
        self.assertEqual(winner.answer, 'Max Votes')

    def testTwoWayTie(self):
        q = Question.objects.get(question='2-Way Tie')
        wa_qs = q.winning_answers()
        self.assertEqual(wa_qs.count(), 2)
        for winner in wa_qs:
            self.assert_(winner.answer.startswith('Max Votes'))

    def testNoResponses(self):
        q = Question.objects.get(question='No Responses')
        wa_qs = q.winning_answers()
        self.assertEqual(wa_qs.count(), 0)

    def testNoAnswers(self):
        q = Question.objects.get(question='No Answers')
        wa_qs = q.winning_answers()
        self.assertEqual(wa_qs.count(), 0)
