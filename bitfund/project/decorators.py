from functools import wraps

from django.http import HttpResponseNotFound, HttpResponseForbidden
from django.shortcuts import get_object_or_404

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
            return view(request, project_key, *args, **kwargs)

    return _wrapped_view


def disallow_not_public_unless_maintainer(view):
    @wraps(view)
    def _wrapped_view(request, *args, **kwargs):
        project_key = kwargs.pop('project_key')
        project = get_object_or_404(Project, key=project_key)
        if not project.is_public and (project.maintainer_id != request.user.id):
            return HttpResponseNotFound()
        else:
            return view(request, project_key, *args, **kwargs)

    return _wrapped_view

def disallow_not_public(view):
    @wraps(view)
    def _wrapped_view(request, *args, **kwargs):
        project_key = kwargs.pop('project_key')
        project = get_object_or_404(Project, key=project_key)
        if not project.is_public:
            return HttpResponseNotFound()
        else:
            return view(request, project_key, *args, **kwargs)

    return _wrapped_view
