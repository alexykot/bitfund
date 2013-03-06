from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.timezone import now

from bitfund.core.settings.project import (SITE_CURRENCY_SIGN,
                                           RGBCOLOR_DONUT_CHART_BACKGROUND,
                                           RGBCOLOR_DONUT_CHART_OTHER_SOURCES,
                                           RGBCOLOR_DONUT_CHART_PLEDGES,
                                           RGBCOLOR_DONUT_CHART_REDONATIONS,
                                           )
from bitfund.project.decorators import disallow_not_public_unless_maintainer, redirect_active
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

@redirect_active
@disallow_not_public_unless_maintainer
def maintainer_verification(request, project_key):
    return render_to_response('project/claim.djhtm', template_data, context_instance=RequestContext(request))

@redirect_active
@disallow_not_public_unless_maintainer
def maintainer_verification(request, project_key):
    return render_to_response('project/claim.djhtm', template_data, context_instance=RequestContext(request))

@redirect_active
@disallow_not_public_unless_maintainer
def vote_maintainer(request, project_key):
    return render_to_response('project/claim.djhtm', template_data, context_instance=RequestContext(request))
