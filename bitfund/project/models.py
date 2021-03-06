from decimal import Decimal
from datetime import timedelta

from django.db import models
from django.contrib.auth.models import User
from django.utils.datetime_safe import datetime
from django.utils.timezone import utc, now
from django.db.models import Count, Sum

from bitfund.project.lists import *
from bitfund.core.settings_split.project import (CALCULATIONS_PRECISION,
                                                 BITFUND_OWN_PROJECT_ID,
                                                 PROJECTS_IN_HOMEPAGE_COLUMN,
                                                 MAX_PUBLIC_GOALS_PER_PROJECT,
                                                 PROJECTS_IN_DATES_BACK_TO_LOOK)


class ProjectCategory(models.Model):
    key           = models.CharField(max_length=80, unique=True)
    title         = models.CharField(max_length=255)
    description   = models.TextField(null=True, blank=True)
    logo          = models.ImageField(upload_to='project_category_logo/', null=True, blank=True)
    date_added    = models.DateTimeField('date added', default=now())

class Project(models.Model):
    maintainer = models.ForeignKey(User, default=-1, on_delete=models.PROTECT)
    key = models.CharField(max_length=80, unique=True)
    title = models.CharField(max_length=255)
    brief = models.CharField(max_length=255, null=True, blank=True)
    categories = models.ManyToManyField(ProjectCategory) #not used at the moment
    logo = models.CharField(max_length=255, null=True, blank=True)
    date_added = models.DateTimeField('date added', default=now())
    is_public = models.BooleanField(default=True)
    status = models.CharField(max_length=80, choices=PROJECT_STATUS_CHOICES, default=PROJECT_STATUS_CHOICES.unclaimed)
    is_refused_to_give_to_bitfund = models.BooleanField(default=False)
    maintainer_status = models.CharField(max_length=80, choices=PROJECT_USER_STATUS_CHOICES,
                                                    default=PROJECT_USER_STATUS_CHOICES.sole_developer,
                                                    null=True, blank=True)
    maintainer_reason_text = models.CharField(max_length=255, null=True, blank=True)
    maintainer_reason_url = models.TextField(null=True, blank=True)
    is_maintainer_confirmed = models.BooleanField(default=False)

    #total donations to this project (all successful pledge transactions sum)
    amount_pledged = models.DecimalField(decimal_places=2, max_digits=12, default=0)

    #total withdrawals of this project, all money withdrawn to projects bank account
    ## @TODO - add separate withdrawal transactions tracking
    amount_withdrawn = models.DecimalField(decimal_places=2, max_digits=12, default=0)

    #total redonations given to other projects (all successful redonation transcations sum where this is redonation_project)
    amount_redonation_given = models.DecimalField(decimal_places=2, max_digits=12, default=0)

    #total redonations received by the project (all successful redonation transcations sum where this is accepting_project)
    amount_redonation_received = models.DecimalField(decimal_places=2, max_digits=12, default=0)

    # total available balance ((amount_donated+amount_redonation_received) - (amount_withdrawn+amount_redonation_given))
    amount_balance = models.DecimalField(decimal_places=2, max_digits=12, default=0)



    def __unicode__(self):
        return self.title

    #gets a list of top funded projects
    @classmethod
    def getTopFundedProjects(cls):
        top_funded_list = (Project.objects
         .raw("""SELECT *,
              ( SELECT
                    SUM(transaction_amount)
                FROM
                    pledger_donationtransaction
                WHERE 1
                  AND transaction_type="pledge"
                  AND accepting_project_id=pp.id
                  AND transaction_status IN ('pending', 'unpaid', 'paid')
                  AND transaction_datetime BETWEEN STR_TO_DATE(%s, '%%Y-%%m-%%d 00:00:00') AND STR_TO_DATE(%s, '%%Y-%%m-%%d 00:00:00') )
                      AS pledged_recently,
              ( SELECT
                    SUM(amount)
                FROM
                    project_projectneed
                WHERE 1
                  AND is_public
                  AND project_id=pp.id
                  AND (date_starting IS NULL OR date_starting < NOW())
                  AND (date_ending IS NULL OR date_ending > NOW())
                  )
                      AS budget_this_month

              FROM
                    project_project AS pp
              WHERE
                    is_public
              HAVING pledged_recently > 0
              ORDER BY pledged_recently DESC
              LIMIT %s """,
              [(now() + timedelta(-PROJECTS_IN_DATES_BACK_TO_LOOK)).strftime('%Y-%m-%d 00:00:00'),
               now().strftime('%Y-%m-%d 00:00:00'),
               PROJECTS_IN_HOMEPAGE_COLUMN])
        )

        result_list = []

        for project in top_funded_list:
            if project.budget_this_month > 0:
                project.pledged_percent = Decimal(Decimal(project.pledged_recently) / Decimal(project.budget_this_month) * Decimal(100)).quantize(Decimal('0'))
            else:
                project.pledged_percent = -1
            result_list.append(project)


        return result_list

    #gets a list of top linked projects
    @classmethod
    def getTopLinkedProjects(cls):
        top_linked_list = (Project.objects
         .raw("""SELECT *,
              ( SELECT COUNT(*) FROM project_project_dependencies WHERE depender_project_id=pp.id ) AS depender_count,
              ( SELECT COUNT(*) FROM project_project_dependencies WHERE dependee_project_id=pp.id ) AS dependee_count
              FROM
                    project_project AS pp
              WHERE
                    is_public
              HAVING (depender_count > 0 OR dependee_count > 0)
              ORDER BY (depender_count+dependee_count) DESC
              LIMIT %s """,
              [PROJECTS_IN_HOMEPAGE_COLUMN])
        )

        result_list = []

        for project in top_linked_list:
            project.links_total = project.depender_count+project.dependee_count
            result_list.append(project)

        return result_list

    #gets a list of top linked projects
    @classmethod
    def getTopUnclaimedProjects(cls):
        top_unclaimed_list = (Project.objects
         .raw("""SELECT *,
              ( SELECT SUM(amount) FROM pledger_donationsubscription WHERE project_id=pp.id ) AS unclaimed_pledging_count
              FROM
                    project_project AS pp
              WHERE
                    is_public
                    AND status = 'unclaimed'
              HAVING unclaimed_pledging_count > 0
              ORDER BY unclaimed_pledging_count DESC
              LIMIT %s """,
              [PROJECTS_IN_HOMEPAGE_COLUMN])
        )
        return top_unclaimed_list

    #creates unique project key from the provided title
    @classmethod
    def slugifyKey(cls, title):
        from django.template.defaultfilters import slugify
        key = slugify(title)

        same_key_projects = Project.objects.filter(key__exact=key)
        index = 0
        while same_key_projects.count() > 0 :
            key = key+str(index)
            same_key_projects = Project.objects.filter(key__exact=key)
            index = index+1

        return key

    # calculates total backers count (goals backers included)
    def getTotalMonthlyBackers(self, monthdate=None):
        from bitfund.pledger.models import DonationTransaction, DONATION_TRANSACTION_TYPES_CHOICES, DONATION_TRANSACTION_STATUSES_CHOICES
            
        if monthdate is None:
            monthdate = now()
            
        return (DonationTransaction.objects
                                 .filter(accepting_project=self)
                                 .filter(transaction_type=DONATION_TRANSACTION_TYPES_CHOICES.pledge)
                                 .filter(transaction_datetime__gte=datetime(monthdate.year, monthdate.month, 1, tzinfo=monthdate.tzinfo))
                                 .exclude(transaction_status=DONATION_TRANSACTION_STATUSES_CHOICES.cancelled)
                                 .aggregate(Count('pledger_user', distinct=True))['pledger_user__count']
                                 )

    # calculates total donations from all sources accounting for the budget income (goals pledges excluded)
    def getTotalMonthlyDonations(self, monthdate=None):
        needs_total = 0
        needs, goals = self.getTotalMonthlyPledges(monthdate)
        needs_total = needs_total+needs
        needs, goals = self.getTotalMonthlyOtherSources(monthdate)
        needs_total = needs_total+needs
        needs_total = needs_total+self.getTotalMonthlyRedonations(monthdate)
        return needs_total

    # gets total monthly budget for project, i.e. sum of all active needs
    def getTotalMonthlyBudget(self, monthdate=None):
        if monthdate is None:
            monthdate = now()
            
        lasting = Decimal((ProjectNeed.objects
                              .filter(project_id=self.id)
                              .filter(is_public=True)
                              .filter(date_ending=None)
                              .aggregate(Sum('amount'))['amount__sum']
                              ) or 0)

        limited = Decimal((ProjectNeed.objects
                              .filter(project_id=self.id)
                              .filter(is_public=True)
                              .filter(date_starting__lte=datetime(monthdate.year, monthdate.month, 1, tzinfo=monthdate.tzinfo))
                              .filter(date_ending__gt=datetime(monthdate.year, monthdate.month+1, 1, tzinfo=monthdate.tzinfo))
                              .aggregate(Sum('amount'))['amount__sum']
                              ) or 0)
        return limited+lasting


    # gets total monthly transactions recorded sum by transaction type
    def getTotalMonthlyNeedsByType(self, transaction_type, monthdate=None):
        from bitfund.pledger.models import DonationTransaction, DONATION_TRANSACTION_STATUSES_CHOICES

        if monthdate is None:
            monthdate = now()

        donations_amount = (DonationTransaction.objects
                            .filter(accepting_project=self)
                            .filter(transaction_type=transaction_type)
                            .filter(transaction_datetime__gte=datetime(monthdate.year, monthdate.month, 1,
                                                                       tzinfo=monthdate.tzinfo))
                            .filter(transaction_datetime__lt=datetime(monthdate.year, monthdate.month + 1, 1,
                                                                      tzinfo=monthdate.tzinfo))
                            .exclude(transaction_status=DONATION_TRANSACTION_STATUSES_CHOICES.cancelled)
                            .exclude(transaction_status=DONATION_TRANSACTION_STATUSES_CHOICES.rejected)
                            .aggregate(Sum('transaction_amount'))['transaction_amount__sum']
                            ) or 0

        return Decimal(donations_amount).quantize(Decimal('0.01'))

    def getTotalMonthlyGoalsByType(self, transaction_type, monthdate=None):
        from bitfund.pledger.models import DonationTransaction, DONATION_TRANSACTION_STATUSES_CHOICES

        if monthdate is None:
            monthdate = now()

        pledges_history_sum = (DonationTransaction.objects
                               .filter(accepting_project=self)
                               .filter(transaction_type=transaction_type)
                               .filter(transaction_datetime__gte=datetime(monthdate.year, monthdate.month, 1,
                                                                          tzinfo=monthdate.tzinfo))
                               .filter(transaction_datetime__lt=datetime(monthdate.year, monthdate.month + 1, 1,
                                                                         tzinfo=monthdate.tzinfo))
                               .exclude(transaction_status=DONATION_TRANSACTION_STATUSES_CHOICES.cancelled)
                               .exclude(transaction_status=DONATION_TRANSACTION_STATUSES_CHOICES.rejected)
                               .aggregate(Sum('transaction_amount'))['transaction_amount__sum']
                               ) or 0

        return Decimal(pledges_history_sum).quantize(Decimal('0.01'))

    # gets total monthly pledges for all actual needs and goals, returned separately in a tuple
    def getTotalMonthlyPledges(self, monthdate=None):
        return self.getTotalMonthlyNeedsByType('pledge', monthdate), self.getTotalMonthlyGoalsByType('pledge', monthdate)

    # gets total monthly other sources for all actual needs and goals, returned separately in a tuple
    def getTotalMonthlyOtherSources(self, monthdate=None):
        return self.getTotalMonthlyNeedsByType('other_source', monthdate), self.getTotalMonthlyGoalsByType('other_source', monthdate)

    # calculates total redonations amount accounting for budget (redonations are not applied to onetime goals)
    def getTotalMonthlyRedonations(self, monthdate=None):
        return self.getTotalMonthlyNeedsByType('redonation', monthdate)

    # gets active needs count
    def getNeedsCount(self):
        from bitfund.project.models import ProjectNeed
        return ProjectNeed.objects.filter(project=self.id).filter(is_public=True).count()

    # gets active goals count
    def getGoalsCount(self):
        from bitfund.project.models import ProjectGoal
        return (ProjectGoal.objects.filter(project=self.id)
                                   .filter(is_public=True)
                                  .filter(date_ending__gt=now())
                                  .filter(date_ending__lt=datetime(now().year, now().month+1, 1, tzinfo=now().tzinfo))
                                  .filter(date_starting__lt=now())
                                  .count()
                                  )

    # adds UserGrateful entry if not grateful, removes entry if he is grateful alredy.
    def toggleGratefulUser(self, user):
        if ProjectGratefulUsers.objects.filter(project=self, user=user).count() > 0 :
            ProjectGratefulUsers.objects.filter(project=self, user=user).delete()
        else :
            grateful = ProjectGratefulUsers()
            grateful.project = self
            grateful.user = user
            grateful.save()

    # gets counf of all projects i_depend_on and depending_on_me, returns it separately as a tuple
    def getLinkedProjectsCount(self):
        return Project_Dependencies.objects.filter(depender_project=self).count(), \
               Project_Dependencies.objects.filter(dependee_project=self).count()

    # calculates total percent redonated to all linked projects. Includes fixed amount redonations, recalculated into
    # percent from current budget
    def getRedonationsPercent(self):
        total_redonation_percent = Decimal(0)
        project_budget = self.getTotalMonthlyBudget()
        if project_budget == 0 :
            return 0

        redonation_projects = Project_Dependencies.objects.filter(depender_project=self)
        for redonation_project in redonation_projects :
            if redonation_project.redonation_amount > 0 :
                total_redonation_percent = total_redonation_percent + ((Decimal(redonation_project.redonation_amount)*100) / Decimal(project_budget))
            elif redonation_project.redonation_percent > 0 :
                total_redonation_percent = total_redonation_percent + Decimal(redonation_project.redonation_percent)

        return total_redonation_percent

    # calculates maximum part of the budget still available for redonations, as percent and amount, returned separately in a tuple.
    def getMaxAvailableRedonationPercentandAmount(self):
        main_project_budget = self.getTotalMonthlyBudget()
        main_project_redonation_percent = self.getRedonationsPercent()

        free_percent = Decimal(Decimal(100)-main_project_redonation_percent).quantize(Decimal('0.01'))
        free_amount = Decimal(main_project_budget - ((main_project_budget/Decimal(100))*main_project_redonation_percent)).quantize(Decimal('0.01'))

        return free_percent, free_amount

    # calculates maximum part of the budget still available for redonations, as percent and amount, returned separately in a tuple.
    def checkProjectLinkedToBitFund(self):
        if (Project_Dependencies.objects
            .filter(dependee_project_id=BITFUND_OWN_PROJECT_ID, depender_project_id=self.id)
            .count()) > 0 :
            return True
        else :
            return False

