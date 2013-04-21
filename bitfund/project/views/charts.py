import os
import cairoplot

from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from bitfund.core.settings_split.project import (ARGB_DONUT_CHART_PLEDGES,
                                           ARGB_DONUT_CHART_REDONATIONS,
                                           ARGB_DONUT_CHART_OTHER_SOURCES,
                                           ARGB_DONUT_CHART_BACKGROUND,
                                           TOTAL_DEGREES,
                                           CHART_RADIUS_LIST,
                                           CHART_IMAGE_TYPE,
                                           CHART_PARAMS,
                                           MINIMAL_DEFAULT_PLEDGES_DEGREES,
                                           MINIMAL_DEFAULT_OTHER_SOURCES_DEGREES,
                                           MINIMAL_DEFAULT_REDONATIONS_DEGREES)
from bitfund.core.settings_split.server import STATICFILES_DIRS, STATIC_ROOT, MEDIA_ROOT
from bitfund.project.decorators import disallow_not_public_unless_maintainer
from bitfund.project.lists import PROJECT_CHART_SIZES, PROJECT_STATUS_CHOICES
from bitfund.project.models import Project, ProjectGoal, ProjectNeed
from bitfund.project.template_helpers import _prepare_project_budget_template_data, _get_chart_relative_filename, _prepare_goal_item_template_data


@disallow_not_public_unless_maintainer
def chart_image_project(request, project_key, chart_size):
    project = get_object_or_404(Project, key=project_key)

    chart_relpathname = _get_chart_relative_filename(project_key, chart_size)
    chart_abspathname = MEDIA_ROOT+chart_relpathname

    project_monthly_budget = project.getTotalMonthlyBudget()

    pledges_needs_total_sum, pledges_goals_total_sum = project.getTotalMonthlyPledges()
    redonations_total_sum = project.getTotalMonthlyRedonations()
    other_sources_needs_total_sum, other_sources_goals_total_sum  = project.getTotalMonthlyOtherSources()
    other_sources_total_sum = other_sources_needs_total_sum + other_sources_goals_total_sum

    #donut chart radiants
    if project_monthly_budget > 0 :
        pledges_degrees = min(TOTAL_DEGREES,
                              round(TOTAL_DEGREES * (pledges_needs_total_sum / project_monthly_budget)))
        redonations_degrees = min((TOTAL_DEGREES-pledges_degrees),
                                  round(TOTAL_DEGREES * (redonations_total_sum / project_monthly_budget)))
        other_sources_degrees = min((TOTAL_DEGREES-pledges_degrees-redonations_degrees),
                                    round(TOTAL_DEGREES * (other_sources_total_sum / project_monthly_budget)))
    else :
        pledges_degrees = 0
        redonations_degrees = 0
        other_sources_degrees = 0
        if pledges_needs_total_sum > 0 :
            pledges_degrees = TOTAL_DEGREES
        elif redonations_total_sum > 0 :
            redonations_degrees = TOTAL_DEGREES
        elif other_sources_total_sum > 0 :
            other_sources_degrees = TOTAL_DEGREES


    if pledges_needs_total_sum == 0 and redonations_degrees == 0 and other_sources_degrees == 0 :
        pledges_degrees = MINIMAL_DEFAULT_PLEDGES_DEGREES
        redonations_degrees = MINIMAL_DEFAULT_REDONATIONS_DEGREES
        other_sources_degrees = MINIMAL_DEFAULT_OTHER_SOURCES_DEGREES

    chart_data = {'1' : pledges_degrees,
                    '2' : redonations_degrees,
                    '3' : other_sources_degrees,
                    '4' : max(0, (TOTAL_DEGREES-(pledges_degrees+redonations_degrees+other_sources_degrees))),
    }


    chart_colors = [ARGB_DONUT_CHART_PLEDGES, ARGB_DONUT_CHART_REDONATIONS, ARGB_DONUT_CHART_OTHER_SOURCES, ARGB_DONUT_CHART_BACKGROUND]

    chart_image_width = CHART_PARAMS['project']['medium']['w']
    chart_image_height = CHART_PARAMS['project']['medium']['h']
    chart_inner_radius = CHART_PARAMS['project']['medium']['ir']

    for size in PROJECT_CHART_SIZES :
        if size == chart_size :
            chart_image_width = CHART_PARAMS['project'][size]['w']
            chart_image_height = CHART_PARAMS['project'][size]['h']
            chart_inner_radius = CHART_PARAMS['project'][size]['ir']

    cairoplot.donut_plot(chart_abspathname, chart_data, chart_image_width, chart_image_height,
                         background='transparent',
                         inner_radius=chart_inner_radius,
                         colors=chart_colors,
                         radius_list=CHART_RADIUS_LIST)

    response = HttpResponse(mimetype='image/'+CHART_IMAGE_TYPE)
    response['Content-Length'] = os.path.getsize(chart_abspathname)
    response.write(open(chart_abspathname, 'r').read())

    return response

