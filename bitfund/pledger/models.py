from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from django.db.models import Count, Sum
from django.shortcuts import get_object_or_404

from model_utils import Choices

from bitfund.project.models import *

DONATION_TRANSACTION_TYPES_CHOICES = Choices(
    ('pledge', u'Pledge'), # onetime or monthly pledge by the user
    ('other_source', u'Other Source'), # income from other source, stated by the project maintainers
    ('redonation', u'Redonation'), # redonation from a pledge on a depended project
)

DONATION_TRANSACTION_STATUSES_CHOICES = Choices(
    ('pending', u'Pending, Unpaid'), # transaction for the monthly pledge for current month, month end not reached yet, not processed through payment yet
    ('unpaid', u'Confirmed, Unpaid'), # trasaction for the monthly pledge when month end reached, or from onetime pledge at any time, not processed through payment yet
    ('paid', u'Paid'), # trasaction already processed through payment successfully
    ('rejected', u'Rejected'), # trasaction rejected by the payment processor
    ('cancelled', u'Cancelled'), # trasaction cancelled by the issuer
)

USER_PROJECT_STATUS_CHOICES = Choices(
    ('sole_developer', u'Sole Developer'),
    ('benevolent_dictator', u'Benevolent Dictator'),
    ('foundation', u'Foundation'),
    ('community_ambassador', u'Community Ambassador'),
)

class Profile(User):
    user = models.OneToOneField(User, unique=True, verbose_name=_('user'), related_name='my_profile')
    api_token = models.CharField(max_length=255, unique=True)
    donation_is_public = models.BooleanField(default=True)
    status_in_project = models.CharField(max_length=80, choices=USER_PROJECT_STATUS_CHOICES,
                                         default=USER_PROJECT_STATUS_CHOICES.sole_developer)

    # calculates total donations from this user to certain project
    def getTotalDonationsByProject(self, project):
        user_project_donations_sum = (DonationTransaction.objects
                                      .filter(user=self.user, accepting_project=project)
                                      .aggregate(Sum('transaction_amount'))['transaction_amount__sum']) or 0

        return Decimal(user_project_donations_sum).quantize(Decimal('0.01'))