class ProjectMaintainerVote(models.Model):
    project = models.ForeignKey(Project, on_delete=models.PROTECT)
    maintainer = models.ForeignKey(User, related_name='maintainer', on_delete=models.PROTECT)
    user = models.ForeignKey(User, related_name='user', on_delete=models.PROTECT)
    vote = models.BooleanField(default=True) #True means support, False - against
    comment = models.CharField(max_length=255, null=True, blank=True)
    date_voted = models.DateTimeField('date added', default=now())

class ProjectReport(models.Model):
    project = models.ForeignKey(Project, on_delete=models.PROTECT)
    reporter = models.ForeignKey(User, on_delete=models.PROTECT)
    comment = models.CharField(max_length=255, null=True, blank=True)
    date_reported = models.DateTimeField('date added', default=now())

class ProjectGratefulUsers(models.Model):
    project = models.ForeignKey(Project)
    user = models.ForeignKey(User)

class ProjectNeed(models.Model):
    project = models.ForeignKey(Project)
    key = models.CharField(max_length=80, blank=True)
    title = models.CharField(max_length=255, blank=True)
    brief = models.CharField(max_length=255, null=True, blank=True)
    amount = models.DecimalField(decimal_places=0, max_digits=12, default=0, blank=True)
    date_starting = models.DateTimeField('date starting', default=now(), null=True, blank=True)
    date_ending = models.DateTimeField('date ending', null=True, blank=True)
    date_added = models.DateTimeField('date added', default=now())
    is_public = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)

    class Meta:
        unique_together = (("project", "key"),)

    # calculates total donations for a need for given transaction_type and month
    def getMonthlyTotalByType(self, transaction_type, monthdate=None):
        from bitfund.pledger.models import DonationTransaction, DONATION_TRANSACTION_STATUSES_CHOICES

        if monthdate is None:
            monthdate = now()

        donation_transactions_sum = (DonationTransaction.objects
                                     .filter(accepting_project=self.project)
                                     .filter(accepting_need=self)
                                     .filter(transaction_type=transaction_type)
                                     .filter(transaction_datetime__gte=datetime(monthdate.year, monthdate.month, 1,
                                                                                tzinfo=monthdate.tzinfo))
                                     .filter(transaction_datetime__lt=datetime(monthdate.year, monthdate.month + 1, 1,
                                                                               tzinfo=monthdate.tzinfo))
                                     .exclude(transaction_status=DONATION_TRANSACTION_STATUSES_CHOICES.cancelled)
                                     .aggregate(Sum('transaction_amount'))['transaction_amount__sum']
                                    ) or 0

        return Decimal(donation_transactions_sum).quantize(Decimal('0.01'))


    def getPledgesMonthlyTotal(self, monthdate=None):
        return self.getMonthlyTotalByType('pledge', monthdate)

    def getOtherSourcesMonthlyTotal(self, monthdate=None):
        return self.getMonthlyTotalByType('other_source', monthdate)

    def getRedonationsMonthlyTotal(self, monthdate=None):
        return self.getMonthlyTotalByType('redonation', monthdate)

    # calculates amount of separate pledges transactions for a need for given month
    def getPledgesMonthlyCount(self, monthdate=None):
        from bitfund.pledger.models import DonationTransaction, DONATION_TRANSACTION_TYPES_CHOICES, DONATION_TRANSACTION_STATUSES_CHOICES

        if monthdate is None:
            monthdate = now()

        return (DonationTransaction.objects
                .filter(accepting_project=self.project)
                .filter(transaction_type=DONATION_TRANSACTION_TYPES_CHOICES.pledge)
                .filter(transaction_datetime__gte=datetime(monthdate.year, monthdate.month, 1,
                                                           tzinfo=monthdate.tzinfo))
                .filter(transaction_datetime__lt=datetime(monthdate.year, monthdate.month + 1, 1,
                                                          tzinfo=monthdate.tzinfo))
                .exclude(transaction_status=DONATION_TRANSACTION_STATUSES_CHOICES.cancelled)
                .count()
        )

