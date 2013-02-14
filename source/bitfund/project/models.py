import datetime

from django.db import models
from django.contrib.auth.models import User
from django.utils.datetime_safe import datetime
from django.utils.timezone import utc, now
from django.db.models import Count, Sum
from django.db.models.query_utils import select_related_descend

from bitfund.project.lists import *

class ProjectCategory(models.Model):
    key           = models.CharField(max_length=80, unique=True)
    title         = models.CharField(max_length=255)
    description   = models.TextField(null=True, blank=True)
    logo          = models.ImageField(upload_to='project_category_logo/', null=True, blank=True)
    date_added    = models.DateTimeField('date added', default=now())

class Project(models.Model):
    maintainer_id = models.ForeignKey(User)
    key           = models.CharField(max_length=80, unique=True)
    title         = models.CharField(max_length=255)
    brief         = models.CharField(max_length=255, null=True, blank=True)
    categories    = models.ManyToManyField(ProjectCategory)
    logo          = models.ImageField(upload_to='project_logo/', null=True, blank=True)
    date_added    = models.DateTimeField('date added', default=now())
    is_public     = models.BooleanField(default=True)
    status        = models.CharField(max_length=80, choices=PROJECT_STATUS_CHOICES)


    def __unicode__(self):
        return self.title

    #calculates total backers count (goals backers included)
    def getTotalMonthlyBackers(self, monthdate=None):
        import datetime
        from django.utils.timezone import now
        from django.db.models import Count, Sum 
        from bitfund.pledger.models import DonationTransaction
            
        if monthdate is None:
            monthdate = now()
            
        return (DonationTransaction.objects
                                 .filter(accepting_project=self)
                                 .filter(transaction_type=DONATION_TRANSACTION_TYPES_CHOICES.pledge)
                                 .filter(datetime_added__gte=datetime.datetime(monthdate.year, monthdate.month, 1, tzinfo=monthdate.tzinfo))
                                 .aggregate(Count('pledger_user', distinct=True))['pledger_user__count']
                                 )
        

    #calculates total donations from all sources accounting for the budget income (goals pledges excluded) 
    def getTotalMonthlyDonations(self, monthdate=None):
        return self.getPledgesMonthlyTotal(monthdate) + self.getOtherSourcesMonthlyTotal(monthdate) + self.getRedonationsMonthlyTotal(monthdate) 

    #calculates total project budget (goals excluded)  

    def getTotalMonthlyBudget(self, monthdate=None):
        import datetime
        from django.utils.timezone import now
        from django.db.models import Count, Sum 
        from bitfund.project.models import ProjectNeed
            
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

    def getTotalMonthlyNeedsByType(self, transaction_type, monthdate=None):
        import datetime
        from django.utils.timezone import now
        from django.db.models import Count, Sum 
        from bitfund.pledger.models import DonationTransaction, DonationTransactionNeeds

        if monthdate is None:
            monthdate = now()
            
        donation_histories = (DonationTransaction.objects
                                             .filter(accepting_project=self)
                                             .filter(transaction_type=transaction_type)
                                             .filter(datetime_added__gte=datetime.datetime(monthdate.year, monthdate.month, 1, tzinfo=monthdate.tzinfo))
                                             .filter(datetime_added__lt=datetime.datetime(monthdate.year, monthdate.month+1, 1, tzinfo=monthdate.tzinfo))
                                             .select_related(depth=1)
                            )
        
        return (DonationTransactionNeeds.objects.filter(donation_history__in=donation_histories).aggregate(Sum('amount'))['amount__sum']) or 0 

    def getTotalMonthlyGoalsByType(self, transaction_type, monthdate=None):
        import datetime
        from django.utils.timezone import now
        from django.db.models import Count, Sum 
        from bitfund.pledger.models import DonationTransaction, DonationTransactionGoals

        if monthdate is None:
            monthdate = now()
            
        donation_histories = (DonationTransaction.objects
                                             .filter(accepting_project=self)
                                             .filter(transaction_type=transaction_type)
                                             .filter(datetime_added__gte=datetime.datetime(monthdate.year, monthdate.month, 1, tzinfo=monthdate.tzinfo))
                                             .filter(datetime_added__lt=datetime.datetime(monthdate.year, monthdate.month+1, 1, tzinfo=monthdate.tzinfo))
                                             .select_related(depth=1))    
        
        return (DonationTransactionGoals.objects.filter(donation_history__in=donation_histories).aggregate(Sum('amount'))['amount__sum']) or 0

    def getTotalMonthlyPledges(self, monthdate=None):
        return self.getTotalMonthlyNeedsByType('pledge', monthdate), self.getTotalMonthlyGoalsByType('pledge', monthdate)

    def getTotalMonthlyOtherSources(self, monthdate=None):
        return self.getTotalMonthlyNeedsByType('other_source', monthdate), self.getTotalMonthlyGoalsByType('other_source', monthdate)

    #calculates total redonations amount accounting for budget and goals, returned separately
    def getTotalMonthlyRedonations(self, monthdate=None):
        return self.getTotalMonthlyNeedsByType('redonation', monthdate), self.getTotalMonthlyGoalsByType('redonation', monthdate)
        
    def getNeedsCount(self):
        from bitfund.project.models import ProjectNeed
        return ProjectNeed.objects.filter(project=self.id).filter(is_public=True).count()
        
    def getGoalsCount(self):
        import datetime
        from django.utils.timezone import utc, now
        from bitfund.project.models import ProjectGoal
        return (ProjectGoal.objects.filter(project=self.id)
                                   .filter(is_public=True)
                                  .filter(date_ending__gt=now())
                                  .filter(date_ending__lt=datetime.datetime(now().year, now().month+1, 1, tzinfo=now().tzinfo))
                                  .filter(date_starting__lt=now())
                                  .count()
                                  )
    
    def userEditAccess(self, user):
        from bitfund.project.models import ProjectUserRole
        
        return (user.is_authenticated() and ProjectUserRole.objects.filter(project=self).filter(profile=user.id).filter(user_role__in=['treasurer', 'maintainer']).count() > 0)

    def toggleGratefulUser(self, user):
        if ProjectGratefulUsers.objects.filter(project=self, user=user).count() > 0 :
            ProjectGratefulUsers.objects.filter(project=self, user=user).delete()
        else :
            grateful = ProjectGratefulUsers()
            grateful.project = self
            grateful.user = user
            grateful.save()



