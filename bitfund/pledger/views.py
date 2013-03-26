from django.db.models.aggregates import Sum
from django.http import HttpResponseNotFound
from django.contrib.auth.models import User
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from django.utils.datetime_safe import datetime

from bitfund.core.settings.project import SITE_CURRENCY_SIGN
from bitfund.pledger.models import Profile, DonationTransaction, DONATION_TRANSACTION_STATUSES_CHOICES
from bitfund.pledger.template_helpers import _prepare_user_public_template_data, _prepare_user_pledges_monthly_history_data, _prepare_project_budget_history_template_data
from bitfund.project.forms import CreateProjectForm
from bitfund.project.lists import PROJECT_STATUS_CHOICES
from bitfund.project.models import Project, ProjectGoal
from bitfund.project.template_helpers import _prepare_project_template_data, _prepare_goal_item_template_data


def profile(request, username=None, external_service=None, external_username=None):
    template_data = {'request': request,
                     'today': now().today(),
                     'site_currency_sign': SITE_CURRENCY_SIGN,
                     }

    if username is not None :
        user = get_object_or_404(User, username=username)

    elif external_service is not None and external_username is not None:
        user = None
        #@TODO identify user by external system ID and external username
    elif request.user.is_authenticated():
        user = request.user

    if user.id > 0 :
        profile = get_object_or_404(Profile, user_id=user.id)

    if user.id != request.user.id :
        user.public = _prepare_user_public_template_data(request, user)
        template_data['user'] = user
        template_data['profile'] = profile

        return render_to_response('pledger/public.djhtm', template_data, context_instance=RequestContext(request))
    else :
        request.user.public = _prepare_user_public_template_data(request, request.user)
        request.user.pledges_history = _prepare_user_pledges_monthly_history_data(request, request.user)
        template_data['request'] = request
        template_data['profile'] = profile
        template_data['current_page'] = 'profile'

        if request.method == 'POST' :
            template_data['create_project_form'] = CreateProjectForm(request.POST)
            if template_data['create_project_form'].is_valid() :
                project = Project()
                project.title = template_data['create_project_form'].cleaned_data['title']
                project.key = Project.slugifyKey(project.title)
                project.is_public = False
                project.maintainer_id = request.user.id
                project.status = PROJECT_STATUS_CHOICES.active
                project.save()
                return redirect('bitfund.project.views.budget_edit', project_key=project.key)

        else :
            template_data['create_project_form'] = CreateProjectForm()

        return render_to_response('pledger/own_overview.djhtm', template_data, context_instance=RequestContext(request))


def existing_similar_projects(request):
    template_data = {'request': request,
                     'today': now().today(),
                     'site_currency_sign': SITE_CURRENCY_SIGN,
                     }

    search_string = request.GET['search_string']

    similar_projects_list = (Project.objects
                             .exclude(status=PROJECT_STATUS_CHOICES.inactive)
                             .exclude(status=PROJECT_STATUS_CHOICES.archived)
                             .exclude(is_public=False)
                             .filter(title__icontains=search_string)
                            )

    if similar_projects_list.count() == 0 :
        return HttpResponseNotFound()

    template_data['project_statuses'] = PROJECT_STATUS_CHOICES
    template_data['similar_projects_list'] = []
    for project in similar_projects_list :
        project.total_received_this_month = project.getTotalMonthlyDonations()
        monthly_budget = project.getTotalMonthlyBudget()
        if monthly_budget > 0 :
            project.total_budget_fulfillment_percent = project.total_received_this_month/monthly_budget*100
        else :
            project.total_budget_fulfillment_percent = -1

        template_data['similar_projects_list'].append(project)


    return render_to_response('pledger/ajax-existing_similar_projects.djhtm', template_data, context_instance=RequestContext(request))

@login_required
def projects(request, project_key=None):
    template_data = {'today': now().today(),
                     'site_currency_sign': SITE_CURRENCY_SIGN,
                     'current_page': 'projects',
                     }

    projects_list = Project.objects.filter(maintainer_id=request.user.id)
    template_data['projects_list'] = []
    for project in projects_list :
        project_data = _prepare_project_template_data(request, project)

        template_data['projects_list'].append(project_data)

        if project_key is None :
            project_key = project_data.key

    current_project = get_object_or_404(Project, key=project_key)

    template_data['current_project'] = _prepare_project_template_data(request, current_project)
    template_data['current_project'].active_needs_count = current_project.getNeedsCount()
    template_data['current_project'].active_goals_count = (ProjectGoal.objects
                                                           .filter(project_id=current_project.id)
                                                           .filter(is_public=True)
                                                           .count()
                                                            )
    active_goals_list = (ProjectGoal.objects
                                                         .filter(project_id=current_project.id)
                                                         .filter(is_public=True)
                                                            )

    template_data['current_project'].active_goals_list = []
    for goal in active_goals_list :
        template_data['current_project'].active_goals_list.append(_prepare_goal_item_template_data(request, current_project, goal))

    request.user.public = _prepare_user_public_template_data(request, request.user)

    total_transactions = (DonationTransaction.objects
                          .filter(accepting_project_id=current_project.id)
                          .exclude(transaction_status=DONATION_TRANSACTION_STATUSES_CHOICES.cancelled)
                          .exclude(transaction_status=DONATION_TRANSACTION_STATUSES_CHOICES.rejected)
                          .count()
    )

    template_data['current_project'].budget_history = []
    if total_transactions > 0 :
        month_upper_bound = (DonationTransaction.objects
                             .filter(accepting_project_id=current_project.id)
                             .exclude(transaction_status=DONATION_TRANSACTION_STATUSES_CHOICES.cancelled)
                             .exclude(transaction_status=DONATION_TRANSACTION_STATUSES_CHOICES.rejected)
                             .order_by('-transaction_datetime')[0]
        ).transaction_datetime

        month_lower_bound = (DonationTransaction.objects
                             .filter(accepting_project_id=current_project.id)
                             .exclude(transaction_status=DONATION_TRANSACTION_STATUSES_CHOICES.cancelled)
                             .exclude(transaction_status=DONATION_TRANSACTION_STATUSES_CHOICES.rejected)
                             .order_by('transaction_datetime')[0]
        ).transaction_datetime

        index_year = int(month_lower_bound.year)
        index_month = int(month_lower_bound.month)
        while True :
            current_month = datetime(year=index_year, month=index_month, day=1, tzinfo=now().tzinfo)
            if current_month > month_upper_bound :
                break

            index_month = index_month+1
            if index_month > 12 :
                index_year = index_year+1
                index_month = 1

            if now().year == current_month.year and now().month == current_month.month :
                template_data['current_project'].budget = _prepare_project_budget_history_template_data(request, current_project, current_month)
            else :
                template_data['current_project'].budget_history.append(_prepare_project_budget_history_template_data(request, current_project, current_month))

    template_data['request'] = request

    return render_to_response('pledger/projects.djhtm', template_data, context_instance=RequestContext(request))

@login_required
def attach_bank_card(request):
    return render_to_response('pledger/attach_bank_card.djhtm', {}, context_instance=RequestContext(request))

@login_required
def attach_bank_account(request):
    return render_to_response('pledger/attach_bank_account.djhtm', {}, context_instance=RequestContext(request))
