import base64
import os
import balanced
from django.db import models
from django.contrib.auth.models import User, UserManager
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from django.db.models import Sum

from model_utils import Choices
from bitfund.core.settings_split.project import API_KEY_LENGTH
from bitfund.project.models import *

DONATION_TRANSACTION_TYPES_CHOICES = Choices(
    ('pledge', u'Pledge'), # onetime or monthly pledge by the user
    ('other_source', u'Other Source'), # income from other source, stated by the project maintainers
    ('redonation', u'Redonation'), # redonation from a pledge on a depended project
)
DONATION_TRANSACTION_STATUSES_CHOICES = Choices(
    ('pending', u'Pending, Unpaid'),
    # transaction for the monthly pledge for current month, month end not reached yet, not processed through payment yet. "pending" is for subscription transactions.
    ('unpaid', u'Confirmed, Unpaid'),
    # trasaction for the monthly pledge when month end reached, or from onetime pledge at any time, not processed through payment yet. "unpaid" is for onetime transactions.
    ('paid', u'Paid'), # trasaction already processed through payment successfully
    ('rejected', u'Rejected'), # trasaction rejected by the payment processor
    ('cancelled', u'Cancelled'), # trasaction cancelled by the issuer
)

PAYMENT_TRANSACTION_STATUSES_CHOICES = Choices(
    ('incomplete', u'Incomplete'), # payment transaction is not fully filled yet in and thus invalid
    ('pending', u'Pending'), # payment transaction to be processed
    ('paid', u'Paid'), # payment transaction successfully processed
    ('rejected', u'Rejected'), # payment trasaction rejected by the payment processor
)

BANK_ACCOUNT_ENTITY_TYPE_CHOICES = Choices(
    ('person', u'Individual'),
    ('business', u'Organisation'),
)


class Profile(User):
    user = models.OneToOneField(User, unique=True, verbose_name=_('user'), related_name='profile')
    api_token = models.CharField(max_length=255, unique=True)
    gravatar_id = models.CharField(max_length=255, null=True, blank=True)
    twitter_pic_url = models.CharField(max_length=1000, null=True, blank=True)
    donation_amount_is_public = models.BooleanField(default=True)
    projects_list_is_public = models.BooleanField(default=False)
    twitter_username = models.CharField(max_length=1000, null=True, blank=True)
    twitter_account_url = models.TextField(null=True, blank=True)
    github_username = models.CharField(max_length=1000, null=True, blank=True)
    github_account_url = models.TextField(null=True, blank=True)

    # calculates total donations from this user to certain project
    def getTotalDonationsByProject(self, project):
        user_project_donations_sum = (DonationTransaction.objects
                                      .filter(user=self.user, accepting_project=project)
                                      .aggregate(Sum('transaction_amount'))['transaction_amount__sum']) or 0

        return Decimal(user_project_donations_sum).quantize(Decimal('0.01'))

    @classmethod
    def generateAPIToken(cls):
        return str(base64.urlsafe_b64encode(os.urandom(1000)))[0:API_KEY_LENGTH]

#part of the social auth pipeline, creates new user profile
#def save_user_profile(sender, user_id, user, is_new, **kwargs):
def save_user_profile(request, *args, **kwargs):
    if kwargs['is_new']:
        profile = Profile()
        profile.user_id = kwargs['user'].id
        profile.api_token = Profile.generateAPIToken()
        if 'gravatar_id' in kwargs['response'] and kwargs['response']['gravatar_id'] != '':
            profile.gravatar_id = kwargs['response']['gravatar_id']
        if 'screen_name' in kwargs['response']:
            profile.twitter_pic_url = 'http://api.twitter.com/1/users/profile_image/' + kwargs['response'][
                'screen_name'] + '.png?size=original'

        if 'twitter' in kwargs and kwargs['twitter']:
            profile.twitter_username = kwargs['username']
            profile.twitter_account_url = 'http://twitter.com/'+kwargs['username'] #this is wrong, need to figure out right way later

        if 'github' in kwargs and kwargs['github']:
            profile.github_username = kwargs['username']
            profile.github_account_url = kwargs['response']['html_url']

        profile.save()

    return None


