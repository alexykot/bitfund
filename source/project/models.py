import datetime

from django.db import models
from django.contrib.auth.models import User
from django.utils.datetime_safe import datetime
from django.utils.timezone import utc, now
from django.db.models import Count, Sum 

from project.lists import * 

class ProjectCategory(models.Model):
    key           = models.CharField(max_length=80, unique=True)
    title         = models.CharField(max_length=255)
    description   = models.TextField(null=True, blank=True)
    logo          = models.ImageField(upload_to='project_category_logo/', null=True, blank=True)
    date_added    = models.DateTimeField('date added', default=now())

class Project(models.Model):
    key           = models.CharField(max_length=80, unique=True)
    title         = models.CharField(max_length=255)
    brief         = models.CharField(max_length=255, null=True, blank=True)
    categories    = models.ManyToManyField(ProjectCategory)
    logo          = models.ImageField(upload_to='project_logo/', null=True, blank=True)
    date_added    = models.DateTimeField('date added', default=now())
    is_public     = models.BooleanField(default=True)
    
    def __unicode__(self):
        return self.title

    #calculates total project budget for given month or current month by default  
    def getTotalMonthlyBudget(self, monthdate=None):
        import datetime
        from django.utils.timezone import now
        from django.db.models import Count, Sum 
        from project.models import ProjectNeed 
            
        if monthdate is None:
            monthdate = now()
            
        lasting = (ProjectNeed.objects
                              .filter(project=self.id)
                              .filter(is_public=True)
                              .filter(date_ending=None)
                              .aggregate(Sum('amount'))['amount__sum']
                              ) or 0
        limited = (ProjectNeed.objects
                              .filter(project=self.id)
                              .filter(is_public=True)
                              .filter(date_starting__lte=datetime.datetime(monthdate.year, monthdate.month, 1, tzinfo=monthdate.tzinfo))
                              .filter(date_ending__gt=datetime.datetime(monthdate.year, monthdate.month+1, 1, tzinfo=monthdate.tzinfo))
                              .aggregate(Sum('amount'))['amount__sum']
                              ) or 0
                               
        return limited+lasting
    
    #calculates total backers amountfor given month or current month by default
    def getTotalMonthlyBackers(self, monthdate=None):
        import datetime
        from django.utils.timezone import now
        from django.db.models import Count, Sum 
        from pledger.models import DonationHistory 
            
        if monthdate is None:
            monthdate = now()
            
        return (DonationHistory.objects
                                 .filter(project=self)
                                 .filter(datetime_sent__gte=datetime.datetime(monthdate.year, monthdate.month, 1, tzinfo=monthdate.tzinfo))
                                 .aggregate(Count('user', distinct=True))['user__count']
                                 )
        
        
    #calculates total budget donations amount for given month or current month by default
    def getTotalMonthlyNeedsDonations(self, monthdate=None):
        import datetime
        from django.utils.timezone import now
        from django.db.models import Count, Sum 
        from pledger.models import DonationHistory, DonationHistoryNeeds 

        if monthdate is None:
            monthdate = now()
            
        donation_histories = (DonationHistory.objects
                                             .filter(project=self)
                                             .filter(datetime_sent__lte=now())
                                             .filter(datetime_sent__gte=datetime.datetime(monthdate.year, monthdate.month, 1, tzinfo=monthdate.tzinfo))
                                             .select_related('donationhistoryneeds'))    
        
        donations_sum = (DonationHistoryNeeds.objects
                                    .filter(donation_history__in=donation_histories)
                                    .aggregate(Sum('amount'))['amount__sum']) 
        if (donations_sum > 0) :
            return donations_sum
        else :
            return 0
        
    def getTotalMonthlyGoalsDonations(self, monthdate=None):
        import datetime
        from django.db.models import Count, Sum
        from django.utils.timezone import utc, now 
        from pledger.models import DonationHistory, DonationHistoryGoals 
        

        if monthdate is None:
            monthdate = now()

        donation_histories = (DonationHistory.objects
                                             .filter(project=self)
                                             .filter(datetime_sent__gte=datetime.datetime(monthdate.year, monthdate.month, 1, tzinfo=monthdate.tzinfo) )
                                             .select_related('donationhistoryneeds'))    
        
        return ((DonationHistoryGoals.objects
                                    .filter(donation_history__in=donation_histories)
                                    .aggregate(Sum('amount'))['amount__sum']) or 0)
        
    #calculates total other sources amount for given month or current month by default
    def getTotalMonthlyOtherSources(self, monthdate=now()):
        import datetime
        from django.utils.timezone import utc, now
        from django.db.models import Sum 
        from project.models import ProjectNeed, ProjectOtherSource
        
        project_other_sources_monthly = (ProjectOtherSource.objects.filter(project=self)
                                                                   .filter(is_public=True)
                                                                   .filter(is_monthly=True)
                                                                   .aggregate(Sum('amount'))['amount__sum']
                                                                   ) or 0 
        project_other_sources_onetime = (ProjectOtherSource.objects.filter(project=self)
                                                                   .filter(is_public=True)
                                                                   .filter(is_monthly=False)
                                                                   .filter(date_received__gte=datetime.datetime(now().year, now().month, 1, tzinfo=now().tzinfo))
                                                                   .filter(date_received__lt=datetime.datetime(now().year, now().month+1, 1, tzinfo=now().tzinfo))
                                                                   .aggregate(Sum('amount'))['amount__sum']
                                                                   ) or 0
        
        return project_other_sources_monthly + project_other_sources_onetime

    def getTotalMonthlyDependantsDonations(self, monthdate=now()):
        import datetime
        from django.utils.timezone import utc, now
        from django.db.models import Sum 
        from project.models import Project_Dependencies

        
        dependants_donations_percent_sum  = 0 
        dependants_donations_percent_list = (Project_Dependencies.objects.filter(dependonme_project=self)
                                                                         .filter(is_public=True)
                                                                         .filter(redonation_percent__gt=0)
                                                                          )
        
        for dependants_donation in dependants_donations_percent_list :
            dependants_project               = Project.objects.get(project=dependants_donation.idependon_project)
            dependants_donations_percent_sum = dependants_donations_percent_sum + (dependants_project/100)*dependants_donation.redonation_percent 
             
        
        dependants_donations_amount_sum = (Project_Dependencies.objects.filter(dependonme_project=self)
                                                                       .filter(is_public=True)
                                                                       .filter(redonation_amount__gt=0)
                                                                       .aggregate(Sum('redonation_amount'))['redonation_amount__sum']
                                                                        ) or 0
         
        
        return dependants_donations_amount_sum + dependants_donations_percent_sum
        
    def getNeedsCount(self):
        from project.models import ProjectNeed
        return ProjectNeed.objects.filter(project=self.id).filter(is_public=True).count()
        
    def getGoalsCount(self):
        import datetime
        from django.utils.timezone import utc, now
        from project.models import ProjectGoal
        return (ProjectGoal.objects.filter(project=self.id)
                                  .filter(is_public=True)
                                  .filter(date_ending__gt=now())
                                  .filter(date_ending__lt=datetime.datetime(now().year, now().month+1, 1, tzinfo=now().tzinfo))
                                  .filter(date_starting__lt=now())
                                  .count()
                                  )
    
    def userEditAccess(self, user):
        from project.models import ProjectUserRole
        
        return (user.is_authenticated() and ProjectUserRole.objects.filter(project=self).filter(profile=user.id).filter(user_role__in=['treasurer', 'maintainer']).count() > 0)