#donations cart, storing donations data until confirmed 
class DonationCart(models.Model):
    user                = models.ForeignKey(User)
    project             = models.ForeignKey(Project)
    datetime_added      = models.DateTimeField('date added', default=now())
    needs               = models.ManyToManyField(ProjectNeed, through='DonationCartNeeds')
    goals               = models.ManyToManyField(ProjectGoal, through='DonationCartGoals')

    def getProjectSupportTotal(self):
        return self.getProjectSupportNeedsTotal()+self.getProjectSupportGoalsTotal() 

    def getProjectSupportNeedsTotal(self):
        needs_support_total = DonationCartNeeds.objects.filter(donation_cart=self).aggregate(Sum('amount'))['amount__sum']
        if not needs_support_total:
            needs_support_total = 0
        return needs_support_total 

    def getProjectSupportGoalsTotal(self):
        goals_support_total = DonationCartGoals.objects.filter(donation_cart=self).aggregate(Sum('amount'))['amount__sum']
        if not goals_support_total:
            goals_support_total = 0
        
        return goals_support_total 

    def getProjectSupportCount(self):
        return self.getProjectSupportNeedsCount()+self.getProjectSupportGoalsCount() 

    def getProjectSupportNeedsCount(self):
        needs_support_count = DonationCartNeeds.objects.filter(donation_cart=self).aggregate(Count('id'))['id__count']
        if not needs_support_count:
            needs_support_count = 0

        return needs_support_count 
    
    def getProjectSupportGoalsCount(self):
        goals_support_count = DonationCartGoals.objects.filter(donation_cart=self).aggregate(Count('id'))['id__count']
        if not goals_support_count:
            goals_support_count = 0
        
        return goals_support_count 

    
    #updates donation from one user to a certain project to increase/decrease all it's needs&goals shares proportionally 
    @staticmethod
    def adjustProjectDonationProportionally(donation_cart_id, new_project_donation_amount, old_project_donation_amount = False):
        if not old_project_donation_amount :
            donation = get_object_or_404(DonationCart, donation_cart_id)
            old_project_donation_amount = donation.getProjectSupportTotal() 
             
        donation_needs    = DonationCartNeeds.objects.filter(donation_cart=donation_cart_id)
        donation_goals    = DonationCartGoals.objects.filter(donation_cart=donation_cart_id)
        
        for donation_need in donation_needs:
            old_donation_amount = donation_need.amount
            donation_percentage = old_donation_amount*100/old_project_donation_amount
            new_donation_amount = new_project_donation_amount*donation_percentage/100
            donation_need.amount = new_donation_amount
            donation_need.save() 
        
        for donation_goal in donation_goals:
            old_donation_amount = donation_goal.amount
            donation_percentage = old_donation_amount*100/old_project_donation_amount
            new_donation_amount = new_project_donation_amount*donation_percentage/100
            donation_goal.amount = new_donation_amount
            donation_goal.save() 
        
    #updates all donations for a certain user to increase/decrease all project donations proportionally 
    @staticmethod
    def adjustTotalDonationProportionally(user_id, new_total_donations_amount):
        projects_donations_totals = {}
        donations = DonationCart.objects.filter(user=user_id)
        old_total_donations_amount = 0
        for donation in donations :
            projects_donations_totals[donation.project.id] = donation.getProjectSupportTotal()
            old_total_donations_amount = old_total_donations_amount + projects_donations_totals[donation.project.id]  

        for donation in donations :
            old_project_donation_amount = projects_donations_totals[donation.project.id]
            donation_percentage = old_project_donation_amount*100/old_total_donations_amount
            new_project_donation_amount = new_total_donations_amount/100*donation_percentage 
            DonationCart.adjustProjectDonationProportionally(donation.id, new_project_donation_amount, old_project_donation_amount)
    
    # for "monthly" it also counts active subscriptions as part of projects supported count
    @staticmethod
    def getProjectsSupportedCount(user, donation_type):
        from django.db import connection
        if donation_type == 'onetime' :
            cursor = connection.cursor() 
            cursor.execute("""
                            SELECT 
                                    COUNT(DISTINCT pledger_donationcart.project_id) as project__count 
                            FROM 
                                    pledger_donationcart 
                                        LEFT JOIN 
                                    pledger_donationcartneeds
                                        ON pledger_donationcartneeds.donation_cart_id = pledger_donationcart.id 
                                        LEFT JOIN 
                                    pledger_donationcartgoals
                                        ON pledger_donationcartgoals.donation_cart_id = pledger_donationcart.id 
                            WHERE    1
                                    AND pledger_donationcart.user_id=%s 
                                    AND (
                                        (pledger_donationcartneeds.id AND pledger_donationcartneeds.donation_type='onetime')
                                        OR 
                                        pledger_donationcartgoals.id
                                        )
                            """, [str(user.id)])
            row = cursor.fetchone()
            if row[0] :
                projects_count = int(row[0])
            else : 
                projects_count = 0
        elif donation_type == 'monthly' :
            cursor = connection.cursor()
            cursor.execute("""
                            SELECT 
                                    COUNT(DISTINCT total_projects.project_id) as project__count 
                            FROM    
                                    ( 
                                     (
                                        SELECT 
                                                DISTINCT project_id  
                                        FROM
                                                pledger_donationcart 
                                                    LEFT JOIN 
                                                pledger_donationcartneeds
                                                    ON pledger_donationcartneeds.donation_cart_id = pledger_donationcart.id 
                                        WHERE
                                                1
                                                AND pledger_donationcart.user_id=%s
                                                AND (pledger_donationcartneeds.id AND pledger_donationcartneeds.donation_type='monthly')
                                     ) UNION (
                                        SELECT 
                                                DISTINCT project_id  
                                        FROM
                                                pledger_donationsubscription 
                                        WHERE
                                                1
                                                AND user_id=%s
                                                AND active
                                     ) 
                                    ) AS total_projects 
                                        
                            """, [str(user.id), str(user.id)])
            row = cursor.fetchone()
            if row[0] :
                projects_count = int(row[0])
            else : 
                projects_count = 0
        return projects_count
    
    # for "monthly" it also counts active subscriptions as part of projects supported total
    @staticmethod
    def getProjectsSupportedTotal(user, donation_type):
        from django.db import connection
        if donation_type == 'onetime' :
            cursor = connection.cursor()
            cursor.execute("""
                            SELECT 
                                    SUM(pdn.amount) as project__sum 
                            FROM 
                                    pledger_donationcart AS pd
                                        INNER JOIN 
                                    pledger_donationcartneeds AS pdn
                                        ON pdn.donation_cart_id = pd.id 
                            WHERE    1
                                    AND pd.user_id=%s
                                    AND pdn.donation_type='onetime'
                            """, [str(user.id)]) 
            row_a = cursor.fetchone()
            cursor.execute("""
                            SELECT 
                                    SUM(pdg.amount) as project__sum 
                            FROM 
                                    pledger_donationcart AS pd 
                                        LEFT JOIN 
                                    pledger_donationcartgoals AS pdg
                                        ON pdg.donation_cart_id = pd.id 
                            WHERE   pd.user_id=%s
                            """, [str(user.id)])
            row_b = cursor.fetchone()
            projects_total = 0
            if row_a[0] :
                projects_total = projects_total+float(row_a[0])
            if row_b[0] :
                projects_total = projects_total+float(row_b[0])
        elif donation_type == 'monthly' :
            cursor = connection.cursor()
            cursor.execute("""
                            SELECT 
                                    SUM(pdn.amount) as project__sum 
                            FROM 
                                    pledger_donationcart AS pd 
                                        INNER JOIN 
                                    pledger_donationcartneeds AS pdn
                                        ON pdn.donation_cart_id = pd.id 
                            WHERE    1
                                    AND pd.user_id=%s
                                    AND pdn.donation_type='monthly'
                            """, [str(user.id)])
            row_a = cursor.fetchone()
            cursor.execute("""
                            SELECT 
                                    SUM(pdsn.amount) as project__sum 
                            FROM 
                                    pledger_donationsubscription AS pds 
                                        LEFT JOIN 
                                    pledger_donationsubscriptionneeds AS pdsn
                                        ON pdsn.donation_subscription_id = pdsn.id 
                            WHERE   1
                                    AND pds.user_id=%s
                                    AND pds.active
                            """, [str(user.id)])
            row_b = cursor.fetchone()
            projects_total = 0
            if row_a[0] :
                projects_total = projects_total+float(row_a[0])
            if row_b[0] :
                projects_total = projects_total+float(row_b[0])

        return projects_total

