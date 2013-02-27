from django.db import transaction
from django.db.models import Sum
from django.utils.timezone import now

from bitfund.core.settings.project import MINIMAL_DEFAULT_PLEDGES_RADIANT, MINIMAL_DEFAULT_REDONATIONS_RADIANT, MINIMAL_DEFAULT_OTHER_SOURCES_RADIANT
from bitfund.project.forms import PledgeProjectNeedForm, CreateProjectNeedForm
from bitfund.project.lists import DONATION_TYPES_CHOICES
from bitfund.project.models import ProjectNeed, ProjectGoal
from bitfund.pledger.models import DonationTransaction, DonationSubscription, DonationSubscriptionNeeds, DONATION_TRANSACTION_STATUSES_CHOICES


def _prepare_need_item_template_data(request, project, need, pledge_need_form=None) :
    if pledge_need_form is None :
        pledge_need_form = PledgeProjectNeedForm()

    pledge_need_form.prefix = 'need-'+str(need.id)

    last_pledge_transaction = False
    previous_pledges_count = 0
    pledge_subscription = False
    if request.user.is_authenticated() :
        previous_pledges = (DonationTransaction.objects
                            .filter(pledger_user__id=request.user.id)
                            .filter(accepting_project__id=project.id)
                            .filter(accepting_need__id=need.id)
                            .exclude(transaction_status=DONATION_TRANSACTION_STATUSES_CHOICES.cancelled)
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


    need_pledges_n_redonations_total = need.getPledgesMonthlyTotal() + need.getRedonationsMonthlyTotal()
    need_other_sources_total = need.getOtherSourcesMonthlyTotal()

    if (need.amount > 0) :
        donations_sum_radiant = min(360, round(360 * (need_pledges_n_redonations_total / need.amount)))
        other_sources_radiant = min(360, round(360 * (need_other_sources_total / need.amount)))
    else :
        donations_sum_radiant = 360
        other_sources_radiant = 360
    if donations_sum_radiant == 0 and other_sources_radiant == 0 :
        donations_sum_radiant = MINIMAL_DEFAULT_PLEDGES_RADIANT
        other_sources_radiant = MINIMAL_DEFAULT_OTHER_SOURCES_RADIANT

    result = {'id': need.id,
              'title': need.title,
              'brief': need.brief,
              'amount': need.amount,
              'is_public': need.is_public,
              'sort_order': need.sort_order,
              'full_total': need.getPledgesMonthlyTotal() + need.getRedonationsMonthlyTotal() +
                            need.getOtherSourcesMonthlyTotal(),
              'pledge_form': pledge_need_form,
              'last_pledge_transaction': last_pledge_transaction,
              'previous_pledges_count': previous_pledges_count,
              'pledge_subscription': pledge_subscription,
              'user_is_project_maintainer': user_is_project_maintainer,
              'donations_sum_radiant': donations_sum_radiant,
              'other_sources_radiant': other_sources_radiant,

    }

    return result

def _prepare_project_budget_template_data(request, project) :
    budget_data = {}

    #BUDGET
    project_needs = ProjectNeed.objects.filter(project=project.id).filter(is_public=True).order_by('sort_order')
    budget_data['project_needs_count'] = project_needs.count()
    budget_data['project_goals_count'] = (ProjectGoal.objects.filter(project=project, is_public=True,
                                                      date_ending__gt=now(), date_starting__lt=now()).count())
    budget_data['project_monthly_budget'] = (project_needs.aggregate(Sum('amount'))['amount__sum']) or 0


    project_needs = ProjectNeed.objects.filter(project=project.id).filter(is_public=True).order_by('sort_order')
    budget_data['project_monthly_budget'] = (project_needs.aggregate(Sum('amount'))['amount__sum']) or 0

    #pledges
    pledges_needs_total_sum, pledges_goals_total_sum = project.getTotalMonthlyPledges()
    budget_data['donations_total_sum'] = pledges_needs_total_sum
    budget_data['donations_total_pledgers'] = project.getTotalMonthlyBackers()

    #redonations
    projects_i_depend_on_count, projects_depending_on_me_count = project.getLinkedProjectsCount()
    redonations_total_sum = project.getTotalMonthlyRedonations()
    budget_data['redonations_total_sum'] = redonations_total_sum
    budget_data['depending_on_me_projects_count'] = projects_depending_on_me_count
    budget_data['i_depend_on_projects_count'] = projects_i_depend_on_count
    budget_data['i_depend_on_transfer_percent'] = project.getRedonationsPercent()

    #other sources
    other_sources_needs_total_sum, other_sources_goals_total_sum  = project.getTotalMonthlyOtherSources()
    other_sources_total_sum = other_sources_needs_total_sum + other_sources_goals_total_sum
    budget_data['other_sources_total_sum'] = other_sources_total_sum

    #donut chart radiants
    if (budget_data['project_monthly_budget'] > 0) :
        budget_data['pledges_radiant'] = min(360, round(
            360 * (pledges_needs_total_sum / budget_data['project_monthly_budget'])))
        budget_data['redonations_radiant'] = min(360, round(
            360 * (redonations_total_sum / budget_data['project_monthly_budget'])))
        budget_data['other_sources_radiant'] = min(360, round(
            360 * (other_sources_total_sum / budget_data['project_monthly_budget'])))

        budget_data['total_gained_percent'] = int(round(
            ((pledges_needs_total_sum+redonations_total_sum+other_sources_total_sum) * 100) / budget_data['project_monthly_budget']))
        if not (budget_data['pledges_radiant'] or budget_data['redonations_radiant'] or budget_data['other_sources_radiant']) :
            budget_data['pledges_radiant'] = MINIMAL_DEFAULT_PLEDGES_RADIANT
            budget_data['redonations_radiant'] = MINIMAL_DEFAULT_REDONATIONS_RADIANT
            budget_data['other_sources_radiant'] = MINIMAL_DEFAULT_OTHER_SOURCES_RADIANT
    else :
        if pledges_needs_total_sum > 0 :
            budget_data['pledges_radiant'] = 360
        else :
            budget_data['pledges_radiant'] = MINIMAL_DEFAULT_PLEDGES_RADIANT
        if redonations_total_sum > 0 :
            budget_data['redonations_radiant'] = 360
        else :
            budget_data['redonations_radiant'] = MINIMAL_DEFAULT_REDONATIONS_RADIANT
        if other_sources_total_sum > 0 :
            budget_data['other_sources_radiant'] = 360
        else :
            budget_data['other_sources_radiant'] = MINIMAL_DEFAULT_OTHER_SOURCES_RADIANT
        budget_data['total_gained_percent'] = -1

    return budget_data

def _prepare_project_crud_need_form_template_data(request, project, need) :
    template_data = {}

    template_data['need_form'] = CreateProjectNeedForm(instance=need)

    return template_data
