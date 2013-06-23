from decimal import Decimal
import os
import re
import cairoplot

from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from bitfund.core.settings_split.project import (  TOTAL_DEGREES,
                                                   CHART_RADIUS_LIST,
                                                   CHART_IMAGE_TYPE,
                                                   CHART_PARAMS,
                                                   MINIMAL_DEFAULT_PLEDGES_DEGREES,
                                                   MINIMAL_DEFAULT_OTHER_SOURCES_DEGREES,
                                                   MINIMAL_DEFAULT_REDONATIONS_DEGREES,
                                                   CHART_INNER_RADIUS
                                                   )
from bitfund.core.settings_split.server import MEDIA_ROOT
from bitfund.project.decorators import disallow_not_public_unless_maintainer
from bitfund.project.models import Project, ProjectGoal, ProjectNeed
from bitfund.project.template_helpers import _get_chart_relative_filename, hex_to_rgb, is_number, _parse_request_chart_params


@disallow_not_public_unless_maintainer
def chart_image_project(request, project_key):
    project = get_object_or_404(Project, key=project_key)

    chart_size, pledges_rgbas, redonations_rgbas, other_sources_rgbas, backcircle_rgbas = _parse_request_chart_params(request)

    chart_colors = [pledges_rgbas, redonations_rgbas, other_sources_rgbas, backcircle_rgbas]

    if chart_size in CHART_PARAMS['project']:
        chart_image_width = CHART_PARAMS['project'][chart_size]['w']
        chart_image_height = CHART_PARAMS['project'][chart_size]['h']
    else:
        chart_image_width = chart_image_height = int(chart_size)

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



    cairoplot.donut_plot(name=chart_abspathname,
                         data=chart_data,
                         width=chart_image_width, height=chart_image_height,
                         background='transparent',
                         inner_radius=CHART_INNER_RADIUS,
                         radius_list=CHART_RADIUS_LIST,
                         colors=chart_colors
                         )

    response = HttpResponse(mimetype='image/'+CHART_IMAGE_TYPE)
    response['Content-Length'] = os.path.getsize(chart_abspathname)
    response.write(open(chart_abspathname, 'r').read())

    return response

def chart_image_need(request, project_key, need_id):
    need = get_object_or_404(ProjectNeed, pk=need_id)

    chart_size, pledges_rgbas, redonations_rgbas, other_sources_rgbas, backcircle_rgbas = _parse_request_chart_params(request)

    chart_colors = [pledges_rgbas, redonations_rgbas, other_sources_rgbas, backcircle_rgbas]

    if chart_size in CHART_PARAMS['need']:
        chart_image_width = CHART_PARAMS['need'][chart_size]['w']
        chart_image_height = CHART_PARAMS['need'][chart_size]['h']
    else:
        chart_image_width = chart_image_height = int(chart_size)

    chart_relpathname = _get_chart_relative_filename(project_key, chart_size, need_id=need_id)
    chart_abspathname = MEDIA_ROOT+chart_relpathname

    pledges_degrees = min(TOTAL_DEGREES, Decimal(TOTAL_DEGREES * ((need.getPledgesMonthlyTotal()) / need.amount)).quantize(Decimal('1') ))
    redonations_degrees = min((TOTAL_DEGREES-pledges_degrees),
                              Decimal(TOTAL_DEGREES * ((need.getRedonationsMonthlyTotal()) / need.amount)).quantize(Decimal('1')) )
    other_sources_degrees = min((TOTAL_DEGREES-(pledges_degrees+redonations_degrees)),
                                Decimal(TOTAL_DEGREES * ((need.getOtherSourcesMonthlyTotal()) / need.amount)).quantize(Decimal('1')) )

    if pledges_degrees == 0 and redonations_degrees == 0 and other_sources_degrees == 0 :
        pledges_degrees = MINIMAL_DEFAULT_PLEDGES_DEGREES
        redonations_degrees = MINIMAL_DEFAULT_REDONATIONS_DEGREES
        other_sources_degrees = MINIMAL_DEFAULT_OTHER_SOURCES_DEGREES

    chart_data = {'1' : pledges_degrees,
                  '2' : redonations_degrees,
                  '3' : other_sources_degrees,
                  '4' : max(0, (TOTAL_DEGREES-(pledges_degrees+other_sources_degrees+redonations_degrees)))
                    }

    cairoplot.donut_plot(name=chart_abspathname,
                         data=chart_data,
                         width=chart_image_width, height=chart_image_height,
                         background='transparent',
                         inner_radius=CHART_INNER_RADIUS,
                         colors=chart_colors,
                         radius_list=CHART_RADIUS_LIST)

    response = HttpResponse(mimetype='image/'+CHART_IMAGE_TYPE)
    response['Content-Length'] = os.path.getsize(chart_abspathname)
    response.write(open(chart_abspathname, 'r').read())

    return response

