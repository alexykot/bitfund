import os
from django.core.files.storage import default_storage
from django.db import transaction
from django.db.models import Sum
from django.utils.timezone import now
import math

from bitfund.core.settings.project import MINIMAL_DEFAULT_PLEDGES_RADIANT, MINIMAL_DEFAULT_REDONATIONS_RADIANT, MINIMAL_DEFAULT_OTHER_SOURCES_RADIANT, CHART_IMAGE_TYPE
from bitfund.core.settings.server import STATIC_ROOT
from bitfund.project.forms import PledgeProjectNeedForm, ProjectNeedForm, PledgeNoBudgetProjectForm, PledgeProjectGoalForm
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
                            .filter(pledger_user_id=request.user.id)
                            .filter(accepting_project_id=project.id)
                            .filter(accepting_need_id=need.id)
                            .exclude(transaction_status=DONATION_TRANSACTION_STATUSES_CHOICES.cancelled)
                            .exclude(transaction_status=DONATION_TRANSACTION_STATUSES_CHOICES.rejected)
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

def _prepare_goal_item_template_data(request, project, goal, pledge_goal_form=None) :
    if pledge_goal_form is None :
        pledge_goal_form = PledgeProjectGoalForm()

    pledges_amount = goal.getTotalPledges() + goal.getTotalRedonations()
    donations_radiant = min(360, round(360 * (pledges_amount / goal.amount)))
    total_percent = int(math.ceil((pledges_amount*100) / goal.amount))

    # other sources are not used at the moment
    # other_sources_amount = goal.getTotalOtherSources()
    # other_sources_radiant = min(360, round(360 * (other_sources_amount / goal.amount)))
    # total_percent = int(math.ceil(((donations_amount+other_sources_amount)*100) / goal.amount))

    if not (donations_radiant) :
        donations_radiant     = MINIMAL_DEFAULT_PLEDGES_RADIANT
        # other_sources_radiant = MINIMAL_DEFAULT_OTHER_SOURCES_RADIANT

    pledging_users_count = (DonationTransaction.objects
                          .filter(accepting_project_id=project.id)
                          .filter(accepting_goal_id=goal.id)
                          .exclude(transaction_status=DONATION_TRANSACTION_STATUSES_CHOICES.cancelled)
                          .exclude(transaction_status=DONATION_TRANSACTION_STATUSES_CHOICES.rejected)
                          .values('pledger_user_id')
                          .distinct()
                          .count()
                         )

    last_transaction = (DonationTransaction.objects
                                  .filter(accepting_project_id=project.id)
                                  .filter(accepting_goal_id=goal.id)
                                  .filter(pledger_user_id=request.user.id)
                                  .exclude(transaction_status=DONATION_TRANSACTION_STATUSES_CHOICES.cancelled)
                                  .exclude(transaction_status=DONATION_TRANSACTION_STATUSES_CHOICES.rejected)
    )
    if last_transaction.count() > 0 :
        last_transaction = last_transaction[0]
    else :
        last_transaction = False


    datetime_to_end = (goal.date_ending - now())
    if goal.date_ending < now() :
        is_expired = True
        days_to_end = 0
        hours_to_end = 0
    else :
        is_expired = False
        days_to_end = int(datetime_to_end.days)
        hours_to_end = int(datetime_to_end.days * 24 + math.ceil(datetime_to_end.seconds / 3600))

    result = {'id': goal.id,
              'key': goal.key,
              'title': goal.title,
              'brief': goal.brief,
              'short_text': goal.short_text,
              'long_text': goal.long_text,
              'youtube_video_id': goal.youtube_video_id,
              'vimeo_video_id': goal.vimeo_video_id,
              'image': goal.image,
              'amount': goal.amount,
              'is_public': goal.is_public,
              'is_expired': is_expired,
              'date_ending': goal.date_ending,
              'days_to_end': days_to_end,
              'hours_to_end': hours_to_end,
              'pledges_amount': pledges_amount,
              'pledges_radiant': donations_radiant,
              'pledging_users_count': pledging_users_count,
              'total_percent': total_percent,
              'pledge_form': pledge_goal_form,
              'last_transaction': last_transaction,
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



def _prepare_empty_project_template_data(request, project, pledge_form=None) :
    template_data = {}
    if pledge_form is None :
            pledge_form = PledgeNoBudgetProjectForm()

    template_data['pledge_form'] = pledge_form

    if request.user.is_authenticated() :
        previous_pledges = (DonationTransaction.objects
                            .filter(pledger_user__id=request.user.id)
                            .filter(accepting_project__id=project.id)
                            .exclude(transaction_status=DONATION_TRANSACTION_STATUSES_CHOICES.cancelled)
                            .exclude(transaction_status=DONATION_TRANSACTION_STATUSES_CHOICES.rejected)
                            .order_by('-transaction_datetime')
        )
        if previous_pledges.count() > 0 :
            template_data['previous_pledges_count'] = previous_pledges.count()
            template_data['last_pledge_transaction'] = previous_pledges[0]

        pledge_subscription_project = (DonationSubscription.objects
                                       .filter(user=request.user, project=project)
                                       .select_related()
        )
        if pledge_subscription_project.count() > 0 :
            pledge_subscription_project = pledge_subscription_project[0]
            pledge_subscription_project_need = (DonationSubscriptionNeeds.objects
                                                .filter(donation_subscription=pledge_subscription_project))
            if pledge_subscription_project_need.count() == 0 :
                template_data['pledge_subscription'] = pledge_subscription_project
                template_data['pledge_form'].initial['pledge_type'] = DONATION_TYPES_CHOICES.monthly
                template_data['pledge_form'].initial['pledge_amount'] = template_data['pledge_subscription'].amount

    return template_data


# gets correct relative path to chart image (can be used either locally to form absolute path or as a part of URL)
# creates required dirs if absent
def _get_chart_relative_filename(project_key, size, need_id=None, goal_id=None) :
    path = ''
    path = os.path.join(path, project_key)

    if need_id is not None :
        path = os.path.join(path, 'need_'+need_id)

    if goal_id is not None :
        path = os.path.join(path, 'need_'+goal_id)

    filename = size+'.'+CHART_IMAGE_TYPE
    relfilepath = os.path.join(path, filename)
    absfilepath = os.path.join(STATIC_ROOT, relfilepath)

    if not os.path.exists(os.path.dirname(absfilepath)) :
        os.makedirs(os.path.dirname(absfilepath))

    return relfilepath