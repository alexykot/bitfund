import math

from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.db.models import Count, Sum
from django.utils.datetime_safe import datetime
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
from bitfund.project.models import *
from bitfund.project.forms import *
from bitfund.project.template_helpers import _prepare_need_item_template_data


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


    #BUDGET
    project_needs = ProjectNeed.objects.filter(project=project.id).filter(is_public=True).order_by('sort_order')
    project_needs_count = project_needs.count()
    project_goals_count = (ProjectGoal.objects.filter(project=project, is_public=True,
                                                      date_ending__gt=now(), date_starting__lt=now()).count())
    template_data['project_monthly_budget'] = (project_needs.aggregate(Sum('amount'))['amount__sum']) or 0

    #pledges
    pledges_needs_total_sum, pledges_goals_total_sum = project.getTotalMonthlyPledges()
    template_data['donations_total_sum'] = pledges_needs_total_sum
    template_data['donations_total_pledgers'] = project.getTotalMonthlyBackers()

    #other sources
    other_sources_needs_total_sum, other_sources_goals_total_sum  = project.getTotalMonthlyOtherSources()
    other_sources_total_sum = other_sources_needs_total_sum + other_sources_goals_total_sum
    template_data['other_sources_total_sum']  = other_sources_total_sum

    #redonations
    projects_i_depend_on_count, projects_depending_on_me_count = project.getLinkedProjectsCount()
    redonations_total_sum = project.getTotalMonthlyRedonations()
    template_data['redonations_total_sum'] = redonations_total_sum
    template_data['depending_on_me_projects_count'] = projects_depending_on_me_count
    template_data['i_depend_on_projects_count'] = projects_i_depend_on_count
    template_data['i_depend_on_transfer_percent'] = project.getRedonationsPercent()

    #donut chart radiants
    template_data['pledges_radiant'] = min(360, round(
        360 * (redonations_total_sum / template_data['project_monthly_budget'])))
    template_data['redonations_radiant'] = min(360, round(
        360 * (redonations_total_sum / template_data['project_monthly_budget'])))
    template_data['other_sources_radiant'] = min(360, round(
        360 * (other_sources_total_sum / template_data['project_monthly_budget'])))

    template_data['total_gained_percent'] = int(round(
        ((redonations_total_sum + other_sources_total_sum) * 100) / template_data['project_monthly_budget']))

    if not (template_data['pledges_radiant']  or template_data['redonations_radiant'] or template_data['other_sources_radiant']) :
        template_data['pledges_radiant'] = MINIMAL_DEFAULT_PLEDGES_RADIANT
        template_data['redonations_radiant'] = MINIMAL_DEFAULT_REDONATIONS_RADIANT
        template_data['other_sources_radiant'] = MINIMAL_DEFAULT_OTHER_SOURCES_RADIANT

    #NEEDS
    template_data['project_needs'] = []
    template_data['project_needs_radiants'] = []
    for need in project_needs :
        template_data['project_needs'].append(_prepare_need_item_template_data(request, project, need))


        need_pledges_n_redonations_total = need.getPledgesMonthlyTotal() + need.getRedonationsMonthlyTotal()
        need_other_sources_total = need.getOtherSourcesMonthlyTotal()

        donations_sum_radiant = min(360, round(360 * (need_pledges_n_redonations_total / need.amount)))
        other_sources_radiant = min(360, round(360 * (need_other_sources_total / need.amount)))
        if donations_sum_radiant == 0 and other_sources_radiant == 0 :
            donations_sum_radiant = MINIMAL_DEFAULT_PLEDGES_RADIANT
            other_sources_radiant = MINIMAL_DEFAULT_OTHER_SOURCES_RADIANT


        template_data['project_needs_radiants'].append({'id': need.id,
                                                        'donations_sum_radiant': donations_sum_radiant,
                                                        'other_sources_radiant': other_sources_radiant,
        })

    #GOALS
    project_goals = (ProjectGoal.objects
                     .filter(project=project)
                     .filter(is_public=True)
                     .filter(date_ending__gt=now())
                     .filter(date_starting__lt=now())
                     .order_by('sort_order')
    )
    template_data['project_goals'] = []

    #@TODO instead of sharing other sources equally between all goals and needs we would need a way to
    # set exact amounts for each need/goal
    other_sources_per_needgoal_amount = (Decimal(round(other_sources_total_sum / (project_needs_count + project_goals_count)))
                                         .quantize(Decimal('0.01')))
    for goal in project_goals:
        donations_amount = goal.getTotalPledges() + goal.getTotalRedonations()
        other_sources_amount = goal.getTotalOtherSources()
        donations_radiant = min(360, round(360 * (donations_amount / goal.amount)))
        other_sources_radiant = min(360, round(360 * (other_sources_amount / goal.amount)))
        total_percent = int(math.ceil(((donations_amount + other_sources_per_needgoal_amount) * 100) / goal.amount))

        if not (donations_radiant or other_sources_radiant) :
            donations_radiant     = MINIMAL_DEFAULT_PLEDGES_RADIANT
            other_sources_radiant = MINIMAL_DEFAULT_OTHER_SOURCES_RADIANT

        template_data['project_goals'].append({'id'                     : goal.id,
                                               'key'                    : goal.key,
                                               'title'                  : goal.title,
                                               'brief'                  : goal.brief,
                                               'video_url'              : goal.video_url,
                                               'image'                  : goal.image,
                                               'amount'                 : goal.amount,
                                               'other_sources'          : other_sources_per_needgoal_amount,
                                               'date_ending'            : goal.date_ending,
                                               'days_to_end'            : (goal.date_ending - now()).days,
                                               'donations_amount'       : donations_amount,
                                               'donations_radiant'      : donations_radiant,
                                               'other_sources_radiant'  : other_sources_radiant,
                                               'total_percent'          : total_percent,
                                               })


    template_data['project_goals_count'] = project_goals.count()

    return render_to_response('project/budget/budget.djhtm', template_data, context_instance=RequestContext(request))



def chart_image(request, project_key, need_key=None, goal_key=None):
    return render_to_response('default.djhtm', {}, context_instance=RequestContext(request))

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