def chart_image_goal(request, project_key, goal_key):
    project = get_object_or_404(Project, key=project_key)
    goal = get_object_or_404(ProjectGoal, project_id=project.id, key=goal_key)

    chart_size, pledges_rgbas, redonations_rgbas, other_sources_rgbas, backcircle_rgbas = _parse_request_chart_params(request)

    chart_colors = [pledges_rgbas, redonations_rgbas, other_sources_rgbas, backcircle_rgbas]

    if chart_size in CHART_PARAMS['goal']:
        chart_image_width = CHART_PARAMS['goal'][chart_size]['w']
        chart_image_height = CHART_PARAMS['goal'][chart_size]['h']
    else:
        chart_image_width = chart_image_height = int(chart_size)

    chart_relpathname = _get_chart_relative_filename(project_key, chart_size, goal_id=goal.id)
    chart_abspathname = MEDIA_ROOT+chart_relpathname

    if goal.amount > 0:
        pledges_degrees = min(TOTAL_DEGREES,
                              Decimal(TOTAL_DEGREES * ((goal.getTotalPledges()) / goal.amount)).quantize(Decimal('1')) )
        other_sources_degrees = min((TOTAL_DEGREES-pledges_degrees),
                                    Decimal(TOTAL_DEGREES * ((goal.getTotalOtherSources()) / goal.amount)).quantize(Decimal('1')) )
    else:
        pledges_degrees = 0
        other_sources_degrees = 0

    if pledges_degrees == 0 and other_sources_degrees == 0 :
        pledges_degrees = MINIMAL_DEFAULT_PLEDGES_DEGREES
        other_sources_degrees = MINIMAL_DEFAULT_OTHER_SOURCES_DEGREES

    chart_data = {'1' : pledges_degrees,
                  '2' : 0, # redonations never apply to goals
                  '3' : other_sources_degrees,
                  '4' : max(0, (TOTAL_DEGREES-(pledges_degrees+other_sources_degrees)))
                    }

    cairoplot.donut_plot(name=chart_abspathname,
                         data=chart_data,
                         width=chart_image_width, height=chart_image_height,
                         background='transparent',
                         inner_radius=CHART_INNER_RADIUS,
                         colors=chart_colors,
                         radius_list=CHART_RADIUS_LIST)

    response = HttpResponse(mimetype='image/'+CHART_IMAGE_TYPE)
    response['Content-Length'] = os.path.getsize(chart_abspathname)
    response.write(open(chart_abspathname, 'r').read())

    return response

#http://127.0.0.1:8080/debug/chart?size=65&pledges_rgb=5369B3&redonations_rgb=7696FF&other_sources_rgb=F0EEE4&backcircle_rgb=BEBDB4&pledges_deg=120&other_sources_deg=0&redonations_deg=20&background_rgb=F0EEE4
# C2AF13
# 69E750
def chart_image_debug(request):
    (chart_size,
     pledges_rgbas,
     redonations_rgbas,
     other_sources_rgbas,
     backcircle_rgbas,
     background_rgbas,
     pledges_degrees,
     other_sources_degrees,
     redonations_degrees
    ) = _parse_request_chart_params(request, True)

    chart_colors = [pledges_rgbas, redonations_rgbas, other_sources_rgbas, backcircle_rgbas]
    chart_image_width = chart_image_height = int(chart_size)

    chart_relpathname = _get_chart_relative_filename('debug', 'custom')
    chart_abspathname = MEDIA_ROOT+chart_relpathname

    if pledges_degrees == 0 and redonations_degrees == 0 and other_sources_degrees == 0 :
        pledges_degrees = MINIMAL_DEFAULT_PLEDGES_DEGREES
        redonations_degrees = MINIMAL_DEFAULT_REDONATIONS_DEGREES
        other_sources_degrees = MINIMAL_DEFAULT_OTHER_SOURCES_DEGREES

    chart_data = {'1' : pledges_degrees,
                  '2' : redonations_degrees,
                  '3' : other_sources_degrees,
                  '4' : max(0, (TOTAL_DEGREES-(pledges_degrees+redonations_degrees+other_sources_degrees))),
                   }



    cairoplot.donut_plot(name=chart_abspathname,
                         data=chart_data,
                         width=chart_image_width, height=chart_image_height,
                         background=background_rgbas,
                         inner_radius=CHART_INNER_RADIUS,
                         radius_list=CHART_RADIUS_LIST,
                         colors=chart_colors
                         )

    response = HttpResponse(mimetype='image/'+CHART_IMAGE_TYPE)
    response['Content-Length'] = os.path.getsize(chart_abspathname)
    response.write(open(chart_abspathname, 'r').read())

    return response


