from bitfund.pledger.models import DonationTransaction, DonationSubscription, DonationSubscriptionNeeds
from bitfund.project.forms import PledgeProjectNeedForm
from bitfund.project.lists import DONATION_TYPES_CHOICES


def _prepare_need_item_template_data(request, project, need, pledge_need_form=None) :
    if pledge_need_form is None :
        pledge_need_form = PledgeProjectNeedForm()

    pledge_need_form.prefix = 'need-'+str(need.id)

    last_pledge_transaction = False
    previous_pledges_count = 0
    pledge_subscription = False
    if request.user.is_authenticated() :
        previous_pledges = (DonationTransaction.objects
                             .filter(pledger_user__id=request.user.id,
                                     accepting_project__id=project.id,
                                     accepting_need__id=need.id)
                             .order_by('-transaction_datetime')
                            )
        if previous_pledges.count() > 0 :
            last_pledge_transaction = previous_pledges[0]
            previous_pledges_count = previous_pledges.count()

        pledge_subscription_project = (DonationSubscription.objects
                                       .filter(user=request.user, project=project)
                                       .select_related()
        )
        if pledge_subscription_project.count() > 0 :
            pledge_subscription_project = pledge_subscription_project[0]
            pledge_subscription_project_need = (DonationSubscriptionNeeds.objects
                                                .filter(donation_subscription=pledge_subscription_project, need=need))
            if pledge_subscription_project_need.count() > 0 :
                pledge_subscription = pledge_subscription_project_need[0]
                pledge_need_form.initial['pledge_amount'] = pledge_subscription.amount
                pledge_need_form.initial['pledge_type'] = DONATION_TYPES_CHOICES.monthly

    user_is_project_maintainer = False
    if request.user.id == project.maintainer_id :
        user_is_project_maintainer = True

    result = {'id': need.id,
              'title': need.title,
              'brief': need.brief,
              'amount': need.amount,
              'full_total': need.getPledgesMonthlyTotal() + need.getRedonationsMonthlyTotal() +
                            need.getOtherSourcesMonthlyTotal(),
              'pledge_form': pledge_need_form,
              'last_pledge_transaction': last_pledge_transaction,
              'previous_pledges_count': previous_pledges_count,
              'pledge_subscription': pledge_subscription,
              'user_is_project_maintainer': user_is_project_maintainer,

    }

    return result
