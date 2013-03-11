import datetime
import math

from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.core.urlresolvers import reverse 
from django.shortcuts import render_to_response, get_object_or_404 
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.utils.datetime_safe import datetime
from django.utils.timezone import utc, now
from bitfund.core.settings.project import SITE_CURRENCY_SIGN
from bitfund.project.decorators import redirect_not_active, disallow_not_public_unless_maintainer

from bitfund.project.models import *
from bitfund.project.forms import *
from bitfund.pledger.models import *
from bitfund.project.template_helpers import _prepare_goal_item_template_data


def goals(request, project_key):
    project = get_object_or_404(Project, key=project_key)

    template_data = {'project' : project,
                     'request' : request,
                     'site_currency_sign': SITE_CURRENCY_SIGN,
                     'today'   : datetime.utcnow().replace(tzinfo=utc).today(),
                     }


    donationhistory_total_sum           = project.getTotalMonthlyNeedsDonations() + project.getTotalMonthlyGoalsDonations()



    #OTHER SOURCES
    other_sources_total_sum             = project.getTotalMonthlyOtherSources()
    project_needs_count                 = project.getNeedsCount()
    project_goals_count                 = project.getGoalsCount()
    other_sources_per_needgoal_amount   = int(round(other_sources_total_sum/(project_goals_count+project_needs_count)))


    #GOALS DETAILS LIST
    project_goals                       = (ProjectGoal.objects
                                                      .filter(project=project)
                                                      .filter(is_public=True)
                                                      .filter(date_ending__gt=now())
                                                      .filter(date_starting__lt=now())
                                                      .order_by('sort_order')
                                           )
    template_data['project_goals']      = []
                   
    for goal in project_goals:
        donations_amount             = DonationHistoryGoals.objects.filter(goal=goal).aggregate(Sum('amount'))['amount__sum']
        donations_radiant            = min(360, round(360*(donations_amount / goal.amount)))
        other_sources_radiant        = min(360, round(360*(other_sources_per_needgoal_amount / goal.amount)))
        total_percent                = int(math.ceil(((donations_amount+other_sources_per_needgoal_amount)*100) / goal.amount))
        
        if not (donations_radiant or other_sources_radiant) :
            donations_radiant     = 2
            other_sources_radiant = 1

        template_data['project_goals'].append({'id'                     : goal.id,
                                               'key'                    : goal.key,
                                               'title'                  : goal.title,
                                               'brief'                  : goal.brief,
                                               'video_url'              : goal.video_url,
                                               'image'                  : goal.image,
                                               'amount'                 : goal.amount,
                                               'other_sources'          : other_sources_per_needgoal_amount,
                                               'short_text'             : goal.short_text,
                                               'long_text'              : goal.long_text,
                                               'date_ending'            : goal.date_ending,
                                               'days_to_end'            : (goal.date_ending - now()).days,
                                               'hours_to_end'           : int((goal.date_ending - now()).days*24 + math.ceil((goal.date_ending - now()).seconds/3600)),
                                               'donations_amount'       : donations_amount,
                                               'donations_radiant'      : donations_radiant,
                                               'other_sources_radiant'  : other_sources_radiant,
                                               'total_percent'          : total_percent,
                                                })
        


    
    
    
    return render_to_response('project/goals.djhtm', template_data, context_instance=RequestContext(request))


@redirect_not_active
@disallow_not_public_unless_maintainer
def goal_view(request, project_key, goal_key):
    project = get_object_or_404(Project, key=project_key)
    goal    = get_object_or_404(ProjectGoal, project=project, key=goal_key)

    template_data = {'project' : project,
                     'request' : request,
                     'today'   : datetime.utcnow().replace(tzinfo=utc).today(),
                     }

    if project.maintainer_id == request.user.id :
        template_data['project_edit_access'] = True
    else :
        template_data['project_edit_access'] = False

    if not goal.is_public :
        if project.userEditAccess(request.user) :
            template_data['view_status'] = 'draft'
        else :
            return HttpResponseForbidden()
    elif goal.date_ending < now() :
        template_data['view_status'] = 'expir2ed'

    template_data['goal'] = _prepare_goal_item_template_data(request, project, goal)

    return render_to_response('project/goal.djhtm', template_data, context_instance=RequestContext(request))























