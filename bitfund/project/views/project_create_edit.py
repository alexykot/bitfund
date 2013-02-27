from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse 
from django.shortcuts import render_to_response, get_object_or_404 
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

from bitfund.core.settings.project import MAX_GOALS_PER_PROJECT, MAX_NEEDS_PER_PROJECT
from bitfund.project.models import *
from bitfund.project.forms import *
from bitfund.project.decorators import *

#from django.conf.locale import fa
from django.utils.translation import to_locale, get_language

@login_required
def create(request):
    if request.method == 'POST':
        project = Project()
        form    = CreateProjectForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            project.maintainer_id   = request.user.id
            form.save()
            
            return HttpResponseRedirect(reverse('bitfund.project.views.budget', args=(project.key,)))
        else :
            data = {}
            for key in request.POST : 
                data[key] = request.POST[key]
            
            data['key'] = data['key'].lower()
            
            form = CreateProjectForm(data, request.FILES)
            return render_to_response('project/create_edit.djhtm', {'form'     : form,
                                                                   'request'  : request, 
                                                                   'back_url' : reverse('bitfund.core.views.index')}, context_instance=RequestContext(request))
        
    else : 
        form    = CreateProjectForm()
        return render_to_response('project/create_edit.djhtm', {'form'     : form,
                                                               'request'  : request, 
                                                               'back_url' : reverse('bitfund.core.views.index')}, context_instance=RequestContext(request))

@login_required
@user_is_project_maintainer
def edit(request, project_key):
    project = get_object_or_404(Project, key=project_key)
    
    if request.method == 'POST':
        form    = CreateProjectForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            form.save()
            
            return HttpResponseRedirect(reverse('bitfund.project.views.budget', args=(project.key,)))
        else :
            data = {}
            for key in request.POST : 
                data[key] = request.POST[key]
            
            data['key'] = data['key'].lower()
            
            form = CreateProjectForm(data)
            return render_to_response('project/create_edit.djhtm', {'form'     : form,
                                                                   'request'  : request,
                                                                   'project'  : project,  
                                                                   'back_url' : reverse('project.views.budget', args=(project.key,))}, context_instance=RequestContext(request))
        
    else : 
        form = CreateProjectForm(instance=project)
        return render_to_response('project/create_edit.djhtm', {'form'     : form,
                                                               'request'  : request,
                                                               'project'  : project, 
                                                               'back_url' : reverse('project.views.budget', args=(project.key,))}, context_instance=RequestContext(request))


@login_required
@user_is_project_maintainer
def edit_needs(request, project_key, need_id = False):
    project         = get_object_or_404(Project, key=project_key)
    needs_list      = ProjectNeed.objects.filter(project=project.id)
    
    if request.method == 'POST':
        if (need_id != False) :
            need = ProjectNeed.objects.get(pk=need_id) 
        else :
            need = ProjectNeed()
            need.project = project
            
        form = CreateProjectNeedForm(request.POST, instance=need)
            
        if form.is_valid():
            need.amount = form.cleaned_data['amount'] 
            form.save()
            
            return HttpResponseRedirect(reverse('bitfund.project.views.edit_needs', args=(project.key,)))
        else :
            return render_to_response('project/edit_needs.djhtm', {   'request'        : request, 
                                                                      'project'        : project,
                                                                      'needs_list'     : needs_list,
                                                                      'need_form'      : form,
                                                                      'need_id'        : need_id,
                                                                      'allow_add_need' : (needs_list.count() < MAX_NEEDS_PER_PROJECT),
                                                                      'need'           : need,
                                                                      }, context_instance=RequestContext(request))
        
    else : 
        if (need_id != False) :
            need = get_object_or_404(ProjectNeed, pk=need_id) 
        else :
            need = ProjectNeed()
        
        form = CreateProjectNeedForm(instance=need)
        
        return render_to_response('project/edit_needs.djhtm', {'request'        : request,
                                                               'project'        : project,
                                                               'needs_list'     : needs_list,
                                                               'need_form'      : form,
                                                               'need_id'        : need_id,
                                                               'allow_add_need' : (needs_list.count() < MAX_NEEDS_PER_PROJECT),
                                                               'need'           : need,         
                                                               }, context_instance=RequestContext(request))

@login_required
@user_is_project_maintainer
def delete_need(request, project_key, need_id = False):
    need = get_object_or_404(ProjectNeed, pk=need_id)
    need.delete()
    
    return HttpResponseRedirect(reverse('bitfund.project.views.edit_needs', args=(project_key,)))

@login_required
@user_is_project_maintainer
def edit_goals(request, project_key, goal_id = False):
    project         = get_object_or_404(Project, key=project_key)
    goals_list      = ProjectGoal.objects.filter(project=project.id)
    
    if request.method == 'POST':
        if (goal_id != False) :
            goal = ProjectGoal.objects.get(pk=goal_id) 
        else :
            goal = ProjectGoal()
            goal.project = project 
            
        form = CreateProjectGoalForm(request.POST, instance=goal)
            
        if form.is_valid():
            goal.amount = form.cleaned_data['amount'] 
            form.save()
            
            return HttpResponseRedirect(reverse('bitfund.project.views.edit_goals', args=(project.key,)))
        else :
            form = CreateProjectGoalForm(request.POST)
            return render_to_response('project/edit_goals.djhtm', {   'request'        : request, 
                                                                      'project'        : project,
                                                                      'goals_list'     : goals_list,
                                                                      'goal_form'      : form,
                                                                      'goal_id'        : goal_id,
                                                                      'allow_add_goal' : (goals_list.count() < MAX_GOALS_PER_PROJECT),
                                                                      'goal'           : goal,
                                                                      }, context_instance=RequestContext(request))
        
    else : 
        if (goal_id != False) :
            goal = ProjectGoal.objects.get(pk=goal_id) 
        else :
            goal = ProjectGoal()
        
        form = CreateProjectGoalForm(instance=goal)
        #form = CreateProjectGoalForm()
        
        return render_to_response('project/edit_goals.djhtm', {'request'        : request,
                                                               'project'        : project,
                                                               'goals_list'     : goals_list,
                                                               'goal_form'      : form,
                                                               'goal_id'        : goal_id,
                                                               'allow_add_goal' : (goals_list.count() < MAX_GOALS_PER_PROJECT),
                                                               'goal'           : goal,
                                                               }, context_instance=RequestContext(request))


@login_required
@user_is_project_maintainer
def delete_goal(request, project_key, goal_id = False):
    goal = get_object_or_404(ProjectGoal, pk=goal_id)
    goal.delete()
    
    return HttpResponseRedirect(reverse('bitfund.project.views.edit_goals', args=(project_key,)))
