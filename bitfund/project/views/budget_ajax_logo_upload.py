import json
import os
import shutil

from django.shortcuts import get_object_or_404
from django.views.generic import View
from django.utils import simplejson as json
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse

from ajaxuploader.views import AjaxFileUploader
from bitfund.core.settings_split.server import MEDIA_ROOT, MEDIA_URL

from bitfund.project.models import Project
from bitfund.project.template_helpers import _get_logo_relative_filename


class BudgetAjaxLogoUploader(AjaxFileUploader, View):

    def _ajax_upload(self, request, *args, **kwargs):
        response = super(BudgetAjaxLogoUploader, self)._ajax_upload(request, *args, **kwargs)

        response_json = json.JSONDecoder().decode(response.content)
        if 'success' in response_json and response_json['success'] :
            project_key = kwargs.pop('project_key')
            project = get_object_or_404(Project, key=project_key)

            tmp_logo_relpath = response_json['path'].replace(MEDIA_URL, '')
            tmp_logo_abspath = os.path.join(MEDIA_ROOT, tmp_logo_relpath)

            if project.logo:
                old_logo_relpath = project.logo
                old_logo_abspath = os.path.join(MEDIA_ROOT, old_logo_relpath)
                if os.path.exists(old_logo_abspath) :
                    os.remove(old_logo_abspath)

            logo_relpath = _get_logo_relative_filename(project_key, os.path.basename(tmp_logo_abspath))
            logo_abspath = os.path.join(MEDIA_ROOT, logo_relpath)
            shutil.move(tmp_logo_abspath, logo_abspath)

            project.logo = logo_relpath
            project.save()

            response_json['path'] = logo_relpath

        return HttpResponse(json.dumps(response_json, cls=DjangoJSONEncoder), content_type='application/json; charset=utf-8')

budget_ajax_logo_upload = BudgetAjaxLogoUploader()