def chart_image_need(request, project_key, need_id, chart_size):
    need = get_object_or_404(ProjectNeed, pk=need_id)

    chart_relpathname = _get_chart_relative_filename(project_key, chart_size, need_id=need_id)
    chart_abspathname = MEDIA_ROOT+chart_relpathname

    pledges_degrees = min(TOTAL_DEGREES, round(TOTAL_DEGREES * ((need.getPledgesMonthlyTotal()) / need.amount)))
    redonations_degrees = min((TOTAL_DEGREES-pledges_degrees), round(TOTAL_DEGREES * ((need.getRedonationsMonthlyTotal()) / need.amount)))
    other_sources_degrees = min((TOTAL_DEGREES-(pledges_degrees+redonations_degrees)), round(TOTAL_DEGREES * ((need.getOtherSourcesMonthlyTotal()) / need.amount)))

    if pledges_degrees == 0 and redonations_degrees == 0 and other_sources_degrees == 0 :
        pledges_degrees = MINIMAL_DEFAULT_PLEDGES_DEGREES
        redonations_degrees = MINIMAL_DEFAULT_REDONATIONS_DEGREES
        other_sources_degrees = MINIMAL_DEFAULT_OTHER_SOURCES_DEGREES

    chart_data = {'1' : pledges_degrees,
                  '2' : redonations_degrees,
                  '3' : other_sources_degrees,
                  '4' : max(0, (TOTAL_DEGREES-(pledges_degrees+other_sources_degrees+redonations_degrees)))
    }


    chart_colors = [ARGB_DONUT_CHART_PLEDGES, ARGB_DONUT_CHART_REDONATIONS, ARGB_DONUT_CHART_OTHER_SOURCES, ARGB_DONUT_CHART_BACKGROUND]

    chart_image_width = CHART_PARAMS['need']['medium']['w']
    chart_image_height = CHART_PARAMS['need']['medium']['h']
    chart_inner_radius = CHART_PARAMS['need']['medium']['ir']

    for size in PROJECT_CHART_SIZES :
        if size == chart_size :
            chart_image_width = CHART_PARAMS['need'][size]['w']
            chart_image_height = CHART_PARAMS['need'][size]['h']
            chart_inner_radius = CHART_PARAMS['need'][size]['ir']

    cairoplot.donut_plot(chart_abspathname, chart_data, chart_image_width, chart_image_height,
                         background='transparent',
                         inner_radius=chart_inner_radius,
                         colors=chart_colors,
                         radius_list=CHART_RADIUS_LIST)

    response = HttpResponse(mimetype='image/png')
    response['Content-Length'] = os.path.getsize(chart_abspathname)
    response.write(open(chart_abspathname, 'r').read())

    return response

def chart_image_goal(request, project_key, goal_key, chart_size):
    project = get_object_or_404(Project, key=project_key)
    goal = get_object_or_404(ProjectGoal, project_id=project.id, key=goal_key)

    chart_relpathname = _get_chart_relative_filename(project_key, chart_size, goal_id=goal.id)
    chart_abspathname = MEDIA_ROOT+chart_relpathname

    pledges_degrees = min(TOTAL_DEGREES, round(TOTAL_DEGREES * ((goal.getTotalPledges()) / goal.amount)))
    other_sources_degrees = min((TOTAL_DEGREES-pledges_degrees), round(TOTAL_DEGREES * ((goal.getTotalOtherSources()) / goal.amount)))

    if pledges_degrees == 0 and other_sources_degrees == 0 :
        pledges_degrees = MINIMAL_DEFAULT_PLEDGES_DEGREES
        other_sources_degrees = MINIMAL_DEFAULT_OTHER_SOURCES_DEGREES

    chart_data = {'1' : pledges_degrees,
                  '2' : 0, # redonations never apply to goals
                  '3' : other_sources_degrees,
                  '4' : max(0, (TOTAL_DEGREES-(pledges_degrees+other_sources_degrees)))
                    }


    chart_colors = [ARGB_DONUT_CHART_PLEDGES, ARGB_DONUT_CHART_REDONATIONS, ARGB_DONUT_CHART_OTHER_SOURCES, ARGB_DONUT_CHART_BACKGROUND]

    chart_image_width = CHART_PARAMS['goal']['medium']['w']
    chart_image_height = CHART_PARAMS['goal']['medium']['h']
    chart_inner_radius = CHART_PARAMS['goal']['medium']['ir']

    for size in PROJECT_CHART_SIZES :
        if size == chart_size :
            chart_image_width = CHART_PARAMS['goal'][size]['w']
            chart_image_height = CHART_PARAMS['goal'][size]['h']
            chart_inner_radius = CHART_PARAMS['goal'][size]['ir']

    cairoplot.donut_plot(chart_abspathname, chart_data, chart_image_width, chart_image_height,
                         background='transparent',
                         inner_radius=chart_inner_radius,
                         colors=chart_colors,
                         radius_list=CHART_RADIUS_LIST)

    response = HttpResponse(mimetype='image/png')
    response['Content-Length'] = os.path.getsize(chart_abspathname)
    response.write(open(chart_abspathname, 'r').read())

    return response