class BalancedAccount(models.Model):
    user = models.OneToOneField(User, unique=True)
    uri = models.CharField(max_length=255, unique=True)
    is_underwritten = models.BooleanField(default=False)

    #returns BalancedAccount for this user. If there is no account - creates it.
    @classmethod
    def getAccount(cls, user_id):
        existing_account = cls.objects.filter(user_id=user_id)
        if existing_account.count() > 0:
            return existing_account[0]
        else:
            balanced_account = balanced.Account().save()

            new_account = cls()
            new_account.user_id = user_id
            new_account.uri = balanced_account.uri
            new_account.is_underwritten = False
            new_account.save()

            return new_account


#bank card data. contains only pieces that are safe and allowed to be stored on our side
class BankCard(models.Model):
    user = models.OneToOneField(User, unique=True)
    balanced_account = models.OneToOneField(BalancedAccount, unique=True)
    uri = models.CharField(max_length=255, unique=True)
    brand = models.CharField(max_length=25)
    last_four_digits = models.CharField(max_length=4)
    is_valid = models.BooleanField()
    name_on_card = models.CharField(max_length=255, null=True, blank=True)
    address_1 = models.CharField(max_length=255, null=True, blank=True)
    address_2 = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    country_code = models.CharField(max_length=5, null=True, blank=True)


#bank account data. contains only pieces that are safe and allowed to be stored on our side
class BankAccount(models.Model):
    user = models.OneToOneField(User, unique=True)
    balanced_account = models.OneToOneField(BalancedAccount, unique=True)
    uri = models.CharField(max_length=255, unique=True)
    last_four = models.CharField(max_length=4)
    bank_name = models.CharField(max_length=255)
    is_valid = models.BooleanField(default=True)