class ProjectGoal(models.Model):
    project = models.ForeignKey(Project)
    key = models.CharField(max_length=80)
    title = models.CharField(max_length=255)
    brief = models.CharField(max_length=255, null=True, blank=True)
    text = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='project_goals/', null=True, blank=True)
    youtube_video_id = models.CharField(max_length=255, null=True, blank=True)
    vimeo_video_id = models.CharField(max_length=255, null=True, blank=True)
    amount = models.DecimalField(decimal_places=0, max_digits=12, default=0)
    date_starting = models.DateTimeField('date starting', null=True, blank=True)
    date_ending = models.DateTimeField('date ending', null=True, blank=True)
    date_added = models.DateTimeField('date added', default=now())
    is_public = models.BooleanField(default=True)
    do_redonations = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)

    def __unicode__(self):
        return self.title
    
    class Meta:
        unique_together = (("project", "key"),)

    #creates per project unique goal key from the provided goal title
    @classmethod
    def slugifyKey(cls, project_id, title):
        from django.template.defaultfilters import slugify
        key = slugify(title)

        same_key_projects = ProjectGoal.objects.filter(project_id=project_id).filter(key__exact=key)
        index = 0
        while same_key_projects.count() > 0 :
            key = key+str(index)
            same_key_projects = ProjectGoal.objects.filter(project_id=project_id).filter(key__exact=key)
            index = index+1

        return key

    #checks if the goal is allowed to go public
    def isValidForPublic(self):
        is_valid = True

        if self.title is None or self.title == '':
            is_valid = False

        if self.brief is None or self.brief == '':
            is_valid = False

        if self.text is None or self.text == '':
            is_valid = False

        if not self.amount > 0 :
            is_valid = False

        if self.image is None :
            is_valid = False

        if ((self.youtube_video_id is None or self.youtube_video_id == '')
            and (self.vimeo_video_id is None or self.vimeo_video_id == '')
            and (self.image is None or self.image == '')) :
            is_valid = False

        if self.date_ending is None :
            is_valid = False

        if self.date_starting is None :
            is_valid = False

        public_goals_count = ProjectGoal.objects.filter(project_id=self.project_id).filter(is_public=True).count()
        if public_goals_count >= MAX_PUBLIC_GOALS_PER_PROJECT :
            is_valid = False

        return is_valid

    # calculates total donations for a goal for given transaction_type4
    def getTotalByType(self, transaction_type):
        from bitfund.pledger.models import DonationTransaction, DONATION_TRANSACTION_STATUSES_CHOICES

        donation_transactions_sum = (DonationTransaction.objects
                                     .filter(accepting_project_id=self.project.id)
                                     .filter(accepting_goal_id=self.id)
                                     .filter(transaction_type=transaction_type)
                                     .exclude(transaction_status=DONATION_TRANSACTION_STATUSES_CHOICES.cancelled)
                                     .exclude(transaction_status=DONATION_TRANSACTION_STATUSES_CHOICES.rejected)
                                     .aggregate(Sum('transaction_amount'))['transaction_amount__sum']
                                    ) or 0

        return Decimal(donation_transactions_sum).quantize(Decimal('0.01'))
    
    def getTotalPledges(self):
        return self.getTotalByType('pledge')

    def getTotalOtherSources(self):
        return self.getTotalByType('other_sources')

    def getTotalRedonations(self):
        return self.getTotalByType('redonations')
    
class Project_Dependencies(models.Model):
    depender_project    = models.ForeignKey(Project, related_name='depender_project', default=0) # the one that depends on someone
    dependee_project    = models.ForeignKey(Project, related_name='dependee_project', default=0) # the one that someone is depended on
    brief               = models.TextField(null=True, blank=True)
    redonation_percent  = models.DecimalField(decimal_places=2, max_digits=6, null=True, blank=True)
    redonation_amount   = models.DecimalField(decimal_places=2, max_digits=6, null=True, blank=True)
    date_added          = models.DateTimeField('date added', default=now())
    sort_order          = models.IntegerField(default=0)


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

class ProjectWithdrawal(models.Model):
    project = models.ForeignKey(Project)
    amount_withdrawn = models.DecimalField(decimal_places=2, max_digits=12)
    amount_fees = models.DecimalField(decimal_places=2, max_digits=12)
    initiated_username = models.CharField(max_length=255)
    datetime_withdrawn = models.DateTimeField('date withdrawn', default=now())
    uri = models.CharField(max_length=255)

    def __unicode__(self):
        return self.title



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