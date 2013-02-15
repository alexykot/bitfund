from selectable.base import ModelLookup
from selectable.registry import registry
from selectable.decorators import ajax_required

from bitfund.project.models import Project, Project_Dependencies

#@ajax_required
class LinkedProjectsLookup(ModelLookup):
    model = Project
    search_fields = ('titel__icontains', )
    filters = {'is_active': True, }

    def get_query(self, request, term):
        return ['foo', 'bar']

registry.register(LinkedProjectsLookup)