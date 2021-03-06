import os
import re
import math

from django.db.models import Sum
from django.utils.timezone import utc, now

from bitfund.core.settings_split.project import CHART_IMAGE_TYPE, PROJECTS_MEDIA_DIR, CHART_PLEDGES_RGB, CHART_PLEDGES_ALPHA, CHART_PLEDGES_STYLE, CHART_REDONATIONS_RGB, CHART_OTHER_SOURCES_RGB, CHART_BACKGROUND_RGB
from bitfund.core.settings_split.server import MEDIA_ROOT
from bitfund.project.forms import PledgeProjectNeedForm, PledgeNoBudgetProjectForm, PledgeProjectGoalForm
from bitfund.project.lists import DONATION_TYPES_CHOICES
from bitfund.project.models import ProjectNeed, ProjectGoal, ProjectMaintainerVote
from bitfund.pledger.models import DonationTransaction, DonationSubscription, DonationSubscriptionNeeds, DONATION_TRANSACTION_STATUSES_CHOICES


def _prepare_project_template_data(request, project):

    project.total_donations = project.getTotalMonthlyDonations()
    project.monthly_budget = project.getTotalMonthlyBudget()
    if project.monthly_budget > 0 :
        project.budget_filled_percent = project.total_donations/project.monthly_budget*100
    else :
        project.budget_filled_percent = -1

    return project


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

    donated_total = need.getPledgesMonthlyTotal() + need.getRedonationsMonthlyTotal() + need.getOtherSourcesMonthlyTotal()

    if need.amount > 0 :
        pledged_percent = donated_total/need.amount*100
    else :
        pledged_percent = -1

    result = {'id': need.id,
              'title': need.title,
              'brief': need.brief,
              'amount': need.amount,
              'is_public': need.is_public,
              'sort_order': need.sort_order,
              'full_total': donated_total,
              'pledged_percent': pledged_percent,
              'pledge_form': pledge_need_form,
              'last_pledge_transaction': last_pledge_transaction,
              'previous_pledges_count': previous_pledges_count,
              'pledge_subscription': pledge_subscription,
              'user_is_project_maintainer': user_is_project_maintainer,
    }

    return result

def _prepare_goal_item_template_data(request, project, goal, pledge_goal_form=None) :
    if pledge_goal_form is None :
        pledge_goal_form = PledgeProjectGoalForm()

    pledges_amount = goal.getTotalPledges() + goal.getTotalRedonations()
    if goal.amount > 0 :
        total_percent = int(math.ceil((pledges_amount*100) / goal.amount))
    else :
        total_percent = -1

        # other sources are not used at the moment
    # other_sources_amount = goal.getTotalOtherSources()
    # total_percent = int(math.ceil(((donations_amount+other_sources_amount)*100) / goal.amount))


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


    is_time_uncertain = False
    is_expired = False
    is_editable = True
    days_to_end = 0
    hours_to_end = 0
    if goal.date_ending is not None and goal.date_starting is not None :
        if goal.date_ending < now() :
            is_expired = True
            is_editable = False
        elif goal.date_starting < now() :
            is_editable = False
            datetime_to_end = (goal.date_ending - now())
            days_to_end = int(datetime_to_end.days)
            hours_to_end = int(datetime_to_end.days * 24 + math.ceil(datetime_to_end.seconds / 3600))
    else :
        is_time_uncertain = True

    goal.is_editable = is_editable
    goal.is_publisheable = goal.isValidForPublic()
    goal.is_expired = is_expired
    goal.is_time_uncertain = is_time_uncertain
    goal.days_to_end = days_to_end
    goal.hours_to_end = hours_to_end
    goal.pledges_amount = pledges_amount
    goal.pledging_users_count = pledging_users_count
    goal.total_percent = total_percent
    goal.pledge_form = pledge_goal_form
    goal.last_transaction = last_transaction

    return goal

# used on the project.views.budget page mainly
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
        budget_data['total_gained_percent'] = int(round(
            ((pledges_needs_total_sum+redonations_total_sum+other_sources_total_sum) * 100) / budget_data['project_monthly_budget']))
    else :
        budget_data['total_gained_percent'] = -1

    project_subscriptions_list = DonationSubscription.objects.filter(project=project.id).filter(is_active=True)
    budget_data['project_subscriptions_count'] = 0
    budget_data['project_subscriptions_total'] = 0
    for project_subscription in project_subscriptions_list:
        budget_data['project_subscriptions_count'] = budget_data['project_subscriptions_count'] + 1
        if project_subscription.amount > 0:
            budget_data['project_subscriptions_total'] = budget_data['project_subscriptions_total'] + project_subscription.amount
        else:
            project_subscription_needs_total = (DonationSubscriptionNeeds.objects
                                                .filter(donation_subscription_id=project_subscription.id)
                                                .aggregate(Sum('amount'))['amount__sum'])
            budget_data['project_subscriptions_total'] = budget_data['project_subscriptions_total'] + project_subscription_needs_total




    return budget_data


