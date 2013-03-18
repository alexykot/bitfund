import os
import cairoplot

from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from bitfund.core.settings.project import ARGB_DONUT_CHART_PLEDGES, ARGB_DONUT_CHART_REDONATIONS, ARGB_DONUT_CHART_OTHER_SOURCES, ARGB_DONUT_CHART_BACKGROUND, TOTAL_DEGREES, CHART_RADIUS_LIST, CHART_IMAGE_TYPE, CHART_MEDIUM_H, CHART_MEDIUM_W
from bitfund.core.settings.server import STATICFILES_DIRS, STATIC_ROOT
from bitfund.project.decorators import disallow_not_public_unless_maintainer
from bitfund.project.models import Project
from bitfund.project.template_helpers import _prepare_project_budget_template_data, _get_chart_relative_filename


@disallow_not_public_unless_maintainer
def chart_image_project(request, project_key, size):
    project = get_object_or_404(Project, key=project_key)

    chart_relpathname = _get_chart_relative_filename(project_key, size)
    chart_abspathname = STATIC_ROOT+chart_relpathname


    budget_data = _prepare_project_budget_template_data(request, project)

    budget_data['pledges_radiant'] = 120
    budget_data['redonations_radiant'] = 40
    budget_data['other_sources_radiant'] = 20


    chart_data = {'1' : budget_data['pledges_radiant'],
                    '2' : budget_data['redonations_radiant'],
                    '3' : budget_data['other_sources_radiant'],
                    '4' : TOTAL_DEGREES-(budget_data['pledges_radiant']+budget_data['redonations_radiant']+budget_data['other_sources_radiant'])}


    shadow_parts = (True, True, False, False)
    chart_colors = [ARGB_DONUT_CHART_PLEDGES, ARGB_DONUT_CHART_REDONATIONS, ARGB_DONUT_CHART_OTHER_SOURCES, ARGB_DONUT_CHART_BACKGROUND]

    cairoplot.donut_plot(chart_abspathname, chart_data, CHART_MEDIUM_W, CHART_MEDIUM_H,
                         background='transparent',
                         gradient=False,
                         shadow=False,
                         shadow_parts=shadow_parts,
                         inner_radius=1,
                         colors=chart_colors,
                         radius_list=CHART_RADIUS_LIST)

    response = HttpResponse(mimetype='image/'+CHART_IMAGE_TYPE)
    response['Content-Length'] = os.path.getsize(chart_abspathname)
    response.write(open(chart_abspathname, 'r').read())

    return response

def chart_image_need(request, project_key, need_id, size):
    chart_filename = 'donut.png'
    chart_abspathname = STATICFILES_DIRS[0]+"img/charts/"+chart_filename

    response = HttpResponse(mimetype='image/png')
    response['Content-Length'] = os.path.getsize(chart_abspathname)
    response.write(open(chart_abspathname, 'r').read())

    return response

def chart_image_goal(request, project_key, goal_id, size):
    chart_filename = 'donut.png'
    chart_abspathname = STATICFILES_DIRS[0]+"img/charts/"+chart_filename

    response = HttpResponse(mimetype='image/png')
    response['Content-Length'] = os.path.getsize(chart_abspathname)
    response.write(open(chart_abspathname, 'r').read())

    return response
