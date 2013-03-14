import os

from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.utils.datetime_safe import datetime
from django.utils.encoding import smart_str
from django.utils.timezone import utc, now

from bitfund.core.settings.project import (SITE_CURRENCY_SIGN,
                                           RGBCOLOR_DONUT_CHART_BACKGROUND,
                                           RGBCOLOR_DONUT_CHART_OTHER_SOURCES,
                                           RGBCOLOR_DONUT_CHART_PLEDGES,
                                           RGBCOLOR_DONUT_CHART_REDONATIONS,
                                           MINIMAL_DEFAULT_PLEDGES_RADIANT,
                                           MINIMAL_DEFAULT_REDONATIONS_RADIANT,
                                           MINIMAL_DEFAULT_OTHER_SOURCES_RADIANT,
                                           )
from bitfund.core.settings.server import STATIC_ROOT, STATICFILES_DIRS
from bitfund.project.decorators import user_is_project_maintainer, disallow_not_public_unless_maintainer, redirect_not_active
from bitfund.project.models import *
from bitfund.project.template_helpers import _prepare_need_item_template_data, _prepare_project_budget_template_data, _prepare_empty_project_template_data, _prepare_goal_item_template_data


@redirect_not_active
@disallow_not_public_unless_maintainer
def budget(request, project_key):
    project = get_object_or_404(Project, key=project_key)

    template_data = {'project': project,
                     'request': request,
                     'today': datetime.utcnow().replace(tzinfo=utc).today(),
                     'site_currency_sign': SITE_CURRENCY_SIGN,
                     'chartPledgesColor': RGBCOLOR_DONUT_CHART_PLEDGES,
                     'chartRedonationsColor': RGBCOLOR_DONUT_CHART_REDONATIONS,
                     'chartOtherColor': RGBCOLOR_DONUT_CHART_OTHER_SOURCES,
                     'chartBackgroundColor': RGBCOLOR_DONUT_CHART_BACKGROUND,
    }

    #GENERAL PROJECT INFO
    if project.maintainer_id == request.user.id :
        template_data['project_edit_access'] = True
    else :
        template_data['project_edit_access'] = False

    #BUDGET, pledges, redonations, other sources, donut charts radiants
    template_data['budget'] = _prepare_project_budget_template_data(request, project)

    #NEEDS
    template_data['project_needs'] = []
    # template_data['project_needs_radiants'] = []
    project_needs = ProjectNeed.objects.filter(project=project.id).filter(is_public=True).order_by('sort_order')
    for need in project_needs :
        template_data['project_needs'].append(_prepare_need_item_template_data(request, project, need))

    template_data['empty_project'] = _prepare_empty_project_template_data(request, project)

    #GOALS
    project_goals = (ProjectGoal.objects
                     .filter(project_id=project.id)
                     .filter(is_public=True)
                     .filter(date_ending__gt=now())
                     .filter(date_starting__lt=now())
                     .order_by('sort_order')
    )
    template_data['project_goals'] = []
    template_data['project_goals_count'] = project_goals.count()
    if template_data['project_goals_count'] > 0 :
        for goal in project_goals:
            template_data['project_goals'].append(_prepare_goal_item_template_data(request, project, goal))

    return render_to_response('project/budget/budget.djhtm', template_data, context_instance=RequestContext(request))


@disallow_not_public_unless_maintainer
def chart_image(request, project_key, need_key=None, goal_key=None):
    chart_filename = 'out.png'
    chart_fullpath = STATICFILES_DIRS[0]+"img/charts/"+chart_filename

    response = HttpResponse(mimetype='image/png')
    response['Content-Length'] = os.path.getsize(chart_fullpath)
    response.write(open(chart_fullpath, 'r').read())

    return response

@disallow_not_public_unless_maintainer
def linked_projects(request, project_key):
    project = get_object_or_404(Project, key=project_key)

    template_data = {'project': project,
                     'request': request,
                     'today': datetime.utcnow().replace(tzinfo=utc).today(),
                     'site_currency_sign': SITE_CURRENCY_SIGN,
                     }

    projects_depending_on_me = (Project_Dependencies.objects
                                .filter(dependee_project=project.id)
                                .order_by('sort_order')
                                .prefetch_related('depender_project')
    )

    if project.maintainer_id == request.user.id :
        template_data['project_edit_access'] = True
    else :
        template_data['project_edit_access'] = False

    template_data['giving_to_bitfund'] = project.checkProjectLinkedToBitFund()
    template_data['refused_to_give_to_bitfund'] = project.is_refused_to_give_to_bitfund

    template_data['projects_depending_on_me'] = []
    template_data['projects_depending_on_me_count'] = projects_depending_on_me.count()
    for project_depending_on_me in projects_depending_on_me:
        template_data['projects_depending_on_me'].append({'id': project_depending_on_me.depender_project.id,
                                                          'key': project_depending_on_me.depender_project.key,
                                                          'title': project_depending_on_me.depender_project.title,
                                                          'logo': project_depending_on_me.depender_project.logo,
                                                          'brief': project_depending_on_me.brief,
                                                          'amount_sum': project_depending_on_me.redonation_amount,
                                                          'amount_percent': project_depending_on_me.redonation_percent,
                                                          })

    projects_i_depend_on = (Project_Dependencies.objects
                            .filter(depender_project=project.id)
                            .order_by('sort_order')
                            .prefetch_related('dependee_project')
    )
    template_data['projects_i_depend_on'] = []
    template_data['projects_i_depend_on_count'] = projects_i_depend_on.count()
    for project_i_depend_on in projects_i_depend_on:
        template_data['projects_i_depend_on'].append({'id': project_i_depend_on.dependee_project.id,
                                                     'key': project_i_depend_on.dependee_project.key,
                                                     'title': project_i_depend_on.dependee_project.title,
                                                     'logo': project_i_depend_on.dependee_project.logo,
                                                     'brief': project_i_depend_on.brief,
                                                     'amount_sum': project_i_depend_on.redonation_amount,
                                                     'amount_percent': project_i_depend_on.redonation_percent,
                                                     })

    return render_to_response('project/linked_projects/linked_projects.djhtm', template_data, context_instance=RequestContext(request))

