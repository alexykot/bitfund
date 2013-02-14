from functools import wraps

from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.core.urlresolvers import reverse 
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.decorators import available_attrs

from bitfund.project.forms import *

"""
def user_is_project_maintainer(request):
    def decorator(view_func, *args, **kwargs):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, project_key, *args, **kwargs):
            project = get_object_or_404(Project, key=project_key)

            if (project.maintainer_id != request.user.id) :
                return HttpResponseRedirect(reverse('bitfund.core.views.index', args=(project.key,)))
            else :
                view_func(request, *args, **kwargs)
            
        return _wrapped_view
    return decorator
"""
def user_is_project_maintainer(view):
    @wraps(view)
    def _wrapped_view(request, project_key, *args, **kwargs):
        project = get_object_or_404(Project, key=project_key)
        if (project.maintainer_id != request.user.id) :
            return HttpResponseForbidden()
        else :
            return view(request, project_key, *args, **kwargs)
    return _wrapped_view

def user_is_not_project_maintainer(view):
    @wraps(view)
    def _wrapped_view(request, project_key, *args, **kwargs):
        project = get_object_or_404(Project, key=project_key)
        if (project.maintainer_id == request.user.id) :
            return HttpResponseForbidden()
        else :
            return view(request, project_key, *args, **kwargs)
    return _wrapped_view