class DonationCartNeeds(models.Model):
    donation_cart       = models.ForeignKey(DonationCart)
    need                = models.ForeignKey(ProjectNeed)
    amount              = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    donation_type       = models.CharField(max_length=7, choices=DONATION_TYPES_CHOICES, default='monthly')
     
class DonationCartGoals(models.Model):
    donation_cart       = models.ForeignKey(DonationCart)
    goal                = models.ForeignKey(ProjectGoal)
    amount              = models.DecimalField(max_digits=12, decimal_places=2, default=0)

#donation subscriptions, storing active monthly donation subscriptions data undefinitely
class DonationSubscription(models.Model):
    user = models.ForeignKey(User)
    project = models.ForeignKey(Project)
    datetime_added = models.DateTimeField('date added', default=now())
    active = models.BooleanField(default=True)
    amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    needs = models.ManyToManyField(ProjectNeed, through='DonationSubscriptionNeeds')

    def cancelPendingTransactions(self, donation_subscription_need=None):
        if donation_subscription_need is not None :
            subscription_pending_transactions_list = (DonationTransaction.objects
                                                      .filter(pledger_donation_subscription__id=self.id)
                                                      .filter(accepting_need__id=donation_subscription_need.need__id)
                                                      .filter(transaction_status=DONATION_TRANSACTION_STATUSES_CHOICES.pending)
            )
        else :
            subscription_pending_transactions_list = (DonationTransaction.objects
                                                      .filter(pledger_donation_subscription__id=self.id)
                                                      .filter(transaction_status=DONATION_TRANSACTION_STATUSES_CHOICES.pending)
                                                      .exclude(accepting_need__isnull=True)
                                                      .exclude(accepting_need=0)
            )

        for subscription_pending_transaction in subscription_pending_transactions_list :
            subscription_pending_transaction.cancel()


