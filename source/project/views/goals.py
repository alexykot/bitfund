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

from project.models import *
from project.forms import *
from pledger.models import *


def goals(request, project_key):
    project = get_object_or_404(Project, key=project_key)

    template_data = {'project' : project, 'request' : request, 'today'   : datetime.utcnow().replace(tzinfo=utc).today(),}

    #PROJECT HEADER
    template_data['project_outlinks']       = ProjectOutlink.objects.filter(project=project).filter(is_public=True).order_by('sort_order')
    template_data['project_categories']     = project.categories.all()
    template_data['project_latest_release'] = ProjectRelease.objects.filter(project=project).filter(is_public=True).order_by('-date_released')[:1]
    if (template_data['project_latest_release'].count() > 0) :
        template_data['project_latest_release'] = template_data['project_latest_release'][0]
    else :
        template_data['project_latest_release'] = False


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


def goal_view(request, project_key, goal_key):
    project = get_object_or_404(Project, key=project_key)
    goal    = get_object_or_404(ProjectGoal, project=project, key=goal_key)

    template_data = {'project' : project,'request' : request,'today'   : datetime.utcnow().replace(tzinfo=utc).today(),}
    
    
    if not goal.is_public :
        if project.userEditAccess(request.user) :
            template_data['view_status'] = 'draft'
        else :    
            return HttpResponseForbidden()
    elif goal.date_ending < now() : 
        template_data['view_status'] = 'expired'
            
    other_sources_total_sum             = project.getTotalMonthlyOtherSources()
    project_needs_count                 = project.getNeedsCount()
    project_goals_count                 = project.getGoalsCount()
    other_sources_per_needgoal_amount   = int(round(other_sources_total_sum/(project_goals_count+project_needs_count)))
    donations_amount                    = DonationHistoryGoals.objects.filter(goal=goal).aggregate(Sum('amount'))['amount__sum']
    
    goal.donations_amount               = donations_amount  
     
    goal.donations_radiant              = min(360, round(360*(donations_amount / goal.amount)))
    goal.other_sources_radiant          = min(360, round(360*(other_sources_per_needgoal_amount / goal.amount)))
    goal.total_percent                  = int(math.ceil(((donations_amount+other_sources_per_needgoal_amount)*100) / goal.amount))
    datetime_to_end                     = (goal.date_ending - now())
    goal.days_to_end                    = int(datetime_to_end.days)
    goal.hours_to_end                   = int(datetime_to_end.days*24 + math.ceil(datetime_to_end.seconds/3600))
        
    goal.backers_count                  = DonationHistoryGoals.objects.filter(goal=goal).aggregate(Count('donation_history', distinct=True))['donation_history__count']
    
    if not (goal.donations_radiant or goal.other_sources_radiant) :
        goal.donations_radiant            = 2
        goal.other_sources_radiant        = 1

    template_data['goal']               = goal
    
    return render_to_response('project/view_goal.djhtm', template_data, context_instance=RequestContext(request))























