import datetime
import math

from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse 
from django.shortcuts import render_to_response, get_object_or_404 
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.utils.timezone import utc, now 

from bitfund.settings_project import MAX_EXPENSES_ON_PROJECT_PAGE, MAX_USERS_ON_PROJECT_PAGE, MAX_GOALS_ON_PROJECT_PAGE
from bitfund.settings import TIME_ZONE
from project.models import *
from project.forms import *
from project.decorators import *
from pledger.models import *


def about(request, project_key):
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

    return render_to_response('project/about.djhtm', template_data, context_instance=RequestContext(request))

def contribute(request, project_key):
    project = get_object_or_404(Project, key=project_key)
    template_data = {'project' : project,'request' : request,'today'   : datetime.utcnow().replace(tzinfo=utc).today(),}

    #PROJECT HEADER
    template_data['project_outlinks']       = ProjectOutlink.objects.filter(project=project).filter(is_public=True).order_by('sort_order')
    template_data['project_categories']     = project.categories.all()
    template_data['project_latest_release'] = ProjectRelease.objects.filter(project=project).filter(is_public=True).order_by('-date_released')[:1]
    if (template_data['project_latest_release'].count() > 0) :
        template_data['project_latest_release'] = template_data['project_latest_release'][0]
    else :
        template_data['project_latest_release'] = False
    
    return render_to_response('project/contribute.djhtm', template_data, context_instance=RequestContext(request))



def linked_projects(request, project_key):
    project = get_object_or_404(Project, key=project_key)

    template_data = {'project' : project,
                     'request' : request,
                     'today'   : datetime.utcnow().replace(tzinfo=utc).today(),
                     }

    return render_to_response('project/default.djhtm', template_data, context_instance=RequestContext(request))

def linked_project_view(request, project_key, need_goal_key):
    project = get_object_or_404(Project, key=project_key)
    template_data = {'project' : project,'request' : request,'today'   : datetime.utcnow().replace(tzinfo=utc).today(),}
    return render_to_response('project/default.djhtm', template_data, context_instance=RequestContext(request))


def team(request, project_key, need_goal_key):
    project = get_object_or_404(Project, key=project_key)
    template_data = {'project' : project,'request' : request,'today'   : datetime.utcnow().replace(tzinfo=utc).today(),}
    return render_to_response('project/default.djhtm', template_data, context_instance=RequestContext(request))

def timeline(request, project_key, need_goal_key):
    project = get_object_or_404(Project, key=project_key)
    template_data = {'project' : project,'request' : request,'today'   : datetime.utcnow().replace(tzinfo=utc).today(),}
    return render_to_response('project/default.djhtm', template_data, context_instance=RequestContext(request))

def blog(request, project_key, need_goal_key):
    project = get_object_or_404(Project, key=project_key)
    template_data = {'project' : project,'request' : request,'today'   : datetime.utcnow().replace(tzinfo=utc).today(),}
    return render_to_response('project/default.djhtm', template_data, context_instance=RequestContext(request))