class ProjectGratefulUsers(models.Model):
    project = models.ForeignKey(Project)
    user = models.ForeignKey(User)

class ProjectNeed(models.Model):
    project = models.ForeignKey(Project)
    key = models.CharField(max_length=80)
    title = models.CharField(max_length=255)
    brief = models.CharField(max_length=255, null=True, blank=True)
    amount = models.DecimalField(decimal_places=0, max_digits=12, default=0)
    date_starting = models.DateTimeField('date starting', default=now(), null=True, blank=True)
    date_ending = models.DateTimeField('date ending', null=True, blank=True)
    date_added = models.DateTimeField('date added', default=now())
    is_public = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)

    def __unicode__(self):
        return self.title
    
    class Meta:
        unique_together = (("project", "key"),)


    def getMonthlyTotalByType(self, transaction_type, monthdate=None):
        import datetime
        from django.utils.timezone import now
        from django.db.models import Sum 
        from bitfund.pledger.models import DonationTransaction, DonationTransactionNeeds

        if monthdate is None:
            monthdate = now()
        
        donation_transactions = (DonationTransaction.objects
                                             .filter(accepting_project=self.project)
                                             .filter(transaction_type=transaction_type)
                                             .filter(datetime_added__gte=datetime.datetime(monthdate.year, monthdate.month, 1, tzinfo=monthdate.tzinfo))
                                             .filter(datetime_added__lt=datetime.datetime(monthdate.year, monthdate.month+1, 1, tzinfo=monthdate.tzinfo))
                                             .select_related(depth=1)
                                             )    
        
        return (DonationTransactionNeeds.objects
                                    .filter(need=self)
                                    .filter(donation_history__in=donation_transactions)
                                    .aggregate(Sum('amount'))['amount__sum']) or 0 


    def getPledgesMonthlyTotal(self, monthdate=None):
        return self.getMonthlyTotalByType('pledge', monthdate)

    def getOtherSourcesMonthlyTotal(self, monthdate=None):
        return self.getMonthlyTotalByType('other_source', monthdate)

    def getRedonationsMonthlyTotal(self, monthdate=None):
        return self.getMonthlyTotalByType('redonation', monthdate)

    def getPledgesMonthlyCount(self, monthdate=None):
        import datetime
        from django.utils.timezone import now
        from django.db.models import Sum 
        from bitfund.pledger.models import DonationTransaction, DonationTransactionNeeds

        if monthdate is None:
            monthdate = now()

        donation_transactions = (DonationTransaction.objects
                                             .filter(accepting_project=self.project)
                                             .filter(transaction_type=DONATION_TRANSACTION_TYPES_CHOICES.pledge)
                                             .filter(datetime_added__gte=datetime.datetime(monthdate.year, monthdate.month, 1, tzinfo=monthdate.tzinfo))
                                             .filter(datetime_added__lt=datetime.datetime(monthdate.year, monthdate.month+1, 1, tzinfo=monthdate.tzinfo))
                                             .select_related(depth=1)
                                             )    
        
        return (DonationTransactionNeeds.objects
                                    .filter(need=self)
                                    .filter(donation_history__in=donation_transactions)
                                    .count()) 


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

    def getTotalByType(self, transaction_type):
        from django.db.models import Sum 
        from bitfund.pledger.models import DonationTransaction, DonationTransactionGoals

        donation_histories = (DonationTransaction.objects
                                             .filter(accepting_project=self.project)
                                             .filter(transaction_type=transaction_type)
                                             .filter(datetime_added__gte=datetime.datetime(monthdate.year, monthdate.month, 1, tzinfo=monthdate.tzinfo))
                                             .filter(datetime_added__lt=datetime.datetime(monthdate.year, monthdate.month+1, 1, tzinfo=monthdate.tzinfo))
                                             .select_related(depth=1)
                                             )    
        
        return (DonationTransactionGoals.objects
                                    .filter(goal=self)
                                    .filter(donation_history__in=donation_histories)
                                    .aggregate(Sum('amount'))['amount__sum']) or 0 
    
    def getTotalPledges(self):
        return self.getTotalByType('pledge')

    def getTotalOtherSources(self):
        return self.getTotalByType('other_sources')

    def getTotalRedonations(self):
        return self.getTotalByType('redonations')
    
