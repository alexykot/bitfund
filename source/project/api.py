import datetime
import re
import math

from django.conf.urls.defaults import *
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404 
from django.template import defaultfilters as filters
from django.utils.datetime_safe import datetime
from django.utils.timezone import utc, now, make_aware 

from tastypie import http
from tastypie.exceptions import ImmediateHttpResponse
from tastypie import fields
from tastypie.utils import trailing_slash
from tastypie.resources import ModelResource
from tastypie.bundle import Bundle

from bitfund.settings_project import TIME_TO_SHOW_HOURS
from project.models import *


class ProjectResource(ModelResource):
    class Meta:
        queryset = Project.objects.filter(is_public=True)
        fields = ['id', 
                  'key', 
                  'logo',
                  'title',
                  'brief', 
                  ]
        allowed_methods = ['get']
    
    def get_resource_uri(self, bundle_or_obj):
        kwargs = {'resource_name': self._meta.resource_name,}
        if isinstance(bundle_or_obj, Bundle):
            kwargs['pk'] = bundle_or_obj.obj.key # pk is referenced in ModelResource
        else:
            kwargs['pk'] = bundle_or_obj.key
        if self._meta.api_name is not None:
            kwargs['api_name'] = self._meta.api_name
        return self._build_reverse_url('api_dispatch_detail', kwargs = kwargs)
    

    def dehydrate(self, bundle):
        ##target month
        #monthly budget
        ##pledgers
        ##other sources
        ##dependants donations
        ##donations total 
        ##filled percent
        ##graph image URL 
        ##outstanding amount
        ##days to go string
        #bitfund profile URL 
            #(w/ user token)

        #needs list
        #need title 
        #need brief
        #need amount
        #need other sources
        
        #goals list
        #goal title 
        #goal brief
        #goal URL (w/ user token)
        #goal amount
        #goal other sources
        #goal end date
        #goal days to go string
         
        #user has donated
        #user donation type
        #user donation amount
        #user donation date
        #user token 
         
        request = bundle.request 
        
        project = get_object_or_404(Project, key=bundle.data['key'])
        
        #GENERAL BUDGET DATA
        project_budget        = {}

        target_month          = request.GET.get('month', None)
        
        if target_month is None :
            target_month = now()
        else :    
            try:
                target_month = make_aware(datetime.strptime(target_month, '%Y-%m-%d'), now().tzinfo)
            except Exception as e:
                raise ImmediateHttpResponse(response=http.HttpBadRequest(e.message))       
        
        bundle.data['target_month'] = target_month.strftime('%b %Y')
        bundle.data['project_profile_absolute_URL'] = 'http://'+request.META['HTTP_HOST']+reverse('project.views.view', kwargs={'project_key':project.key}) 
        
        project_budget_total                                    = project.getTotalMonthlyBudget(target_month)
        project_budget['budget_monthly']                        = {}
        project_budget['budget_monthly']['amount']              = project_budget_total 
        project_budget['budget_monthly']['currency']            = 'USD'
        project_budget['budget_monthly']['formatted']           = '$'+filters.floatformat(project_budget_total, 2)
        project_budget['budget_monthly']['chart_image_URL']     = 'http://'+request.META['HTTP_HOST']+reverse('project.views.chart_image', kwargs={'project_key':project.key})
        
        
        if target_month >= datetime(now().year, now().month, 1, tzinfo=now().tzinfo) :
            timedelta_to_end = (datetime(now().year, now().month+1, 1, tzinfo=now().tzinfo) - now())
            project_budget['budget_monthly']['time_to_end_seconds']     = timedelta_to_end.seconds
            if timedelta_to_end.days*24 > TIME_TO_SHOW_HOURS : 
                project_budget['budget_monthly']['time_to_end_formatted']   = str(timedelta_to_end.days)+u' days'
            else :
                project_budget['budget_monthly']['time_to_end_formatted']   = str(int(timedelta_to_end.days*24 + math.ceil(timedelta_to_end.seconds/3600)))+u' hours'
        else :
            project_budget['budget_monthly']['time_to_end_seconds']     = 0
            project_budget['budget_monthly']['time_to_end_formatted']   = 'ended'
            

        project_donations_total                                                     = project.getTotalMonthlyNeedsDonations(target_month)
        project_budget['pledgers_monthly']                                          = {}
        project_budget['pledgers_monthly']['amount']                                = project_donations_total
        project_budget['pledgers_monthly']['currency']                              = 'USD'
        project_budget['pledgers_monthly']['formatted']                             = '$'+filters.floatformat(project_donations_total, 2)
        if project_budget_total > 0 :
            project_budget['pledgers_monthly']['contributed_percent']               = round((project_donations_total*100)/project_budget_total,2)
        else :  
            project_budget['pledgers_monthly']['contributed_percent']               = -1
        
        project_other_sources_total                                                 = project.getTotalMonthlyOtherSources(target_month)
        project_budget['other_sources_monthly']                                     = {}
        project_budget['other_sources_monthly']['amount']                           = project_other_sources_total
        project_budget['other_sources_monthly']['currency']                         = 'USD'
        project_budget['other_sources_monthly']['formatted']                        = '$'+filters.floatformat(project_other_sources_total, 2)
        if project_budget_total > 0 :
            project_budget['other_sources_monthly']['contributed_percent']          = round((project_other_sources_total*100)/project_budget_total,2) 
        else :
            project_budget['other_sources_monthly']['contributed_percent']          = -1
        
        project_dependants_donations_total                                          = project.getTotalMonthlyDependantsDonations(target_month)
        project_budget['dependants_donations_monthly']                              = {}
        project_budget['dependants_donations_monthly']['amount']                    = project_dependants_donations_total
        project_budget['dependants_donations_monthly']['currency']                  = 'USD'
        project_budget['dependants_donations_monthly']['formatted']                 = '$'+filters.floatformat(project_dependants_donations_total, 2)
        if project_budget_total > 0 :
            project_budget['dependants_donations_monthly']['contributed_percent']   = round((project_dependants_donations_total*100)/project_budget_total, 2) 
        else : 
            project_budget['dependants_donations_monthly']['contributed_percent']   = -1
        
        project_donations_monthly_total                                             = project_donations_total+project_other_sources_total+project_dependants_donations_total
        project_budget['total_donations_monthly']                                   = {}
        project_budget['total_donations_monthly']['amount']                         = project_donations_monthly_total 
        project_budget['total_donations_monthly']['currency']                       = 'USD'
        project_budget['total_donations_monthly']['formatted']                      = '$'+filters.floatformat(project_donations_monthly_total, 2)
        if project_budget_total > 0 :
            project_budget['total_donations_monthly']['contributed_percent']        = round((project_donations_monthly_total*100)/project_budget_total, 2) 
        else : 
            project_budget['total_donations_monthly']['contributed_percent']        = -1
        
        project_budget_outstanding                                                  = max((project_budget_total-project_donations_total),0) 
        project_budget['budget_outstanding']                                        = {}
        project_budget['budget_outstanding']['amount']                              = project_budget_outstanding
        project_budget['budget_outstanding']['currency']                            = 'USD'
        project_budget['budget_outstanding']['formatted']                           = '$'+filters.floatformat(project_budget_outstanding, 2)
        

        
        bundle.data['project_budget'] = project_budget
        
        
        #USER SPECIFIC DATA, IF VALID TOKEN SUPPLIED
        user_token   = request.GET.get('userToken', None)
        
        return bundle
    
    
    def override_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<key>[\w\d_.-]+)/$" % self._meta.resource_name, self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
        ]
    
    """
    #custom data added to standard item entry in list or details
    def dehydrate(self, bundle):
        bundle.data['custom_field'] = "project ID is: "+str(bundle.data['id'])
        return bundle
    """

    """    
    #completely custom actions 
    def override_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/details%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('get_details'), name="api_get_details"),
        ]

    def get_details(self, request, **kwargs):
        print request.GET.get('project', '')
        projects = Project.objects.filter(is_public=True)
        objects = []
        for result in projects:
            bundle = self.build_bundle(obj=result, request=request)
            bundle = self.full_dehydrate(bundle)
            objects.append(bundle)
        
        return self.create_response(request, objects)
    """
    
class ProjectNeedResource(ModelResource):
    project =  fields.ForeignKey(ProjectResource, 'project')
     
    class Meta:
        queryset = ProjectNeed.objects.filter(is_public=True)
        fields = ['id', 
                  'key', 
                  'project',
                  'title',
                  'amount', 
                  'brief', 
                  'sort_order',
                  ]
        allowed_methods = ['get']


class ProjectGoalResource(ModelResource):
    project =  fields.ForeignKey(ProjectResource, 'project')
     
    class Meta:
        queryset = ProjectGoal.objects.filter(is_public=True)
        fields = ['id', 
                  'key', 
                  'project',
                  'title',
                  'amount', 
                  'brief', 
                  'sort_order',
                  ]
        allowed_methods = ['get']