class DonationSubscriptionNeeds(models.Model):
    donation_subscription = models.ForeignKey(DonationSubscription)
    need = models.ForeignKey(ProjectNeed)
    amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)



#donation history, storing all past donation transactions, for both onetime and monthly donations
class DonationTransaction(models.Model):
    transaction_type = models.CharField(max_length=64, choices=DONATION_TRANSACTION_TYPES_CHOICES,
                                        default=DONATION_TRANSACTION_TYPES_CHOICES.pledge)
    transaction_hash = models.CharField(max_length=255, unique=True)
    transaction_status = models.CharField(max_length=64, choices=DONATION_TRANSACTION_STATUSES_CHOICES,
                                          default=DONATION_TRANSACTION_STATUSES_CHOICES.unpaid)

    pledger_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    pledger_username = models.CharField(max_length=30, null=True, blank=True)
    pledger_email = models.CharField(max_length=255, null=True, blank=True)
    pledger_donation_type = models.CharField(max_length=7, choices=DONATION_TYPES_CHOICES,
                                             default=DONATION_TYPES_CHOICES.onetime, null=True, blank=True)
    pledger_donation_subscription = models.ForeignKey(DonationSubscription, on_delete=models.SET_NULL,
                                                      null=True, blank=True)

    other_source = models.ForeignKey(ProjectOtherSource, on_delete=models.SET_NULL, null=True, blank=True)
    other_source_title = models.CharField(max_length=255, null=True, blank=True)

    redonation_transaction = models.ForeignKey('self', on_delete=models.PROTECT, null=True, blank=True)
    redonation_project = models.ForeignKey(Project, related_name='redonation_project', on_delete=models.SET_NULL,
                                           null=True, blank=True)
    redonation_project_key = models.CharField(max_length=80, null=True, blank=True)
    redonation_project_title = models.CharField(max_length=80, null=True, blank=True)

    accepting_project = models.ForeignKey(Project, related_name='accepting_project', on_delete=models.SET_NULL,
                                          null=True, blank=True)
    accepting_project_key = models.CharField(max_length=80)
    accepting_project_title = models.CharField(max_length=255)
    transaction_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    transaction_datetime = models.DateTimeField('date sent')

    accepting_need = models.ForeignKey(ProjectNeed, on_delete=models.SET_NULL, null=True, blank=True)
    accepting_need_title = models.CharField(max_length=255, null=True, blank=True)
    accepting_need_key = models.CharField(max_length=80, null=True, blank=True)

    accepting_goal = models.ForeignKey(ProjectGoal, on_delete=models.SET_NULL, null=True, blank=True)
    accepting_goal_title = models.CharField(max_length=255, null=True, blank=True)
    accepting_goal_key = models.CharField(max_length=80, null=True, blank=True)
    accepting_goal_datetime_ending = models.DateTimeField(null=True, blank=True)

    def generateHash(self):
        transaction_datetime = str(self.transaction_datetime.isoformat())
        transaction_type = str(self.transaction_type)
        transaction_accepting_project_key = str(self.accepting_project.key)
        transaction_accepting_amount = str(self.transaction_amount)

        if (transaction_type == DONATION_TRANSACTION_TYPES_CHOICES.pledge):
            transaction_source = str(self.pledger_user.username)
        elif (transaction_type == DONATION_TRANSACTION_TYPES_CHOICES.other_source):
            transaction_source = str(self.other_source.id)
        elif (transaction_type == DONATION_TRANSACTION_TYPES_CHOICES.redonation):
            transaction_source = str(self.redonation_project.key)

        import hashlib

        hash_source = (transaction_datetime
                       + '_' + transaction_type
                       + '_' + transaction_source
                       + '_' + transaction_accepting_project_key
                       + '_' + transaction_accepting_amount
        )

        return hashlib.sha512(hash_source).hexdigest()

    # cycles through all linked projects for given transaction and creates redonations transactions if needed
    def createRedonationTransactions(self):
        projects_i_depend_on_list = (Project_Dependencies.objects
                                .filter(depender_project=self.accepting_project)
                                .order_by('sort_order'))

        # only genuine user pledges are to be redonated, other sources and redonations do not trigger subsequent redonations
        if self.transaction_type != DONATION_TRANSACTION_TYPES_CHOICES.pledge:
            return self

        # parent transaction should be already saved before doing this
        if not self.pk:
            return self

        project_current_budget = self.accepting_project.getTotalMonthlyBudget()

        for project_i_depend_on in projects_i_depend_on_list :
            # if the redonations transaction for this depender project and this initial transaction
            # exists already - omiting the transaction
            if (DonationTransaction.objects.filter(redonation_project=self.accepting_project)
                .filter(accepting_project=project_i_depend_on.depender_project)
                .filter(redonation_transaction=self).count()) > 0:
                continue


            # first we check if there is a fixed redonation amount set
            if project_i_depend_on.redonation_amount > 0 :
                # fixed redonation_amount is a part of this project's budget. Here we're getting
                # the % representation of that part.
                current_redonation_percent = Decimal((project_i_depend_on.redonation_amount) / project_current_budget).quantize(Decimal('0.01'))

                # multiply % representation on parent transaction's amount - getting the amount we're going
                # to redonate in this transaction
                current_redonation_amount = Decimal(self.transaction_amount*current_redonation_percent).quantize(Decimal('0.01'))

                # getting total of already sent redonations from this project to that one.
                total_current_redonations = (DonationTransaction.objects
                                             .filter(transaction_type=DONATION_TRANSACTION_TYPES_CHOICES.redonation)
                                             .filter(redonation_project_id=self.accepting_project.id)
                                             .filter(accepting_project_id=project_i_depend_on.dependee_project.id)
                                             .aggregate(Sum('transaction_amount'))['transaction_amount__sum']
                                            )

                total_current_redonations = Decimal(total_current_redonations or 0)

                # if (existing_redonations + current_redonation) makes up bigger amount than total
                # fixed redonation - redonation is capped
                if (total_current_redonations+current_redonation_amount) > project_i_depend_on.redonation_amount :
                    # in case of the cap current redonation should cover only difference between already given and the cap
                    current_redonation_amount = (Decimal(Decimal(project_i_depend_on.redonation_amount) - total_current_redonations)
                                                 .quantize(Decimal('0.01')))

                    # if in fact total already given redonations have covered all designated fixed
                    # redonation amount - nothing else to be redonated here then, omiting this cycle.
                    if current_redonation_amount <= 0 :
                        continue

            # if there is no fixed redonation, maybe there is a percentage
            elif project_i_depend_on.redonation_percent > 0 :
                # figuring out redonation amount from a percentage is easy - there is no cap,
                # just a share of the initial pledge
                current_redonation_amount = (Decimal((self.transaction_amount/100) * project_i_depend_on.redonation_percent)
                                             .quantize(Decimal('0.01')))
            else :  # this project dependency doesn't imply any redonations, so we omit this cycle
                continue

            # now we have to take into account all active needs of the accepting project, if there are any
            project_i_depend_on_needs_list = ProjectNeed.objects.filter(project=project_i_depend_on, is_public=True)
            project_i_depend_on_needs_count = project_i_depend_on_needs_list.count()

            # if redonation accepting project has no needs - redonation is not bound to any particular need
            if project_i_depend_on_needs_count == 0 :
                redonation_transaction = DonationTransaction()
                redonation_transaction.populateRedonationTransaction(project=project_i_depend_on.dependee_project,
                                                                     redonation_project=self.accepting_project,
                                                                     redonation_transaction=self,
                                                                     pledge_amount=current_redonation_amount)
                redonation_transaction.save()
            else :
                # if there are needs in the redonation accepting project - we split redonation amount between all needs equally
                current_redonation_amount_per_need = current_redonation_amount / project_i_depend_on_needs_count
                for project_i_depend_on_need in project_i_depend_on_needs_list :
                    redonation_transaction = DonationTransaction()
                    redonation_transaction.populateRedonationTransaction(project=project_i_depend_on.dependee_project,
                                                                         redonation_project=self.accepting_project,
                                                                         redonation_transaction=self,
                                                                         pledge_amount=current_redonation_amount_per_need,
                                                                         need=project_i_depend_on_need)
                    redonation_transaction.save()


    def populatePledgeTransaction(self, project, user, pledge_amount, need=None, goal=None, donation_subscription=None):
        self.transaction_type = DONATION_TRANSACTION_TYPES_CHOICES.pledge
        self.transaction_status = DONATION_TRANSACTION_STATUSES_CHOICES.unpaid

        if donation_subscription is not None:
            self.pledger_donation_type = DONATION_TYPES_CHOICES.monthly
            self.pledger_donation_subscription = donation_subscription
        else:
            self.pledger_donation_type = DONATION_TYPES_CHOICES.onetime

        self.pledger_user = user
        self.pledger_username = user.username
        self.pledger_email = user.email

        self.accepting_project = project
        self.accepting_project_key = project.key
        self.accepting_project_title = project.title
        self.transaction_amount = pledge_amount

        if need is not None :
            self.accepting_need = need
            self.accepting_need_title = need.title
            self.accepting_need_key = need.key
        elif goal is not None :
            self.accepting_goal = goal
            self.accepting_goal_title = goal.title
            self.accepting_goal_key = goal.key
            self.accepting_goal_datetime_ending = goal.date_ending

        self.transaction_datetime = now()
        self.transaction_hash = self.generateHash()

    def populateRedonationTransaction(self, project, redonation_project, redonation_transaction, pledge_amount,
                                      need=None):
        self.transaction_type = DONATION_TRANSACTION_TYPES_CHOICES.redonation
        self.transaction_status = redonation_transaction.transaction_status
        self.pledger_donation_type = redonation_transaction.pledger_donation_type

        self.redonation_transaction = redonation_transaction
        self.redonation_project = redonation_project
        self.redonation_project_key = redonation_project.key
        self.redonation_project_title = redonation_project.title

        self.accepting_project = project
        self.accepting_project_key = project.key
        self.accepting_project_title = project.title
        self.transaction_amount = pledge_amount
        self.transaction_datetime = now()

        if need is ProjectNeed:
            self.accepting_need = need
            self.accepting_need_title = need.title
            self.accepting_need_key = need.key

        self.transaction_hash = self.generateHash()

    def cancel(self):
        self.transaction_status = DONATION_TRANSACTION_STATUSES_CHOICES.cancelled
        self.save()

        redonation_transactions_list = (DonationTransaction.objects
                            .filter(transaction_type=DONATION_TRANSACTION_TYPES_CHOICES.redonation)
                            .filter(redonation_transaction_id=self.id)
                            )

        for redonation_transaction in redonation_transactions_list :
            redonation_transaction.transaction_status = DONATION_TRANSACTION_STATUSES_CHOICES.cancelled
            redonation_transaction.save()






