class Project_Dependencies(models.Model):
    depender_project   = models.ForeignKey(Project, related_name='depender') # the one that depends
    dependee_project  = models.ForeignKey(Project, related_name='dependee') # the one that is depended on
    brief               = models.TextField(null=True, blank=True)
    redonation_percent  = models.DecimalField(decimal_places=0, max_digits=2, null=True, blank=True)
    redonation_amount   = models.DecimalField(decimal_places=2, max_digits=6, null=True, blank=True)
    date_added          = models.DateTimeField('date added', default=now())
    is_public           = models.BooleanField(default=True)
    sort_order          = models.IntegerField(default=0)
    
    class Meta:
        unique_together = (("depender_project", "dependee_project"),)


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

"""
# I doubt this will ever be used, but let it stay here for now
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
"""


"""
#commented out until full implementation
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
"""

"""
#commented out until full implementation
class Project_DependandsDonations_Shares(models.Model):
    project_need    = models.ForeignKey(ProjectNeed, null=True, blank=True)
    project_goal    = models.ForeignKey(ProjectGoal, null=True, blank=True)
    brief           = models.CharField(max_length=255, null=True, blank=True)
    amount_sum      = models.DecimalField(decimal_places=2, max_digits=6, null=True, blank=True)
    amount_percent  = models.DecimalField(decimal_places=0, max_digits=3, null=True, blank=True)
    is_monthly      = models.BooleanField(default=True)
    date_added      = models.DateTimeField('date added', default=now())

    class Meta:
        unique_together = (("project_need", "project_goal"),)
"""

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

    "Traceback (most recent call last):\n\n


}

"""


