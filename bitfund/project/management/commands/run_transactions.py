from decimal import Decimal
from optparse import make_option
import balanced

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models.query_utils import Q
from django.shortcuts import get_object_or_404
from django.utils.timezone import now

from bitfund.core.settings_split.extensions import BALANCED
from bitfund.pledger.models import DonationTransaction, DONATION_TRANSACTION_TYPES_CHOICES, DONATION_TRANSACTION_STATUSES_CHOICES, BalancedAccount, PaymentTransaction, PAYMENT_TRANSACTION_STATUSES_CHOICES
from bitfund.project.management.helpers import _calculate_balanced_transaction_fee, _calculate_project_balances
from bitfund.project.models import Project


class Command(BaseCommand):
    # option_list = BaseCommand.option_list + (
    #     make_option('--delete',
    #                 action='store_true',
    #                 dest='delete',
    #                 default=False,
    #                 help='Delete poll instead of closing it'),
    # )

    help = 'This command: \n'\
           '    - gathers all existing unpaid donation transactions \n' \
           '    - creates aggregated payment transactions \n' \
           '    - runs debits with Balanced \n' \
           '    - updates donation transactions statuses \n' \
           '    - updates project balances \n'

    def handle(self, *args, **options):
        aggregated_donations_transactions_list = self.get_aggregated_donations_transactions_list()
        self.create_payment_transactions(aggregated_donations_transactions_list)
        self.debit_payments()


    # fetches and forms a list of all DonationTransactions to process, aggregated by pledger_user
    def get_aggregated_donations_transactions_list(self):
        unpaid_donation_transactions_list = (DonationTransaction.objects
                                             .filter(transaction_type=DONATION_TRANSACTION_TYPES_CHOICES.pledge)
                                             .filter(Q(transaction_status=DONATION_TRANSACTION_STATUSES_CHOICES.unpaid) | Q(transaction_status=DONATION_TRANSACTION_STATUSES_CHOICES.pending))
                                             .filter(payment_transaction__isnull=True)
        )

        transactionc_count = unpaid_donation_transactions_list.count()


        aggregated_donations_transactions_list = {}

        for unpaid_donation_transaction in unpaid_donation_transactions_list:
            if unpaid_donation_transaction.pledger_user_id not in aggregated_donations_transactions_list:
                aggregated_donations_transactions_list[unpaid_donation_transaction.pledger_user_id] = {
                    'pledger_user_id': unpaid_donation_transaction.pledger_user_id,
                    'donation_transactions_list': {},
                    'amount': Decimal('0.00'),
                    }

            (aggregated_donations_transactions_list[unpaid_donation_transaction.pledger_user_id]
             ['donation_transactions_list']
             [unpaid_donation_transaction.id]) = {'transaction_id': unpaid_donation_transaction.id,
                                                  'transaction_amount': unpaid_donation_transaction.transaction_amount,
                                                  'accepting_project': unpaid_donation_transaction.id,
                                                  }

            aggregated_donations_transactions_list[unpaid_donation_transaction.pledger_user_id]['amount'] = (
                unpaid_donation_transaction.transaction_amount
                + aggregated_donations_transactions_list[unpaid_donation_transaction.pledger_user_id]['amount'])

        return aggregated_donations_transactions_list


    # cycles through aggregated_donations_transactions_list and creates PaymentTransaction entries based on it, with "pending" status.
    # Also updates DonationTransaction entries with relevant newly created payment_transaction_ids
    def create_payment_transactions(self, aggregated_donations_transactions_list):
        for pledger_user_id in aggregated_donations_transactions_list:
            payment_transaction_data = aggregated_donations_transactions_list[pledger_user_id]
            pledger_balanced_account = BalancedAccount.objects.filter(user_id=pledger_user_id)

            if (pledger_balanced_account.count() > 0):
                pledger_balanced_account = pledger_balanced_account[0]
            else:
                pledger_balanced_account = False

            if not pledger_balanced_account:
                for donation_transaction in payment_transaction_data['donation_transactions_list']:
                    bad_transaction = DonationTransaction.objects.get(pk=donation_transaction['transaction_id'])
                    bad_transaction.transaction_status = DONATION_TRANSACTION_STATUSES_CHOICES.rejected
                    bad_transaction.save()
            else:
                payment_transaction = PaymentTransaction()
                payment_transaction.user_id = pledger_user_id
                payment_transaction.balanced_account_id = pledger_balanced_account.id
                payment_transaction.status = PAYMENT_TRANSACTION_STATUSES_CHOICES.incomplete
                payment_transaction.amount = payment_transaction_data['amount']
                payment_transaction.fees_amount = _calculate_balanced_transaction_fee(payment_transaction_data['amount'])
                payment_transaction.total_amount = payment_transaction.amount + payment_transaction.fees_amount
                payment_transaction.save()

                pledger_user = User.objects.get(pk=payment_transaction_data['pledger_user_id'])
                pledger_user = User.objects.get(pk=payment_transaction_data['pledger_user_id'])

                payment_transaction_description = now().strftime(
                    '%b %Y') + ' payment from ' + pledger_user.username + ' to '
                for index in payment_transaction_data['donation_transactions_list']:
                    donation_transaction = payment_transaction_data['donation_transactions_list'][index]
                    not_bad_transaction = DonationTransaction.objects.get(pk=donation_transaction['transaction_id'])
                    not_bad_transaction.payment_transaction_id = payment_transaction.id
                    not_bad_transaction.save()

                    payment_transaction_description = (payment_transaction_description
                                                       + ' ' + not_bad_transaction.accepting_project_key
                                                       + ': $' + str(not_bad_transaction.transaction_amount) + ';')

                payment_transaction.status = PAYMENT_TRANSACTION_STATUSES_CHOICES.pending
                payment_transaction.statement_text = 'BitFind.org #' + unicode(payment_transaction.id)
                payment_transaction.description = payment_transaction_description
                payment_transaction.save()


    # debits all payments for PaymentTransactions in "pending" status. updates PaymentTransactions on success or failure.
    # also invokes self.update_donation_transaction() to update DonationTransaction data
    # also invokes self.update_project_balances() to update Project balances
    # runs each cycle in DB transaction
    def debit_payments(self):
        balanced.configure(BALANCED['API_KEY'])

        payment_transactions_to_debit_list = PaymentTransaction.objects.filter(
            status=PAYMENT_TRANSACTION_STATUSES_CHOICES.pending)
        for payment_transaction in payment_transactions_to_debit_list:
            print 'running debit for transaction #'+str(payment_transaction.id)

            pledger_balanced_account = BalancedAccount.objects.get(pk=payment_transaction.balanced_account_id)
            balanced_account = balanced.Account.find(pledger_balanced_account.uri)

            with transaction.commit_on_success():
                total_amount_cents = int(Decimal(payment_transaction.total_amount*Decimal(100)).quantize((Decimal('1'))))
                balanced_debit = balanced_account.debit(appears_on_statement_as=payment_transaction.statement_text,
                                                        amount=total_amount_cents,
                                                        description=payment_transaction.description,
                                                        )

                if balanced_debit.status == 'succeeded':
                    payment_transaction.status = PAYMENT_TRANSACTION_STATUSES_CHOICES.paid
                    payment_transaction.datetime_debited = now()
                else:
                    payment_transaction.status = PAYMENT_TRANSACTION_STATUSES_CHOICES.rejected
                payment_transaction.balanced_status = balanced_debit.status
                try:
                    payment_transaction.balanced_transaction_number = balanced_debit.transaction_number
                    payment_transaction.source_uri = balanced_debit.source.uri
                    payment_transaction.uri = balanced_debit.uri
                except AttributeError:
                    pass
                payment_transaction.save()

                self.update_donation_transaction(payment_transaction)
                if payment_transaction.status == PAYMENT_TRANSACTION_STATUSES_CHOICES.paid:
                    self.update_project_balances(payment_transaction)

    # updates donation transaction status. also updates redonation transaction statuses.
    def update_donation_transaction(self, payment_transaction):
        queries_count = 0
        donation_transactions_list = (DonationTransaction.objects
                                      .filter(payment_transaction_id=payment_transaction.id)
                                      .filter(transaction_type=DONATION_TRANSACTION_TYPES_CHOICES.pledge))
        for donation_transaction in donation_transactions_list:
            if payment_transaction.status == PAYMENT_TRANSACTION_STATUSES_CHOICES.paid:
                donation_transaction.transaction_status = DONATION_TRANSACTION_STATUSES_CHOICES.paid
            else:
                donation_transaction.transaction_status = DONATION_TRANSACTION_STATUSES_CHOICES.rejected

            donation_transaction.save()
            queries_count = queries_count+1

            redonation_transactions_list = (DonationTransaction.objects
                                            .filter(redonation_transaction_id=donation_transaction.id)
                                            .filter(transaction_type=DONATION_TRANSACTION_TYPES_CHOICES.redonation))
            for redonation_transaction in redonation_transactions_list:
                if payment_transaction.status == PAYMENT_TRANSACTION_STATUSES_CHOICES.paid:
                    redonation_transaction.transaction_status = DONATION_TRANSACTION_STATUSES_CHOICES.paid
                else:
                    redonation_transaction.transaction_status = DONATION_TRANSACTION_STATUSES_CHOICES.rejected

                redonation_transaction.payment_transaction_id = payment_transaction.id
                redonation_transaction.save()
                queries_count = queries_count+1

    #updates project balances, adds supplied payment_transaction.
    #also check all redonations and updates all redonation accepting projects accordingly
    def update_project_balances(self, payment_transaction):
        donation_transactions_list = (DonationTransaction.objects
                                      .filter(payment_transaction_id=payment_transaction.id)
                                      .filter(transaction_status=DONATION_TRANSACTION_STATUSES_CHOICES.paid))

        for donation_transaction in donation_transactions_list:
            project = Project.objects.get(pk=donation_transaction.accepting_project_id)
            project.amount_pledged = project.amount_pledged + donation_transaction.transaction_amount

            redonation_transactions_list = (DonationTransaction.objects
                                            .filter(payment_transaction_id=payment_transaction.id)
                                            .filter(redonation_transaction_id=donation_transaction.id)
                                            .filter(transaction_status=DONATION_TRANSACTION_STATUSES_CHOICES.paid))

            total_redonations = Decimal('0.00')
            redonation_accepting_projects_list = {}
            for redonation_transaction in redonation_transactions_list:
                if redonation_transaction.accepting_project_id not in redonation_accepting_projects_list:
                    redonation_accepting_projects_list[redonation_transaction.accepting_project_id] = {'redonation_accepting_project_id': redonation_transaction.accepting_project_id,
                                                                                                       'additional_amount_redonation_received': Decimal('0.00')}

                redonation_accepting_projects_list[redonation_transaction.accepting_project_id]['additional_amount_redonation_received'] = \
                    redonation_accepting_projects_list[redonation_transaction.accepting_project_id]['additional_amount_redonation_received'] \
                    + redonation_transaction.transaction_amount

                total_redonations = total_redonations + redonation_transaction.transaction_amount

            for redonation_accepting_project_id in redonation_accepting_projects_list:
                redonation_accepting_project = Project.objects.get(pk=redonation_accepting_project_id)
                new_balances = _calculate_project_balances(redonation_accepting_project,
                                                           additional_amount_redonation_received=redonation_accepting_projects_list[redonation_accepting_project_id]['additional_amount_redonation_received'])

                redonation_accepting_project.amount_pledged = new_balances['amount_pledged']
                redonation_accepting_project.amount_redonation_given = new_balances['amount_redonation_given']
                redonation_accepting_project.amount_redonation_received = new_balances['amount_redonation_received']
                redonation_accepting_project.amount_withdrawn = new_balances['amount_withdrawn']
                redonation_accepting_project.amount_balance = new_balances['amount_balance']

                redonation_accepting_project.save()

            project.amount_redonation_given = project.amount_redonation_given + total_redonations

            project.amount_balance = ((project.amount_pledged + project.amount_redonation_received)
                                      - (project.amount_redonation_given + project.amount_withdrawn))
            project.save()
