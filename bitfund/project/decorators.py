from functools import wraps

from django.http import HttpResponseNotFound, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from bitfund.core.http_responses import HttpResponseNotImplemented

from bitfund.project.forms import *


def user_is_project_maintainer(view):
    @wraps(view)
    def _wrapped_view(request, *args, **kwargs):
        project_key = kwargs.pop('project_key')
        project = get_object_or_404(Project, key=project_key)
        if (project.maintainer_id != request.user.id):
            return HttpResponseForbidden()
        else:
            return view(request, project_key, *args, **kwargs)

    return _wrapped_view


def user_is_not_project_maintainer(view):
    @wraps(view)
    def _wrapped_view(request, project_key, *args, **kwargs):
        project = get_object_or_404(Project, key=project_key)
        if (project.maintainer_id == request.user.id):
            return HttpResponseForbidden()
        else:
            return view(request, project_key=project_key, *args, **kwargs)

    return _wrapped_view


def disallow_not_public_unless_maintainer(view):
    @wraps(view)
    def _wrapped_view(request, *args, **kwargs):
        project_key = kwargs.pop('project_key')
        project = get_object_or_404(Project, key=project_key)
        if not project.is_public and (project.maintainer_id != request.user.id):
            return HttpResponseNotFound()

        if 'goal_key' in kwargs :
            goal_key = kwargs.pop('goal_key')
            goal = get_object_or_404(ProjectGoal, key=goal_key)
            if not goal.is_public and (project.maintainer_id != request.user.id):
                return HttpResponseNotFound()
            else :
                return view(request, project_key=project_key, goal_key=goal_key, *args, **kwargs)

        return view(request, project_key=project_key, *args, **kwargs)

    return _wrapped_view

def disallow_not_public(view):
    @wraps(view)
    def _wrapped_view(request, *args, **kwargs):
        project_key = kwargs.pop('project_key')
        project = get_object_or_404(Project, key=project_key)
        if not project.is_public:
            return HttpResponseNotFound()
        else:
            return view(request, project_key=project_key, *args, **kwargs)

    return _wrapped_view

def redirect_not_active(view):
    @wraps(view)
    def _wrapped_view(request, *args, **kwargs):
        project_key = kwargs.pop('project_key')
        project = get_object_or_404(Project, key=project_key)
        if project.status == PROJECT_STATUS_CHOICES.unclaimed:
            return redirect('bitfund.project.views.unclaimed', project_key=project_key)
        elif project.status != PROJECT_STATUS_CHOICES.active:
            return HttpResponseNotImplemented()
        else:
            return view(request, project_key=project_key, *args, **kwargs)

    return _wrapped_view

def redirect_active(view):
    @wraps(view)
    def _wrapped_view(request, *args, **kwargs):
        project_key = kwargs.pop('project_key')
        project = get_object_or_404(Project, key=project_key)
        if project.status == PROJECT_STATUS_CHOICES.active:
            return redirect('bitfund.project.views.budget', project_key=project_key)
        else:
            return view(request, project_key=project_key, *args, **kwargs)

    return _wrapped_view


def user_not_voted_maintainer_yet(view):
    @wraps(view)
    def _wrapped_view(request, *args, **kwargs):
        project_key = kwargs.pop('project_key')
        project = get_object_or_404(Project, key=project_key)
        project_maintainer_votes_count = (ProjectMaintainerVote.objects
                                          .filter(project_id=project.id)
                                          .filter(maintainer_id=project.maintainer_id)
                                          .filter(user_id=request.user.id)
                                          .count()
                                            )
        if project_maintainer_votes_count != 0:
            return redirect('bitfund.project.views.budget', project_key=project_key)
        else:
            return view(request, project_key=project_key, *args, **kwargs)

    return _wrapped_view


def user_not_reported_project_yet(view):
    @wraps(view)
    def _wrapped_view(request, *args, **kwargs):
        project_key = kwargs.pop('project_key')
        project = get_object_or_404(Project, key=project_key)
        project_reports_count = (ProjectReport.objects
                                          .filter(project_id=project.id)
                                          .filter(reporter_id=request.user.id)
                                          .count()
        )
        if project_reports_count != 0:
            return redirect('bitfund.project.views.budget', project_key=project_key)
        else:
            return view(request, project_key=project_key, *args, **kwargs)

    return _wrapped_view
