from django.db import models
from django.contrib.auth.models import User
from django.utils.datetime_safe import datetime


DONATION_TYPES_CHOICES = (
    ('onetime', 'One time'),
    ('monthly', 'Monthly'),
)

PROJECT_USER_ROLES = (
    ('treasurer', 'Treasurer'),
    ('maintainer', 'Maintainer'),
    ('developer', 'Developer'),
)


class Project(models.Model):
    key           = models.CharField(max_length=80, unique=True)
    title         = models.CharField(max_length=255)
    description   = models.TextField(null=True, blank=True)
    logo          = models.ImageField(null=True, blank=True, upload_to='project_logo/')
    date_added    = models.DateTimeField('date added', default = datetime.now())
    other_sources = models.DecimalField(decimal_places=0, max_digits=6, null=True, blank=True)
    maintainer    = models.ForeignKey(User, null=True, blank=True)
    is_public     = models.BooleanField(default=True)
    
    def __unicode__(self):
        return self.title

class ProjectNeed(models.Model):
    project       = models.ForeignKey(Project)
    key           = models.CharField(max_length=80, null=True, blank=True)
    title         = models.CharField(max_length=255)
    description   = models.CharField(max_length=255, null=True, blank=True)
    amount        = models.DecimalField(decimal_places=0, max_digits=12, default=0)
    date_added    = models.DateTimeField('date added', default=datetime.now())

class ProjectGoal(models.Model):
    project       = models.ForeignKey(Project)
    key           = models.CharField(max_length=80, null=True, blank=True)
    title         = models.CharField(max_length=255)
    description   = models.CharField(max_length=255, null=True, blank=True)
    amount        = models.DecimalField(decimal_places=0, max_digits=12, default=0)
    date_ending   = models.DateField('date ending')
    date_added    = models.DateTimeField('date added', default=datetime.now())
    
class ProjectFeatureRequest(models.Model):
    user          = models.ForeignKey(User)
    project       = models.ForeignKey(Project)
    title         = models.CharField(max_length=200)
    description   = models.TextField()
    
class ProjectUserRole(models.Model):
    user          = models.ForeignKey(User)
    project       = models.ForeignKey(Project)
    user_role     = models.CharField(max_length=10, choices=PROJECT_USER_ROLES, null=True, blank=True)


"""
class Event(models.Model):
    TASK_SIZES = (
        (u'XS', u'XSmall'),
        (u'S', u'Small'),
        (u'M', u'Medium'),
        (u'L', u'Large'),
        (u'XL', u'XLarge'),
    )
    task_size  = models.CharField(max_length=2, choices=TASK_SIZES)
    
    def __unicode__(self):
        return self.summary
"""