class ProjectNeed(models.Model):
    project       = models.ForeignKey(Project)
    key           = models.CharField(max_length=80)
    title         = models.CharField(max_length=255)
    brief         = models.CharField(max_length=255, null=True, blank=True)
    amount        = models.DecimalField(decimal_places=0, max_digits=12, default=0)
    date_starting = models.DateTimeField('date starting', default=now(), null=True, blank=True)
    date_ending   = models.DateTimeField('date ending', null=True, blank=True)
    date_added    = models.DateTimeField('date added', default=now())
    is_public     = models.BooleanField(default=True)
    sort_order    = models.IntegerField(default=0)

    def __unicode__(self):
        return self.title
    
    class Meta:
        unique_together = (("project", "key"),)

class ProjectGoal(models.Model):
    project       = models.ForeignKey(Project)
    key           = models.CharField(max_length=80)
    title         = models.CharField(max_length=255)
    brief         = models.CharField(max_length=255)
    short_text    = models.TextField(null=True, blank=True)
    long_text     = models.TextField(null=True, blank=True)
    image         = models.ImageField(upload_to='project_goals/', null=True, blank=True)
    video_url     = models.CharField(max_length=255, null=True, blank=True)
    amount        = models.DecimalField(decimal_places=0, max_digits=12, default=0)
    date_starting = models.DateTimeField('date starting', default=now())
    date_ending   = models.DateTimeField('date ending')
    date_added    = models.DateTimeField('date added', default=now())
    is_public     = models.BooleanField(default=True)
    sort_order    = models.IntegerField(default=0)

    def __unicode__(self):
        return self.title
    
    class Meta:
        unique_together = (("project", "key"),)
    
class ProjectUserRole(models.Model):
    from pledger.models import Profile

    profile         = models.ForeignKey(Profile)
    project         = models.ForeignKey(Project)
    user_role       = models.CharField(max_length=10, choices=PROJECT_USER_ROLES, null=True, blank=True)
    user_role_title = models.CharField(max_length=255, null=True, blank=True)
    sort_order      = models.IntegerField(default=0)
    date_added      = models.DateTimeField('date added', default=now())

    def __unicode__(self):
        return self.user_role_title

class ProjectOutlink(models.Model):
    project         = models.ForeignKey(Project)
    type            = models.CharField(max_length=50, choices=PROJECT_OUTLINK_TYPES)
    title           = models.CharField(max_length=50)
    address         = models.TextField()
    date_added      = models.DateTimeField('date added', default=now())
    is_public       = models.BooleanField(default=True)
    sort_order      = models.IntegerField(default=0)

    def __unicode__(self):
        return self.project.title

