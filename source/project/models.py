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
    
    @classmethod
    def getProjectActualNeedsGoalsOrderedList(self, project):
        return self.objects.raw("""
                        SELECT 
                                joined_list.* 
                        FROM 
                                ((SELECT 
                                        `id`,
                                        'need' AS 'type',
                                        `key`,
                                        `title`,
                                        `amount`,
                                        `sort_order`
                                 FROM
                                        project_projectneed 
                                 WHERE
                                        1
                                        AND project_id=%s
                                        AND is_public
                                ) 
                                        UNION
                                 (SELECT 
                                        `id`,
                                        'goal' AS 'type',
                                        `key`,
                                        `title`,
                                        `amount`,
                                        `sort_order`
                                 FROM
                                        project_projectgoal 
                                 WHERE
                                        1
                                        AND project_id=%s
                                        AND is_public
                                        AND NOW() BETWEEN date_starting AND date_ending
                                        AND date_ending <= LAST_DAY(NOW())
                                        )) AS joined_list       
                        ORDER BY
                            joined_list.sort_order
                                
                        """, [str(project.id), str(project.id)])
    

class ProjectNeed(models.Model):
    project       = models.ForeignKey(Project)
    key           = models.CharField(max_length=80)
    title         = models.CharField(max_length=255)
    description   = models.CharField(max_length=255, null=True, blank=True)
    amount        = models.DecimalField(decimal_places=0, max_digits=12, default=0)
    date_added    = models.DateTimeField('date added', default=datetime.now())
    is_public     = models.BooleanField(default=True)
    sort_order    = models.IntegerField(default=0)

class ProjectGoal(models.Model):
    project       = models.ForeignKey(Project)
    key           = models.CharField(max_length=80)
    title         = models.CharField(max_length=255)
    brief         = models.CharField(max_length=255)
    description   = models.TextField(null=True, blank=True)
    image         = models.ImageField(upload_to='project_goals/', null=True, blank=True)
    video_url     = models.CharField(max_length=255, null=True, blank=True)
    amount        = models.DecimalField(decimal_places=0, max_digits=12, default=0)
    date_ending   = models.DateTimeField('date ending')
    date_starting = models.DateTimeField('date starting', default=datetime.now())
    date_added    = models.DateTimeField('date added', default=datetime.now())
    is_public     = models.BooleanField(default=True)
    sort_order    = models.IntegerField(default=0)
    
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
    title           = models.CharField(max_length=50)
    address         = models.TextField()
    date_added      = models.DateTimeField('date added', default = datetime.now())
    is_public       = models.BooleanField(default=True)
    sort_order      = models.IntegerField(default=0)

class ProjectContact(models.Model):
    project         = models.ForeignKey(Project)
    type            = models.CharField(max_length=50, choices=PROJECT_CONTACT_TYPES)
    data            = models.TextField()
    date_added      = models.DateTimeField('date added', default = datetime.now())
    is_public       = models.BooleanField(default=True)
    sort_order      = models.IntegerField(default=0)

class Project_Dependencies(models.Model):
    idependon_project   = models.ForeignKey(Project, related_name='idependon') # the one that depends
    dependonme_project  = models.ForeignKey(Project, related_name='dependonme') # the one that is depended on
    brief               = models.TextField(null=True, blank=True)
    redonation_percent  = models.DecimalField(decimal_places=0, max_digits=2, null=True, blank=True)
    redonation_amount   = models.DecimalField(decimal_places=2, max_digits=6, null=True, blank=True)
    date_added          = models.DateTimeField('date added', default = datetime.now())
    is_public           = models.BooleanField(default=True)
    sort_order          = models.IntegerField(default=0)
    
    class Meta:
        unique_together = (("idependon_project", "dependonme_project"),)
    

class ProjectRelease(models.Model):
    project             = models.ForeignKey(Project) 
    version             = models.CharField(max_length=50, null=True, blank=True)
    title               = models.CharField(max_length=255, null=True, blank=True)
    brief               = models.TextField(null=True, blank=True)
    date_released       = models.DateTimeField('date released')
    previous_version    = models.ForeignKey('self', null=True, blank=True)
    date_added          = models.DateTimeField('date added', default = datetime.now())
    is_public           = models.BooleanField(default=True)

class ProjectOtherSource(models.Model):
    project         = models.ForeignKey(Project)
    title           = models.CharField(max_length=255)
    brief           = models.TextField(null=True, blank=True)
    amount_sum      = models.DecimalField(decimal_places=2, max_digits=6, null=True, blank=True)
    amount_percent  = models.DecimalField(decimal_places=0, max_digits=3, null=True, blank=True)
    is_monthly      = models.BooleanField(default=True)
    date_received   = models.DateTimeField('date received', null=True, blank=True)
    date_added      = models.DateTimeField('date added', default = datetime.now())
    is_public       = models.BooleanField(default=True)


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