#list of transations actually debited from pledgers bank cards. aggregates all donation transactions for one pledger one month
class PaymentTransaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    balanced_account = models.ForeignKey(BalancedAccount, on_delete=models.PROTECT)
    uri = models.CharField(max_length=255, unique=True, null=True, blank=True)
    status = models.CharField(max_length=10, choices=PAYMENT_TRANSACTION_STATUSES_CHOICES,
                              default=PAYMENT_TRANSACTION_STATUSES_CHOICES.pending)
    balanced_status = models.CharField(max_length=25, null=True, blank=True)
    balanced_transaction_number = models.CharField(max_length=255, unique=True, null=True, blank=True)
    source_uri = models.CharField(max_length=255, null=True, blank=True)
    statement_text = models.CharField(max_length=22, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    transaction_amount = models.DecimalField(decimal_places=2, max_digits=12,
                                             default=0) #aggregated amount of all DonationTransactions payed with this PaymentTransaction
    fees_amount = models.DecimalField(decimal_places=2, max_digits=12,
                                      default=0) # fees amount applied to this PaymentTransaction
    total_amount = models.DecimalField(decimal_places=2, max_digits=12, default=0) # total amount debited
    datetime_added = models.DateTimeField('date added', default=now())
    datetime_debited = models.DateTimeField('date debited', null=True, blank=True)

#donation subscriptions, storing active monthly donation subscriptions data until cancelled
class DonationSubscription(models.Model):
    user = models.ForeignKey(User)
    project = models.ForeignKey(Project)
    datetime_added = models.DateTimeField('date added', default=now())
    is_active = models.BooleanField(default=True)
    amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    needs = models.ManyToManyField(ProjectNeed, through='DonationSubscriptionNeeds')

    def cancelPendingTransactions(self, donation_subscription_need=None):
        if donation_subscription_need is not None:
            subscription_pending_transactions_list = (DonationTransaction.objects
                                                      .filter(pledger_donation_subscription_id=self.id)
                                                      .filter(accepting_need_id=donation_subscription_need.need_id)
                                                      .filter(
                transaction_status=DONATION_TRANSACTION_STATUSES_CHOICES.pending)
            )
        else:
            subscription_pending_transactions_list = (DonationTransaction.objects
                                                      .filter(pledger_donation_subscription_id=self.id)
                                                      .filter(
                transaction_status=DONATION_TRANSACTION_STATUSES_CHOICES.pending)
                                                      .exclude(accepting_need__isnull=True)
                                                      .exclude(accepting_need=0)
            )

        for subscription_pending_transaction in subscription_pending_transactions_list:
            subscription_pending_transaction.cancel()


class DonationSubscriptionNeeds(models.Model):
    donation_subscription = models.ForeignKey(DonationSubscription, on_delete=models.CASCADE)
    need = models.ForeignKey(ProjectNeed, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)

#donation history, storing all past donation transactions, for both onetime and monthly donations
class DonationTransaction(models.Model):
    transaction_type = models.CharField(max_length=64, choices=DONATION_TRANSACTION_TYPES_CHOICES,
                                        default=DONATION_TRANSACTION_TYPES_CHOICES.pledge)
    transaction_hash = models.CharField(max_length=255, unique=True)
    transaction_status = models.CharField(max_length=64, choices=DONATION_TRANSACTION_STATUSES_CHOICES,
                                          default=DONATION_TRANSACTION_STATUSES_CHOICES.unpaid)
    payment_transaction = models.ForeignKey(PaymentTransaction, on_delete=models.PROTECT, null=True, blank=True)

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

        for project_i_depend_on in projects_i_depend_on_list:
            # if the redonations transaction for this depender project and this initial transaction
            # exists already - omiting the transaction
            if (DonationTransaction.objects.filter(redonation_project=self.accepting_project)
                .filter(accepting_project=project_i_depend_on.depender_project)
                .filter(redonation_transaction=self).count()) > 0:
                continue


            # first we check if there is a fixed redonation amount set
            if project_i_depend_on.redonation_amount > 0:
                # fixed redonation_amount is a part of this project's budget. Here we're getting
                # the % representation of that part.
                current_redonation_percent = Decimal(
                    (project_i_depend_on.redonation_amount) / project_current_budget).quantize(Decimal('0.01'))

                # multiply % representation on parent transaction's amount - getting the amount we're going
                # to redonate in this transaction
                current_redonation_amount = Decimal(self.transaction_amount * current_redonation_percent).quantize(
                    Decimal('0.01'))

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
                if (total_current_redonations + current_redonation_amount) > project_i_depend_on.redonation_amount:
                    # in case of the cap current redonation should cover only difference between already given and the cap
                    current_redonation_amount = (
                    Decimal(Decimal(project_i_depend_on.redonation_amount) - total_current_redonations)
                    .quantize(Decimal('0.01')))

                    # if in fact total already given redonations have covered all designated fixed
                    # redonation amount - nothing else to be redonated here then, omiting this cycle.
                    if current_redonation_amount <= 0:
                        continue

            # if there is no fixed redonation, maybe there is a percentage
            elif project_i_depend_on.redonation_percent > 0:
                # figuring out redonation amount from a percentage is easy - there is no cap,
                # just a share of the initial pledge
                current_redonation_amount = (
                Decimal((self.transaction_amount / 100) * project_i_depend_on.redonation_percent)
                .quantize(Decimal('0.01')))
            else:  # this project dependency doesn't imply any redonations, so we omit this cycle
                continue

            # now we have to take into account all active needs of the accepting project, if there are any
            project_i_depend_on_needs_list = ProjectNeed.objects.filter(project=project_i_depend_on, is_public=True)
            project_i_depend_on_needs_count = project_i_depend_on_needs_list.count()

            # if redonation accepting project has no needs - redonation is not bound to any particular need
            if project_i_depend_on_needs_count == 0:
                redonation_transaction = DonationTransaction()
                redonation_transaction.populateRedonationTransaction(project=project_i_depend_on.dependee_project,
                                                                     redonation_project=self.accepting_project,
                                                                     redonation_transaction=self,
                                                                     pledge_amount=current_redonation_amount)
                redonation_transaction.save()
            else:
                # if there are needs in the redonation accepting project - we split redonation amount between all needs equally
                current_redonation_amount_per_need = current_redonation_amount / project_i_depend_on_needs_count
                for project_i_depend_on_need in project_i_depend_on_needs_list:
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

        if need is not None:
            self.accepting_need = need
            self.accepting_need_title = need.title
            self.accepting_need_key = need.key
        elif goal is not None:
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

        for redonation_transaction in redonation_transactions_list:
            redonation_transaction.transaction_status = DONATION_TRANSACTION_STATUSES_CHOICES.cancelled
            redonation_transaction.save()









