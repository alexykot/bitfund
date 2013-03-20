from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.utils.timezone import now

from bitfund.core.settings.project import (SITE_CURRENCY_SIGN,
                                           RGBCOLOR_DONUT_CHART_BACKGROUND,
                                           RGBCOLOR_DONUT_CHART_OTHER_SOURCES,
                                           RGBCOLOR_DONUT_CHART_PLEDGES,
                                           RGBCOLOR_DONUT_CHART_REDONATIONS,
                                           )
from bitfund.pledger.models import DonationSubscription
from bitfund.project.decorators import disallow_not_public_unless_maintainer, redirect_active
from bitfund.project.forms import PledgeNoBudgetProjectForm
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

            return render_to_response('project/unclaimed.djhtm', template_data, context_instance=RequestContext(request))
    else :
        template_data['pledge_form'] = PledgeNoBudgetProjectForm(initial={'pledge_type':DONATION_TYPES_CHOICES.monthly})
        pledge_subscription = (DonationSubscription.objects
                               .filter(user__id=request.user.id)
                               .filter(project__id=project.id))
        if pledge_subscription.count() == 1 :
            template_data['pledge_subscription'] = pledge_subscription[0]

    return render_to_response('project/unclaimed.djhtm', template_data, context_instance=RequestContext(request))

@redirect_active
@disallow_not_public_unless_maintainer
def claim(request, project_key):
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

    return render_to_response('project/claim.djhtm', template_data, context_instance=RequestContext(request))

@disallow_not_public_unless_maintainer
def maintainer_verification(request, project_key):
    project = get_object_or_404(Project, key=project_key)

    template_data = {'project': project,
                     'request': request,
                     'today': now().today(),
                     'site_currency_sign': SITE_CURRENCY_SIGN,
                     }

    return render_to_response('project/claim.djhtm', template_data, context_instance=RequestContext(request))

@disallow_not_public_unless_maintainer
def vote_maintainer(request, project_key, action=None):
    project = get_object_or_404(Project, key=project_key)

    template_data = {'project': project,
                     'request': request,
                     'today': now().today(),
                     'site_currency_sign': SITE_CURRENCY_SIGN,
                     }

    return render_to_response('project/vote_maintainer.djhtm', template_data, context_instance=RequestContext(request))
