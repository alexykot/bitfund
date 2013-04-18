from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from bitfund.pledger.models import DonationTransaction, DonationSubscription, DonationSubscriptionNeeds, DONATION_TRANSACTION_STATUSES_CHOICES
from bitfund.project.lists import PROJECT_STATUS_CHOICES
from bitfund.project.models import Project, ProjectNeed


class Command(BaseCommand):
    # option_list = BaseCommand.option_list + (
    #     make_option('--delete',
    #                 action='store_true',
    #                 dest='delete',
    #                 default=False,
    #                 help='Delete poll instead of closing it'),
    # )

    help = 'This command fetches all active donation subscriptions and creates new donation transactions for it \n'

    def handle(self, *args, **options):
        donation_subscriptions_list = DonationSubscription.objects.filter(is_active=True)

        for donation_subscription in donation_subscriptions_list:
            project = Project.objects.get(pk=donation_subscription.project_id)
            user = User.objects.get(pk=donation_subscription.user_id)
            if project.status != PROJECT_STATUS_CHOICES.active:
                continue

            donation_subscription_needs_list = DonationSubscriptionNeeds.objects.filter(donation_subscription_id=donation_subscription.id)

            if donation_subscription_needs_list.count() > 0:
                for donation_subscription_need in donation_subscription_needs_list:
                    need = ProjectNeed.objects.get(pk=donation_subscription_need.need_id)
                    if not need.is_public:
                        continue

                    donation_transaction = DonationTransaction()
                    donation_transaction.populatePledgeTransaction(project=project,
                                                                   user=user,
                                                                   pledge_amount=donation_subscription_need.amount,
                                                                   need=need,
                                                                   donation_subscription=donation_subscription)
                    donation_transaction.transaction_status = DONATION_TRANSACTION_STATUSES_CHOICES.pending
                    donation_transaction.save()
                    donation_transaction.createRedonationTransactions()
            else:
                donation_transaction = DonationTransaction()
                donation_transaction.populatePledgeTransaction(project=project,
                                                               user=user,
                                                               pledge_amount=donation_subscription.amount,
                                                               donation_subscription=donation_subscription)
                donation_transaction.save()
                donation_transaction.createRedonationTransactions()
