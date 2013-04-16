from optparse import make_option
import balanced

from django.core.management.base import BaseCommand
from django.db.models.query_utils import Q
from django.utils.timezone import now
from bitfund.core.settings.extensions import BALANCED
from bitfund.pledger.models import DonationTransaction, DONATION_TRANSACTION_TYPES_CHOICES, DONATION_TRANSACTION_STATUSES_CHOICES, BalancedAccount


class Command(BaseCommand):
    # option_list = BaseCommand.option_list + (
    #     make_option('--delete',
    #                 action='store_true',
    #                 dest='delete',
    #                 default=False,
    #                 help='Delete poll instead of closing it'),
    # )

    def handle(self, *args, **options):
        balanced.configure(BALANCED['API_KEY'])

        unpaid_donation_transactions_list = (DonationTransaction.objects
                                                .filter(transaction_type=DONATION_TRANSACTION_TYPES_CHOICES.pledge)
                                                .filter(status=DONATION_TRANSACTION_STATUSES_CHOICES.unpaid)
                                                )

        payment_transactions_list = {}

        for unpaid_donation_transaction in unpaid_donation_transactions_list:
            if unpaid_donation_transaction.pledger_user_id not in payment_transactions_list:
                payment_transactions_list[unpaid_donation_transaction.pledger_user_id] = {'user_id': unpaid_donation_transaction.pledger_user_id,
                                                                                          'transactions_list': {},
                                                                                          'appears_on_statement_as': 'BitFind.org',
                                                                                          'description': 'payment for '+now().strftime('%Y-%m-%d'),
                                                                                          'amount': 0.0,
                }

            payment_transactions_list[unpaid_donation_transaction.pledger_user_id]['transactions_list']

        for payment_transaction in payment_transactions_list:
            pledger_balanced_account = BalancedAccount.objects.filter(user_id=unpaid_donation_transaction.pledger_user_id)

            if (pledger_balanced_account.count() > 0):
                pledger_balanced_account = pledger_balanced_account[0]
            else :
                transaction.transaction_status = DONATION_TRANSACTION_STATUSES_CHOICES.rejected
                transaction.save()
                continue


            balanced_account = balanced.Account.find(pledger_balanced_account.uri)
            balanced_account.debit(
                appears_on_statement_as='BitFind.org #',
                amount='5000',
                description='Some descriptive text for the debit in the dashboard',
                )


