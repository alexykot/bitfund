from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now

from model_utils import Choices


BLOGPOST_STATUS_CHOICES = Choices(
    ('unpublished', u'Unpublished'),
    ('published', u'Published'),
)

BLOGCOMMENT_STATUS_CHOICES = Choices(
    ('published', u'Published'),
    ('censored', u'Censored'),
    ('removed', u'Removed'),
)

class BlogPost(models.Model):
    title = models.CharField(max_length=1000)
    slug = models.CharField(max_length=255, unique=True)
    extract = models.TextField(null=True, blank=True)
    body = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=64, choices=BLOGPOST_STATUS_CHOICES, default=BLOGPOST_STATUS_CHOICES.unpublished)
    order = models.IntegerField(default=0)
    date_added = models.DateTimeField('date added', default=now())

class BlogComment(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    blogpost = models.ForeignKey(BlogPost, on_delete=models.PROTECT)
    text = models.TextField(null=True, blank=True)
    date_added = models.DateTimeField('date added', default=now())
    status = models.CharField(max_length=64, choices=BLOGCOMMENT_STATUS_CHOICES, default=BLOGCOMMENT_STATUS_CHOICES.published)
