import datetime
from django.db import models
from django.db.models import Max


class SurveyManager(models.Manager):
    def completed(self):
        return self.filter(closes__lt=datetime.date.today())

    def active(self):
        return self.filter(opens__lte=datetime.date.today()).\
            filter(closes__gte=datetime.date.today())

    def upcoming(self):
        return self.filter(opens__gt=datetime.date.today())


class Survey(models.Model):
    title = models.CharField(max_length=60)
    opens = models.DateField()
    closes = models.DateField(blank=True)

    objects = SurveyManager()

    def __unicode__(self):
        return u'%s (Opens %s, closes %s)' % (self.title,
                                              self.opens,
                                              self.closes)

    def save(self, **kwargs):
        if not self.pk and self.opens and not self.closes:
            self.closes = self.opens + datetime.timedelta(7)
        super(Survey, self).save(**kwargs)

    @models.permalink
    def get_absolute_url(self):
        return ('survey_detail', (self.pk,))


class Question(models.Model):
    question = models.CharField(max_length=200)
    survey = models.ForeignKey(Survey)

    def __unicode__(self):
        return u'%s: %s' % (self.survey, self.question)

    def winning_answers(self):
        max_votes = self.answer_set.aggregate(Max('votes')).values()[0]
        if max_votes and max_votes > 0:
            rv = self.answer_set.filter(votes=max_votes)
        else:
            rv = self.answer_set.none()
        return rv


class Answer(models.Model):
    answer = models.CharField(max_length=200)
    question = models.ForeignKey(Question)
    votes = models.IntegerField(default=0)
