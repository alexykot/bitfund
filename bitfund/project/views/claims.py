from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.utils.timezone import now

from bitfund.core.settings_split.project import (SITE_CURRENCY_SIGN,
                                           RGBCOLOR_DONUT_CHART_BACKGROUND,
                                           RGBCOLOR_DONUT_CHART_OTHER_SOURCES,
                                           RGBCOLOR_DONUT_CHART_PLEDGES,
                                           RGBCOLOR_DONUT_CHART_REDONATIONS,
                                           )
from bitfund.pledger.models import DonationSubscription
from bitfund.project.decorators import disallow_not_public_unless_maintainer, redirect_active, user_is_not_project_maintainer, user_not_voted_maintainer_yet, user_not_reported_project_yet
from bitfund.project.forms import PledgeNoBudgetProjectForm, VoteMaintainerForm, ClaimProjectForm
from bitfund.project.models import *
from bitfund.project.template_helpers import _prepare_project_budget_template_data

@redirect_active
@disallow_not_public_unless_maintainer
def unclaimed(request, project_key):
    project = get_object_or_404(Project, key=project_key)

    template_data = {'project': project,
                     'request': request,
                     'today': now().today(),
                     'site_currency_sign': SITE_CURRENCY_SIGN,
                     'chartPledgesColor': RGBCOLOR_DONUT_CHART_PLEDGES,
                     'chartRedonationsColor': RGBCOLOR_DONUT_CHART_REDONATIONS,
                     'chartOtherColor': RGBCOLOR_DONUT_CHART_OTHER_SOURCES,
                     'chartBackgroundColor': RGBCOLOR_DONUT_CHART_BACKGROUND,
                     }

    #BUDGET, pledges, redonations, other sources, donut charts radiants
    template_data['budget'] = _prepare_project_budget_template_data(request, project)

    if request.method == 'POST' :
        if not request.user.is_authenticated() :
            redirect('bitfund.project.views.unclaimed', project_key=project.key)

        template_data['pledge_form'] = PledgeNoBudgetProjectForm(request.POST)
        if template_data['pledge_form'].is_valid() :
            if template_data['pledge_form'].cleaned_data['pledge_amount'] > 0 :
                pledge_subscription = (DonationSubscription.objects
                                       .filter(user__id=request.user.id)
                                       .filter(project__id=project.id))
                if pledge_subscription.count() == 1 :
                    pledge_subscription = pledge_subscription[0]
                else :
                    pledge_subscription = DonationSubscription()
                    pledge_subscription.user = request.user
                    pledge_subscription.project = project

                pledge_subscription.amount = template_data['pledge_form'].cleaned_data['pledge_amount']
                pledge_subscription.save()
            else :
                pledge_subscription = (DonationSubscription.objects
                                       .filter(user__id=request.user.id)
                                       .filter(project__id=project.id))
                if pledge_subscription.count() == 1 :
                    pledge_subscription[0].delete()

            return redirect('bitfund.project.views.unclaimed', project_key=project.key)
        else :

            return render_to_response('project/claims_votes/unclaimed.djhtm', template_data, context_instance=RequestContext(request))
    else :
        template_data['pledge_form'] = PledgeNoBudgetProjectForm(initial={'pledge_type':DONATION_TYPES_CHOICES.monthly})
        pledge_subscription = (DonationSubscription.objects
                               .filter(user__id=request.user.id)
                               .filter(project__id=project.id))
        if pledge_subscription.count() == 1 :
            template_data['pledge_subscription'] = pledge_subscription[0]

    return render_to_response('project/claims_votes/unclaimed.djhtm', template_data, context_instance=RequestContext(request))


@redirect_active
@disallow_not_public_unless_maintainer
def claim(request, project_key):
    project = get_object_or_404(Project, key=project_key)

    template_data = {'project': project,
                     'request': request,
                     'today': now().today(),
                     'site_currency_sign': SITE_CURRENCY_SIGN,
                     }

    if request.method == 'POST' :
        template_data['claim_form'] = ClaimProjectForm(data=request.POST, initial={'maintainer_username':request.user.username})
        if template_data['claim_form'].is_valid() :
            project.maintainer_id = request.user.id
            project.maintainer_status = template_data['claim_form'].cleaned_data['maintainer_role']
            project.maintainer_reason_text = template_data['claim_form'].cleaned_data['maintainer_reason_text']
            project.maintainer_reason_url = template_data['claim_form'].cleaned_data['maintainer_reason_url']
            project.status = PROJECT_STATUS_CHOICES.active
            project.is_maintainer_confirmed = False
            project.save()

            return redirect('bitfund.project.views.budget', project_key=project.key)
        else :
            return render_to_response('project/claims_votes/claim.djhtm', template_data, context_instance=RequestContext(request))

    else :
        template_data['claim_form'] = ClaimProjectForm(initial={'maintainer_username':request.user.username})

    return render_to_response('project/claims_votes/claim.djhtm', template_data, context_instance=RequestContext(request))


@login_required
@user_is_not_project_maintainer
@user_not_voted_maintainer_yet
def vote_maintainer(request, project_key, action=None):
    project = get_object_or_404(Project, key=project_key)

    template_data = {'project': project,
                     'request': request,
                     'today': now().today(),
                     'site_currency_sign': SITE_CURRENCY_SIGN,
                     'action' : action,
                     }
    if action == PROJECT_MAINTAINER_VOTE.support :
        initial = {'maintainer':project.maintainer_id, 'vote': True}
    else :
        initial = {'maintainer':project.maintainer_id, 'vote': False}

    if request.method == 'POST' :
        vote_form = VoteMaintainerForm(data=request.POST, project=project, initial=initial)
        if vote_form.is_valid() :
            vote = ProjectMaintainerVote()
            vote.project_id = project.id
            vote.user_id = request.user.id
            vote.maintainer_id = vote_form.cleaned_data['maintainer'].id
            vote.comment = vote_form.cleaned_data['comment']
            vote.vote = vote_form.cleaned_data['vote']
            vote.save()

            return redirect('bitfund.project.views.budget', project_key=project.key)
        else :
            template_data['vote_form'] = vote_form
    else :
        template_data['vote_form'] = VoteMaintainerForm(project=project, initial=initial)



    return render_to_response('project/claims_votes/vote_maintainer.djhtm', template_data, context_instance=RequestContext(request))

@login_required
@user_is_not_project_maintainer
@user_not_reported_project_yet
def report(request, project_key):
    project = get_object_or_404(Project, key=project_key)

    project_report = ProjectReport()
    project_report.project_id = project.id
    project_report.reporter_id = request.user.id
    project_report.save()

    return redirect('bitfund.project.views.budget', project_key=project.key)