def _prepare_empty_project_template_data(request, project, pledge_form=None) :
    template_data = {}
    if pledge_form is None :
            pledge_form = PledgeNoBudgetProjectForm()

    template_data['pledge_form'] = pledge_form

    if request.user.is_authenticated() :
        previous_pledges = (DonationTransaction.objects
                            .filter(pledger_user_id=request.user.id)
                            .filter(accepting_project_id=project.id)
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
def _get_chart_relative_filename(project_key, chart_size, need_id=None, goal_id=None) :
    path = ''
    path = os.path.join(path, PROJECTS_MEDIA_DIR, project_key)

    if need_id is not None:
        path = os.path.join(path, 'need_' + str(need_id))

    if goal_id is not None:
        path = os.path.join(path, 'need_' + str(goal_id))

    filename = chart_size + '.' + CHART_IMAGE_TYPE
    relfilepath = os.path.join(path, filename)
    absfilepath = os.path.join(MEDIA_ROOT, relfilepath)

    if not os.path.exists(os.path.dirname(absfilepath)):
        os.makedirs(os.path.dirname(absfilepath))

    return relfilepath

def _get_logo_relative_filename(project_key, logo_filename) :
    relfilepath = os.path.join(PROJECTS_MEDIA_DIR, project_key, logo_filename)
    absfilepath = os.path.join(MEDIA_ROOT, relfilepath)

    if not os.path.exists(os.path.dirname(absfilepath)):
        os.makedirs(os.path.dirname(absfilepath))

    return relfilepath


# gets request and returns a tuple of ('int chart_size in px',
#                                       'pledges_color in cairo rgbas',
#                                       'redonations_color in cairo rgbas',
#                                       'other_sources_color in cairo rgbas',
#                                       'background_color in cairo rgbas'
#                                         )
def _parse_request_chart_params(request):
    if 'size' in request.GET:
        if request.GET['size'] == 'large' or request.GET['size'] == 'medium' or request.GET['size'] == 'small':
            chart_size = str(request.GET['size'])
        elif is_number(request.GET['size']):
            chart_size = str(int(request.GET['size']))
        else:
            chart_size = 'default'
    else:
        chart_size = 'default'


    if 'pledges_rgb' in request.GET and re.search('^[a-fA-F0-9]{6}$', request.GET['pledges_rgb']):
        pledges_rgb = str(request.GET['pledges_rgb'])
    else:
        pledges_rgb = CHART_PLEDGES_RGB
    pledges_rgb = hex_to_rgb(pledges_rgb)
    pledges_rgbas = (round(pledges_rgb[0] / 255.0, 3),
                     round(pledges_rgb[1] / 255.0, 3),
                     round(pledges_rgb[2] / 255.0, 3),
                     CHART_PLEDGES_ALPHA,
                     CHART_PLEDGES_STYLE)

    if 'redonations_rgb' in request.GET and re.search('^[a-fA-F0-9]{6}$', request.GET['redonations_rgb']):
        redonations_rgb = str(request.GET['redonations_rgb'])
    else:
        redonations_rgb = CHART_REDONATIONS_RGB
    redonations_rgb = hex_to_rgb(redonations_rgb)
    redonations_rgbas = (round(redonations_rgb[0] / 255.0, 3),
                         round(redonations_rgb[1] / 255.0, 3),
                         round(redonations_rgb[2] / 255.0, 3),
                         CHART_PLEDGES_ALPHA,
                         CHART_PLEDGES_STYLE)

    if 'other_sources_rgb' in request.GET and re.search('^[a-fA-F0-9]{6}$', request.GET['other_sources_rgb']):
        other_sources_rgb = str(request.GET['other_sources_rgb'])
    else:
        other_sources_rgb = CHART_OTHER_SOURCES_RGB
    other_sources_rgb = hex_to_rgb(other_sources_rgb)
    other_sources_rgbas = (round(other_sources_rgb[0] / 255.0, 3),
                           round(other_sources_rgb[1] / 255.0, 3),
                           round(other_sources_rgb[2] / 255.0, 3),
                           CHART_PLEDGES_ALPHA,
                           CHART_PLEDGES_STYLE)

    if 'background_rgb' in request.GET and re.search('^[a-fA-F0-9]{6}$', request.GET['background_rgb']):
        background_rgb = str(request.GET['background_rgb'])
    else:
        background_rgb = CHART_BACKGROUND_RGB
    background_rgb = hex_to_rgb(background_rgb)
    background_rgbas = (round(background_rgb[0] / 255.0, 3),
                        round(background_rgb[1] / 255.0, 3),
                        round(background_rgb[2] / 255.0, 3),
                        CHART_PLEDGES_ALPHA,
                        CHART_PLEDGES_STYLE)


    return chart_size, pledges_rgbas, redonations_rgbas, other_sources_rgbas, background_rgbas

#converts CSS RGB hex string '#FFFFFF' into a tuple (255,255,255). leading # is optional
def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i+lv/3], 16) for i in range(0, lv, lv/3))

#converts tuple of (255,255,255) into CSS RGB string '#FFFFFF' with leading #
def rgb_to_hex(rgb):
    r = rgb[0]
    g = rgb[1]
    b = rgb[2]
    return '#%02X%02X%02X' % (r,g,b)

#tests if the value is a parsable number
def is_number(val):
    try:
        float(val)
        return True
    except ValueError:
        return False