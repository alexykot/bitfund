from django.db import models
from django.contrib.auth.models import User
from django.utils.datetime_safe import datetime

from project.lists import * 

class ProjectCategory(models.Model):
    key           = models.CharField(max_length=80, unique=True)
    title         = models.CharField(max_length=255)
    description   = models.TextField(null=True, blank=True)
    logo          = models.ImageField(upload_to='project_category_logo/', null=True, blank=True)
    date_added    = models.DateTimeField('date added', default = datetime.now())

class Project(models.Model):
    key           = models.CharField(max_length=80, unique=True)
    title         = models.CharField(max_length=255)
    brief         = models.CharField(max_length=255, null=True, blank=True)
    categories    = models.ManyToManyField(ProjectCategory)
    about         = models.TextField(null=True, blank=True)
    contribute    = models.TextField(null=True, blank=True)
    logo          = models.ImageField(upload_to='project_logo/', null=True, blank=True)
    date_added    = models.DateTimeField('date added', default = datetime.now())
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
    is_public     = models.BooleanField(default=True)

class ProjectGoal(models.Model):
    project       = models.ForeignKey(Project)
    key           = models.CharField(max_length=80, null=True, blank=True)
    title         = models.CharField(max_length=255)
    brief         = models.CharField(max_length=255, null=True, blank=True)
    description   = models.TextField(null=True, blank=True)
    image         = models.ImageField(upload_to='project_goals/', null=True, blank=True)
    video_url     = models.CharField(max_length=255, null=True, blank=True)
    amount        = models.DecimalField(decimal_places=0, max_digits=12, default=0)
    date_ending   = models.DateField('date ending')
    date_added    = models.DateTimeField('date added', default=datetime.now())
    is_public     = models.BooleanField(default=True)
    
class ProjectUserRole(models.Model):
    from pledger.models import Profile

    profile         = models.ForeignKey(Profile)
    project         = models.ForeignKey(Project)
    user_role       = models.CharField(max_length=10, choices=PROJECT_USER_ROLES, null=True, blank=True)
    user_role_title = models.CharField(max_length=255, null=True, blank=True)
    sort_order      = models.IntegerField(default=0)
    date_added      = models.DateTimeField('date added', default = datetime.now())

class ProjectOutlink(models.Model):
    project         = models.ForeignKey(Project)
    type            = models.CharField(max_length=50, choices=PROJECT_OUTLINK_TYPES)
    address         = models.TextField()
    date_added      = models.DateTimeField('date added', default = datetime.now())

class ProjectContact(models.Model):
    project         = models.ForeignKey(Project)
    type            = models.CharField(max_length=50, choices=PROJECT_CONTACT_TYPES)
    data            = models.TextField()
    date_added      = models.DateTimeField('date added', default = datetime.now())

class ProjectDependency(models.Model):
    depending_project   = models.ForeignKey(Project, related_name='depending') # the one that depends
    depended_project    = models.ForeignKey(Project, related_name='depended') # the one that is depended on
    brief               = models.TextField(null=True, blank=True)
    redonation_percent  = models.DecimalField(decimal_places=0, max_digits=2, null=True, blank=True)
    redonation_amount   = models.DecimalField(decimal_places=2, max_digits=6, null=True, blank=True)
    date_added          = models.DateTimeField('date added', default = datetime.now())

class ProjectOtherSource(models.Model):
    project       = models.ForeignKey(Project)
    title         = models.CharField(max_length=255)
    brief         = models.TextField(null=True, blank=True)
    amount        = models.DecimalField(decimal_places=2, max_digits=6, null=True, blank=True)
    is_monthly    = models.BooleanField(default=True)
    date_received = models.DateTimeField('date received')
    date_added    = models.DateTimeField('date added', default = datetime.now())
    is_public     = models.BooleanField(default=True)


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
