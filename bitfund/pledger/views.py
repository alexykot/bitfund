from django.http import HttpResponseNotFound
from django.contrib.auth.models import User
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from bitfund.core.settings.project import SITE_CURRENCY_SIGN
from bitfund.pledger.models import Profile
from bitfund.pledger.template_helpers import _prepare_user_public_template_data, _prepare_user_pledges_monthly_history_data
from bitfund.project.forms import CreateProjectForm
from bitfund.project.lists import PROJECT_STATUS_CHOICES
from bitfund.project.models import Project


def user_profile_overview(request, username=None, external_service=None, external_username=None):
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

        return render_to_response('pledger/profile/public.djhtm', template_data, context_instance=RequestContext(request))
    else :
        request.user.public = _prepare_user_public_template_data(request, request.user)
        #request.user.pledges_history = _prepare_user_pledges_monthly_history_data(request, request.user)
        template_data['request'] = request
        template_data['profile'] = profile
        print template_data['profile'].api_token

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

        return render_to_response('pledger/profile/own_overview.djhtm', template_data, context_instance=RequestContext(request))


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
        #project.total_received_this_month = project.getTotalMonthlyDonations()

        #monthly_budget = project.getTotalMonthlyBudget()


        template_data['similar_projects_list'].append(project)


    return render_to_response('pledger/profile/ajax-existing_similar_projects.djhtm', template_data, context_instance=RequestContext(request))

@login_required
def user_profile_projects(request):
    template_data = {'request': request,
                     'today': now().today(),
                     'site_currency_sign': SITE_CURRENCY_SIGN,
                     }





    return render_to_response('pledger/profile/projects.djhtm', {}, context_instance=RequestContext(request))

@login_required
def attach_bank_card(request):
    return render_to_response('pledger/profile/attach_bank_card.djhtm', {}, context_instance=RequestContext(request))

@login_required
def attach_bank_account(request):
    return render_to_response('pledger/profile/attach_bank_account.djhtm', {}, context_instance=RequestContext(request))