class Project_Dependencies(models.Model):
    idependon_project   = models.ForeignKey(Project, related_name='idependon') # the one that depends
    dependonme_project  = models.ForeignKey(Project, related_name='dependonme') # the one that is depended on
    brief               = models.TextField(null=True, blank=True)
    redonation_percent  = models.DecimalField(decimal_places=0, max_digits=2, null=True, blank=True)
    redonation_amount   = models.DecimalField(decimal_places=2, max_digits=6, null=True, blank=True)
    date_added          = models.DateTimeField('date added', default=now())
    is_public           = models.BooleanField(default=True)
    sort_order          = models.IntegerField(default=0)
    
    class Meta:
        unique_together = (("idependon_project", "dependonme_project"),)
    

class ProjectOtherSource(models.Model):
    project         = models.ForeignKey(Project)
    title           = models.CharField(max_length=255)
    brief           = models.TextField(null=True, blank=True)
    amount          = models.DecimalField(decimal_places=2, max_digits=6, null=True, blank=True)
    is_monthly      = models.BooleanField(default=True)
    date_received   = models.DateTimeField('date received', null=True, blank=True)
    date_added      = models.DateTimeField('date added', default=now())
    is_public       = models.BooleanField(default=True)

    def __unicode__(self):
        return self.title

class Project_OtherSource_Shares(models.Model):
    project_need    = models.ForeignKey(ProjectNeed, null=True, blank=True)
    project_goal    = models.ForeignKey(ProjectGoal, null=True, blank=True)
    other_source    = models.ForeignKey(ProjectOtherSource)
    brief           = models.CharField(max_length=255, null=True, blank=True)
    amount_sum      = models.DecimalField(decimal_places=2, max_digits=6, null=True, blank=True)
    amount_percent  = models.DecimalField(decimal_places=0, max_digits=3, null=True, blank=True)
    is_monthly      = models.BooleanField(default=True)
    date_added      = models.DateTimeField('date added', default=now())

    class Meta:
        unique_together = (("project_need", "project_goal", "other_source"),)

class Project_DependandsDonations_Shares(models.Model):
    project_need    = models.ForeignKey(ProjectNeed, null=True, blank=True)
    project_goal    = models.ForeignKey(ProjectGoal, null=True, blank=True)
    brief           = models.CharField(max_length=255, null=True, blank=True)
    amount_sum      = models.DecimalField(decimal_places=2, max_digits=6, null=True, blank=True)
    amount_percent  = models.DecimalField(decimal_places=0, max_digits=3, null=True, blank=True)
    is_monthly      = models.BooleanField(default=True)
    date_added      = models.DateTimeField('date added', default=now())



"""
#timeline is not going to be implemented now. but I'll leave it here, just in case some day it will be needed again.
class ProjectEvent(models.Model):
    EVENT_BRANCHES = (
        ('sources', u'Sources'),
        ('social', u'Social'),
        ('releases', u'Releases'),
        ('finances', u'Finances'),
    )
    EVENT_TYPES = (
        (u'Sources', (
            ('commit',            u'Commit'),
            ('pull_request',      u'Pull request'),
            ('new_branch',        u'New branch'),
         )),
        (u'Social', ( 
            ('blog_entry',        u'Blog'),
            ('team_update',       u'Team update'),
            ('community_update',  u'Community update'),
         )), 
        (u'Releases', ( 
            ('major_release',     u'Major Release'),
            ('minor_release',     u'Minor Release'),
            ('release_announce',  u'Release Announce'),
         )), 
        (u'Finances', ( 
            ('goal_added',        u'Goal Added'),
            ('goal_updated',      u'Goal Updated'),
            ('goal_removed',      u'Goal Removed'),
            ('goal_plan',         u'Goal Plan'),
            ('goal_success',      u'Goal Success'),
            ('goal_fail',         u'Goal Fail'),
            ('need_added',        u'Need Added'),
            ('need_updated',      u'Need Updated'),
            ('need_removed',      u'Need Removed'),
            ('need_plan',         u'Need Plan'),
            ('need_success',      u'Need Success'),
            ('need_fail',         u'Need Fail'),
            ('other_added',       u'Other Source Added'),
            ('other_updated',     u'Other Source Updated'),
            ('other_removed',     u'Other Source Removed'),
            ('other_plan',        u'Other Source Plan'),
            ('other_success',     u'Other Source Success'),
            ('other_fail',        u'Other Source Fail'),
         )), 
    )
    project         = models.ForeignKey(Project)
    branch          = models.CharField(max_length=10, choices=EVENT_BRANCHES)
    type            = models.CharField(max_length=10, choices=EVENT_TYPES)
    title           = models.CharField(max_length=255)
    text            = models.TextField(null=True, blank=True)
    date_published  = models.DateTimeField('date published', default=now(), null=True, blank=True)
    date_added      = models.DateTimeField('date added', default=now())
    is_public       = models.BooleanField(default=True)
"""    

