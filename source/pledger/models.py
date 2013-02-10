import datetime

from django.db import models
from django.contrib.auth.models import User
from django.utils.datetime_safe import datetime
from django.utils.timezone import utc, now 
from django.utils.translation import ugettext_lazy as _
from django.db.models import Count, Sum
from django.shortcuts import get_object_or_404

from userena.models import UserenaBaseProfile

from project.models import *
from project.lists import *

DONATION_TRANSACTION_TYPES_CHOICES = (
    ('pledge', u'Pledge'),
    ('other_source', u'Other Source'),
    ('redonation', u'Redonation'),
)

DONATION_TRANSACTION_STATUSES_CHOICES = (
    ('unpaid', u'Confirmed, Unpaid'),
    ('paid', u'Paid'),
    ('rejected', u'Rejected'),
)


class Profile(UserenaBaseProfile):
    user                    = models.OneToOneField(User, unique=True, verbose_name=_('user'), related_name='my_profile')
    api_token               = models.CharField(max_length=255, unique=True)
    donation_is_public      = models.BooleanField(default=True)
    
    def getTotalProjectDonations(self, project):
        from django.db.models import Sum 
        from pledger.models import DonationTransaction, DonationTransactionNeeds, DonationTransactionGoals
        
        user_project_donations_history           = DonationTransaction.objects.filter(user=self.user).filter(project=project)
        user_project_donations_history_needs_sum = (DonationTransactionNeeds.objects.filter(donation_history__in=user_project_donations_history)
                                                                                .aggregate(Sum('amount'))['amount__sum']
                                                                                ) or 0

        user_project_donations_history_goals_sum = (DonationTransactionGoals.objects.filter(donation_history__in=user_project_donations_history)
                                                                                .aggregate(Sum('amount'))['amount__sum']
                                                                                ) or 0
        
        return user_project_donations_history_needs_sum + user_project_donations_history_goals_sum


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
    user                = models.ForeignKey(User)
    project             = models.ForeignKey(Project)
    datetime_last_sent  = models.DateTimeField('last sent', null=True)
    active              = models.BooleanField(default = True)
    needs               = models.ManyToManyField(ProjectNeed, through='DonationSubscriptionNeeds')

class DonationSubscriptionNeeds(models.Model):
    donation_subscription   = models.ForeignKey(DonationSubscription)
    need                    = models.ForeignKey(ProjectNeed)
    amount                  = models.DecimalField(max_digits=6, decimal_places=2, default=0)

     
#donation history, storing all past donation transactions, for both onetime and monthly donations      
class DonationTransaction(models.Model):
    transaction_type                = models.CharField(max_length=64, choices=DONATION_TRANSACTION_TYPES_CHOICES)
    transaction_hash                = models.CharField(max_length=64, unique=True)
    transaction_status              = models.CharField(max_length=64, choices=DONATION_TRANSACTION_STATUSES_CHOICES)
    
    pledger_user                    = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    pledger_donation_subscription   = models.ForeignKey(DonationSubscription, on_delete=models.SET_NULL, null=True, blank=True) 

    #other_source                    = models.ForeignKey(ProjectOtherSource, on_delete=models.SET_NULL, null=True, blank=True)

    redonation_transaction          = models.ForeignKey('self', on_delete=models.PROTECT, null=True, blank=True)
    redonation_project              = models.ForeignKey(Project, related_name='redonation_project', on_delete=models.SET_NULL, null=True, blank=True)
    
    accepting_project               = models.ForeignKey(Project, related_name='accepting_project', on_delete=models.SET_NULL, null=True, blank=True)
    accepting_project_key           = models.CharField(max_length=80)
    accepting_project_title         = models.CharField(max_length=255)
    accepting_amount                = models.CharField(max_length=255)
    datetime_added                  = models.DateTimeField('date sent', default=now())
    needs                           = models.ManyToManyField(ProjectNeed, through='DonationTransactionNeeds')
    goals                           = models.ManyToManyField(ProjectGoal, through='DonationTransactionGoals')

    def generateHash(self):
        transaction_date                  = str(self.datetime_added.isoformat())
        transaction_type                  = str(self.transaction_type)
        transaction_username              = str(self.accepting_project_key)
        transaction_other_source          = str(self.other_source.id)
        transaction_redonation_project    = str(self.redonation_project.id)
        transaction_accepting_project_key = str(self.accepting_project_key)
        transaction_accepting_amount      = str(self.accepting_amount)
        
        import hashlib

        hash_source = (transaction_date
                       +'_'+transaction_type
                       +'_'+transaction_username
                       +'_'+transaction_other_source
                       +'_'+transaction_redonation_project
                       +'_'+transaction_accepting_project_key
                       +'_'+transaction_accepting_amount
                       )  
                
        return hashlib.sha512(hash_source).hexdigest()
        

    def getAmount(self):
        from django.db.models import Sum
        from pledger.models import DonationTransactionNeeds, DonationTransactionGoals
        
        user_project_donations_history_needs_sum = (DonationTransactionNeeds.objects.filter(donation_history=self)
                                                                                .aggregate(Sum('amount'))['amount__sum']
                                                                                ) or 0

        user_project_donations_history_goals_sum = (DonationTransactionGoals.objects.filter(donation_history=self)
                                                                                .aggregate(Sum('amount'))['amount__sum']
                                                                                ) or 0

        return user_project_donations_history_needs_sum + user_project_donations_history_goals_sum

class DonationTransactionDetails(models.Model):
    donation_transaction            = models.OneToOneField(DonationTransaction)
    pledger_username                 = models.CharField(max_length=30, null=True, blank=True)
    pledger_email                    = models.CharField(max_length=255, null=True, blank=True)

    other_source_title              = models.CharField(max_length=255, null=True, blank=True)
    
    redonation_project_key          = models.CharField(max_length=80, null=True, blank=True)
    redonation_project_title        = models.CharField(max_length=80, null=True, blank=True)



class DonationTransactionNeeds(models.Model):
    donation_history            = models.ForeignKey(DonationTransaction)
    need                        = models.ForeignKey(ProjectNeed, on_delete=models.SET_NULL, null=True)
    need_title                  = models.CharField(max_length=255)
    need_key                    = models.CharField(max_length=80, null=True, blank=True)
    amount                      = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    donation_type               = models.CharField(max_length=7, choices=DONATION_TYPES_CHOICES, default='onetime')
     
class DonationTransactionGoals(models.Model):
    donation_history            = models.ForeignKey(DonationTransaction)
    goal                        = models.ForeignKey(ProjectGoal, on_delete=models.SET_NULL, null=True)
    goal_title                  = models.CharField(max_length=255)
    goal_key                    = models.CharField(max_length=80, null=True, blank=True)
    goal_date_ending            = models.DateField('date ending')
    amount                      = models.DecimalField(max_digits=12, decimal_places=2, default=0)

                                                   