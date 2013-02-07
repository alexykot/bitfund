import time
import datetime
import re
import math

from django.conf.urls.defaults import *
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404 
from django.template import defaultfilters as filters
from django.utils.datetime_safe import datetime
from django.utils.timezone import utc, now, make_aware
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

from tastypie import http
from tastypie.exceptions import ImmediateHttpResponse
from tastypie import fields
from tastypie.utils import trailing_slash
from tastypie.resources import ModelResource, ALL_WITH_RELATIONS
from tastypie.bundle import Bundle

from bitfund.settings_project import TIME_TO_SHOW_HOURS, API_USER_TOKEN_PARAM_NAME, API_TARGET_MONTH_PARAM_NAME, SITE_CURRENCY
from project.models import *
from pledger.models import *


def checkUserToken(user_token):
    import os
    import base64
    user = None
    if user_token is None or Profile.objects.filter(donation_is_public=True).filter(api_token=user_token).count() != 1 :
        user_token = base64.urlsafe_b64encode(os.urandom(32))
    else :
        user = Profile.objects.get(api_token=user_token).user
        
    return user_token, user
    
def checkTargetMonth(target_month):    
    if target_month is None :
        target_month = now()
    else :    
        try:
            target_month = make_aware(datetime.strptime(target_month, '%Y-%m-%d'), now().tzinfo)
        except Exception as e:
            raise ImmediateHttpResponse(response=http.HttpBadRequest(e.message))       
    return target_month

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
        filtering = {'key': ALL_WITH_RELATIONS, }

    def get_resource_uri(self, bundle_or_obj):
        kwargs = {'resource_name': self._meta.resource_name,}
        if isinstance(bundle_or_obj, Bundle):
            kwargs['key'] = bundle_or_obj.obj.key # pk is referenced in ModelResource
        else:
            kwargs['key'] = bundle_or_obj.key
        if self._meta.api_name is not None:
            kwargs['api_name'] = self._meta.api_name

        return self._build_reverse_url('api_dispatch_detail', kwargs = kwargs)

    def override_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<key>[\w\d_.-]+)/$" % self._meta.resource_name, self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
            #url(r"^(?P<resource_name>%s)/(?P<key>\w[\w/-]*)/need$" % self._meta.resource_name, self.wrap_view('get_needs'), name="api_get_needs"),
            #url(r"^(?P<resource_name>%s)/(?P<key>\w[\w/-]*)/need/(?P<need_key>\w[\w/-]*)$" % self._meta.resource_name, self.wrap_view('get_need'), name="api_get_need"),
            #url(r"^(?P<resource_name>%s)/(?P<key>\w[\w/-]*)/goals/(?P<key>\w[\w/-]*)%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('get_goals'), name="api_get_goals"),

            #url(r"^(?P<resource_name>%s)/(?P<key>[\w\d_.-]+)/$" % self._meta.resource_name, self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
            #url(r"^(?P<resource_name>%s)/(?P<custom_id>[-_\w\d]+)%s$" % (self._meta.resource_name,trailing_slash()),self.wrap_view('dispatch_detail'),name="api_dispatch_detail"),
        ]

    def get_needs(self, request, **kwargs):
        obj = self.cached_obj_get(request=request, **self.remove_api_resource_names(kwargs))
        
        return ProjectNeedResource().get_list(request, project=obj.pk)

    def get_need(self, request, need_key, **kwargs):
        return ProjectNeedResource().get_detail(request, key=need_key)

    """    
    def get_goals(self, request, **kwargs):
        try:
            obj = self.cached_obj_get(request=request, **self.remove_api_resource_names(kwargs))
        except ObjectDoesNotExist:
            return http.HttpGone()
        except MultipleObjectsReturned:
            return http.HttpMultipleChoices("More than one resource is found at this URI.")

        child_resource = ProjectGoalResource()
        return child_resource.get_detail(request, project=obj.pk)
    """    
    
    def dehydrate(self, bundle):
        #supplied data: 
        ##target month, monthly budget, pledgers,other sources,dependants donations,donations total,filled percent,graph image URL, outstanding amount,days to go string,bitfund profile URL (w/ user token),
        ##user has donated,user donation type,user donation amount,user donation date,user token ,
        ##needs list link, goals list link
         

         
        request = bundle.request 
        
        project = get_object_or_404(Project, key=bundle.data['key'])
        
        #GENERAL BUDGET DATA
        project_budget        = {}

        target_month     = checkTargetMonth(request.GET.get(API_TARGET_MONTH_PARAM_NAME, None))
        user_token, user = checkUserToken(request.GET.get(API_USER_TOKEN_PARAM_NAME, None))
        
        bundle.data['target_month']        = target_month.strftime('%b %Y')
        bundle.data['project_profile_URL'] = 'http://'+request.META['HTTP_HOST']+reverse('project.views.view', kwargs={'project_key':project.key})+'?'+API_USER_TOKEN_PARAM_NAME+'='+user_token 
        
        project_budget_total                                    = project.getTotalMonthlyBudget(target_month)
        project_budget['budget_monthly']                        = {}
        project_budget['budget_monthly']['amount']              = project_budget_total 
        project_budget['budget_monthly']['currency']            = 'USD'
        project_budget['budget_monthly']['formatted']           = '$'+filters.floatformat(project_budget_total, 2)
        project_budget['budget_monthly']['chart_image_URL']     = 'http://'+request.META['HTTP_HOST']+reverse('project.views.chart_image', kwargs={'project_key':project.key})
        
        
        project_budget['end_utctimestamp']        = time.mktime(datetime(target_month.year, target_month.month+1, 1, tzinfo=target_month.tzinfo).utctimetuple())-1 #-1 because it's the last second of previous month, not first second of the next one
        if target_month >= datetime(now().year, now().month, 1, tzinfo=now().tzinfo) :
            timedelta_to_end = (datetime(now().year, now().month+1, 1, tzinfo=now().tzinfo) - now())
            project_budget['budget_monthly']['time_to_end_seconds']     = timedelta_to_end.seconds+timedelta_to_end.days*86400
            if timedelta_to_end.days*24 > TIME_TO_SHOW_HOURS : 
                project_budget['budget_monthly']['time_to_end_formatted']   = str(timedelta_to_end.days)+u' days'
            else :
                project_budget['budget_monthly']['time_to_end_formatted']   = str(int(timedelta_to_end.days*24 + math.ceil(timedelta_to_end.seconds/3600)))+u' hours'
        else :
            project_budget['budget_monthly']['time_to_end_seconds']     = 0
            project_budget['budget_monthly']['time_to_end_formatted']   = 'ended'
            

        project_donations_total                                                     = project.getTotalMonthlyNeedsPledges(target_month)
        project_budget['pledgers_monthly']                                          = {}
        project_budget['pledgers_monthly']['amount']                                = project_donations_total
        project_budget['pledgers_monthly']['currency']                              = SITE_CURRENCY
        project_budget['pledgers_monthly']['formatted']                             = '$'+filters.floatformat(project_donations_total, 2)
        if project_budget_total > 0 :
            project_budget['pledgers_monthly']['contributed_percent']               = round((project_donations_total*100)/project_budget_total,2)
        else :  
            project_budget['pledgers_monthly']['contributed_percent']               = -1
        
        project_other_sources_total                                                 = project.getTotalMonthlyOtherSources(target_month)
        project_budget['other_sources_monthly']                                     = {}
        project_budget['other_sources_monthly']['amount']                           = project_other_sources_total
        project_budget['other_sources_monthly']['currency']                         = SITE_CURRENCY
        project_budget['other_sources_monthly']['formatted']                        = '$'+filters.floatformat(project_other_sources_total, 2)
        if project_budget_total > 0 :
            project_budget['other_sources_monthly']['contributed_percent']          = round((project_other_sources_total*100)/project_budget_total,2) 
        else :
            project_budget['other_sources_monthly']['contributed_percent']          = -1
        
        project_dependants_donations_total                                          = project.getTotalMonthlyDependantsDonations(target_month)
        project_budget['dependants_donations_monthly']                              = {}
        project_budget['dependants_donations_monthly']['amount']                    = project_dependants_donations_total
        project_budget['dependants_donations_monthly']['currency']                  = SITE_CURRENCY
        project_budget['dependants_donations_monthly']['formatted']                 = '$'+filters.floatformat(project_dependants_donations_total, 2)
        if project_budget_total > 0 :
            project_budget['dependants_donations_monthly']['contributed_percent']   = round((project_dependants_donations_total*100)/project_budget_total, 2) 
        else : 
            project_budget['dependants_donations_monthly']['contributed_percent']   = -1
        
        project_donations_monthly_total                                             = project_donations_total+project_other_sources_total+project_dependants_donations_total
        project_budget['total_donations_monthly']                                   = {}
        project_budget['total_donations_monthly']['amount']                         = project_donations_monthly_total 
        project_budget['total_donations_monthly']['currency']                       = SITE_CURRENCY
        project_budget['total_donations_monthly']['formatted']                      = '$'+filters.floatformat(project_donations_monthly_total, 2)
        if project_budget_total > 0 :
            project_budget['total_donations_monthly']['contributed_percent']        = round((project_donations_monthly_total*100)/project_budget_total, 2) 
        else : 
            project_budget['total_donations_monthly']['contributed_percent']        = -1
        
        project_budget_outstanding                                                  = max((project_budget_total-project_donations_total),0) 
        project_budget['budget_outstanding']                                        = {}
        project_budget['budget_outstanding']['amount']                              = project_budget_outstanding
        project_budget['budget_outstanding']['currency']                            = SITE_CURRENCY
        project_budget['budget_outstanding']['formatted']                           = '$'+filters.floatformat(project_budget_outstanding, 2)
        
        
        
        #PROJECT NEEDS LIST URI
        project_needs = '/api/'+ProjectNeedResource()._meta.resource_name+'/?project__key='+project.key  

        #PROJECT GOALS LIST URI
        project_goals = '/api/'+ProjectGoalResource()._meta.resource_name+'/?project__key='+project.key
        
        
        #USER SPECIFIC DATA, IF VALID TOKEN SUPPLIED
        project_user_data = {}
        project_user_data['user_token'] = user_token
        
        if user is not None : 
            user_profile = Profile.objects.get(user=user)
            project_user_data['user_known']            = True
            project_user_data['total_donations_sum']   = user_profile.getTotalProjectDonations(project)
            project_user_data['total_donations_count'] = DonationHistory.objects.filter(user=user).filter(project=project).count()
            if project_user_data['total_donations_count'] > 0 :
                latest_donation        = (DonationHistory.objects.filter(user=user).filter(project=project).order_by('-datetime_sent')[:1])[0]
                latest_donation_amount = latest_donation.getAmount()
                project_user_data['latest_donation']                      = {}
                project_user_data['latest_donation']['date_utctimestamp'] = time.mktime(latest_donation.datetime_sent.utctimetuple()) 
                project_user_data['latest_donation']['date_formatted']    = latest_donation.datetime_sent.strftime('%d %b %Y')
                project_user_data['latest_donation']['amount']            = latest_donation_amount
                project_user_data['latest_donation']['currency']          = SITE_CURRENCY
                project_user_data['latest_donation']['formatted']         = '$'+filters.floatformat(latest_donation_amount, 2)
            else :
                project_user_data['last_donation']     = False 
        else :
            project_user_data['user_known']            = False
        
        
        bundle.data['project_budget']    = project_budget
        bundle.data['project_needs']     = project_needs
        bundle.data['project_goals']     = project_goals
        bundle.data['project_user_data'] = project_user_data
        
        return bundle
    
    
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
        queryset = ProjectNeed.objects.filter(is_public=True).order_by('sort_order')
        fields = ['id', 
                  'key', 
                  'project',
                  'title',
                  'amount', 
                  'brief', 
                  'sort_order',
                  ]
        allowed_methods = ['get']
        filtering = {'project': ALL_WITH_RELATIONS, }
    
    def get_resource_uri(self, bundle_or_obj):
        kwargs = {'resource_name': self._meta.resource_name,}
        if isinstance(bundle_or_obj, Bundle):
            kwargs['key']      = bundle_or_obj.obj.key
        else:
            kwargs['key']      = bundle_or_obj.key
        if self._meta.api_name is not None:
            kwargs['api_name'] = self._meta.api_name#

        return self._build_reverse_url('api_dispatch_detail', kwargs = kwargs)

    def override_urls(self):
        return [url(r"^(?P<resource_name>%s)/(?P<key>[\w\d_.-]+)/$" % self._meta.resource_name, self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),]
    

    def dehydrate(self, bundle_or_obj):
        ##values included: need title, need brief,need amount,donations,other sources,dependants donations,donations total,filled percent,graph image URL,outstanding amount,days to go string,pledgers num
        
        if isinstance(bundle_or_obj, Bundle):
            need = bundle_or_obj.obj
        else :
            need = bundle_or_obj

        request = bundle_or_obj.request 
            
        target_month     = checkTargetMonth(request.GET.get(API_TARGET_MONTH_PARAM_NAME, None))
        user_token, user = checkUserToken(request.GET.get(API_USER_TOKEN_PARAM_NAME, None))
            
        
        bundle_or_obj.data['resource_uri'] = self.get_resource_uri(need)
        
        need_budget_monthly = {}
        
        need_budget_monthly['end_utctimestamp']        = time.mktime(datetime(target_month.year, target_month.month+1, 1, tzinfo=target_month.tzinfo).utctimetuple())-1 #-1 because it's the last second of previous month, not first second of the next one
        if target_month >= datetime(now().year, now().month, 1, tzinfo=now().tzinfo) :
            timedelta_to_end = (datetime(now().year, now().month+1, 1, tzinfo=now().tzinfo) - now())
            need_budget_monthly['time_to_end_seconds']     = timedelta_to_end.seconds+timedelta_to_end.days*86400
            if timedelta_to_end.days*24 > TIME_TO_SHOW_HOURS : 
                need_budget_monthly['time_to_end_formatted']   = str(timedelta_to_end.days)+u' days'
            else :
                need_budget_monthly['time_to_end_formatted']   = str(int(timedelta_to_end.days*24 + math.ceil(timedelta_to_end.seconds/3600)))+u' hours'
        else :
            need_budget_monthly['time_to_end_seconds']     = 0
            need_budget_monthly['time_to_end_formatted']   = 'ended'
            
              
        
        need_budget_monthly['amount']           = need.amount  
        need_budget_monthly['currency']         = SITE_CURRENCY
        need_budget_monthly['formatted']        = '$'+filters.floatformat(need.amount, 2)
        need_budget_monthly['chart_image_URL']  = 'http://'+request.META['HTTP_HOST']+reverse('project.views.chart_image', kwargs={'project_key':need.project.key, 'need_key':need.key,})


        
        need_pledges_sum = need.getTotalMonthlyPledges(target_month)
        need_pledges               = {}
        need_pledges['amount']     = need_pledges_sum  
        need_pledges['currency']   = SITE_CURRENCY
        need_pledges['formatted']  = '$'+filters.floatformat(need_pledges_sum, 2)
        need_pledges['percent']    = round((need_pledges_sum*100)/need.amount, 2)

        donation_histories = (DonationHistory.objects
                                             .filter(project=need.project)
                                             .filter(datetime_sent__gte=datetime(target_month.year, target_month.month, 1, tzinfo=target_month.tzinfo))
                                             .filter(datetime_sent__lt=datetime(target_month.year, target_month.month+1, 1, tzinfo=target_month.tzinfo))
                                             .select_related('donationhistoryneeds'))    
        need_pledges['count']      = DonationHistoryNeeds.objects.filter(need=need).filter(donation_history__in=donation_histories).count() 
        
        
        need_other_sources_sum = need.getTotalMonthlyOtherSources(target_month)
        need_other_sources               = {}
        need_other_sources['amount']     = need_other_sources_sum  
        need_other_sources['currency']   = SITE_CURRENCY
        need_other_sources['formatted']  = '$'+filters.floatformat(need_other_sources_sum, 2)
        need_other_sources['percent']    = filters.floatformat((need_other_sources_sum*100)/need.amount, 2)

        need_redonations_sum = need.getTotalMonthlyDependantsDonations(target_month)
        need_redonations               = {}
        need_redonations['amount']     = need_redonations_sum  
        need_redonations['currency']   = SITE_CURRENCY
        need_redonations['formatted']  = '$'+filters.floatformat(need_redonations_sum, 2)
        need_redonations['percent']    = filters.floatformat((need_redonations_sum*100)/need.amount, 0)+'%'

        need_donations_total_sum = need_pledges_sum+need_other_sources_sum+need_redonations_sum
        need_donations_total               = {}
        need_donations_total['amount']     = need_donations_total_sum  
        need_donations_total['currency']   = SITE_CURRENCY
        need_donations_total['formatted']  = '$'+filters.floatformat(need_donations_total_sum, 2)
        need_donations_total['percent']    = filters.floatformat((need_donations_total_sum*100)/need.amount, 0)+'%'
            
        need_budget_outstanding               = {}
        need_budget_outstanding_sum           = need.amount - need_other_sources_sum
        need_budget_outstanding['amount']     = need_budget_outstanding_sum  
        need_budget_outstanding['currency']   = SITE_CURRENCY
        need_budget_outstanding['formatted']  = '$'+filters.floatformat(need_budget_outstanding_sum, 2)
            

        bundle_or_obj.data['budget_monthly']        = need_budget_monthly
        bundle_or_obj.data['budget_outstanding']    = need_budget_outstanding
        bundle_or_obj.data['pledges']               = need_pledges
        bundle_or_obj.data['other_sources']         = need_other_sources
        bundle_or_obj.data['redonations']           = need_redonations
        bundle_or_obj.data['donations_total']       = need_donations_total
        
        
        return bundle_or_obj



class ProjectGoalResource(ModelResource):
    project =  fields.ForeignKey(ProjectResource, 'project')
     
    class Meta:
        queryset = ProjectGoal.objects.filter(is_public=True).filter(date_ending__gt=now()).filter(date_starting__lte=now()).order_by('sort_order')
        fields = ['id', 
                  'key', 
                  'project',
                  'title',
                  'amount', 
                  'brief', 
                  'sort_order',
                  ]
        allowed_methods = ['get']
        filtering = {'project': ALL_WITH_RELATIONS, }

    def get_resource_uri(self, bundle_or_obj):
        kwargs = {'resource_name': self._meta.resource_name,}
        if isinstance(bundle_or_obj, Bundle):
            kwargs['key'] = bundle_or_obj.obj.key 
        else:
            kwargs['key'] = bundle_or_obj.key
        if self._meta.api_name is not None:
            kwargs['api_name'] = self._meta.api_name

        return self._build_reverse_url('api_dispatch_detail', kwargs = kwargs)

    def override_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<key>[\w\d_.-]+)/$" % self._meta.resource_name, self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
        ]
    

    def dehydrate(self, bundle_or_obj):
        ##values provided: title, brief,URL (w/ user token),amount,other sources,end date,days to go string,donations,redonations,donations total,filled percent,graph image URL,outstanding amount,pledgers num
        
        if isinstance(bundle_or_obj, Bundle):
            goal = bundle_or_obj.obj
        else :
            goal = bundle_or_obj

        request = bundle_or_obj.request 
            
        user_token, user = checkUserToken(request.GET.get(API_USER_TOKEN_PARAM_NAME, None))
            
        
        bundle_or_obj.data['resource_uri'] = self.get_resource_uri(goal)
        
        goal_budget_total = {}
        
        goal_budget_total['end_utctimestamp']                = time.mktime(goal.date_ending.utctimetuple())  
        if goal.date_ending >= datetime(now().year, now().month, 1, tzinfo=now().tzinfo) :
            timedelta_to_end = goal.date_ending - now()
            goal_budget_total['time_to_end_seconds']         = timedelta_to_end.seconds+timedelta_to_end.days*86400
            if timedelta_to_end.days*24 > TIME_TO_SHOW_HOURS : 
                goal_budget_total['time_to_end_formatted']   = str(timedelta_to_end.days)+u' days'
            else :
                goal_budget_total['time_to_end_formatted']   = str(int(timedelta_to_end.days*24 + math.ceil(timedelta_to_end.seconds/3600)))+u' hours'
        else :
            goal_budget_total['time_to_end_seconds']         = 0
            goal_budget_total['time_to_end_formatted']       = 'ended'

        
        goal_budget_total['amount']           = goal.amount  
        goal_budget_total['currency']         = SITE_CURRENCY
        goal_budget_total['formatted']        = '$'+filters.floatformat(goal.amount, 2)
        goal_budget_total['chart_image_URL']  = 'http://'+request.META['HTTP_HOST']+reverse('project.views.chart_image', kwargs={'project_key':goal.project.key, 'goal_key':goal.key,})

        goal_pledges_sum = goal.getTotalPledges()
        goal_pledges               = {}
        goal_pledges['amount']     = goal_pledges_sum  
        goal_pledges['currency']   = SITE_CURRENCY
        goal_pledges['formatted']  = '$'+filters.floatformat(goal_pledges_sum, 2)
        goal_pledges['percent']    = round((goal_pledges_sum*100)/goal.amount, 2)
        goal_pledges['count']      = DonationHistoryGoals.objects.filter(goal=goal).count() 
        
        
        goal_other_sources_sum = goal.getTotalOtherSources()
        goal_other_sources               = {}
        goal_other_sources['amount']     = goal_other_sources_sum  
        goal_other_sources['currency']   = SITE_CURRENCY
        goal_other_sources['formatted']  = '$'+filters.floatformat(goal_other_sources_sum, 2)
        goal_other_sources['percent']    = filters.floatformat((goal_other_sources_sum*100)/goal.amount, 2)

        goal_redonations_sum = goal.getTotalRedonations()
        goal_redonations               = {}
        goal_redonations['amount']     = goal_redonations_sum  
        goal_redonations['currency']   = SITE_CURRENCY
        goal_redonations['formatted']  = '$'+filters.floatformat(goal_redonations_sum, 2)
        goal_redonations['percent']    = filters.floatformat((goal_redonations_sum*100)/goal.amount, 0)+'%'

        goal_donations_total_sum = goal_pledges_sum+goal_other_sources_sum+goal_redonations_sum
        goal_donations_total               = {}
        goal_donations_total['amount']     = goal_donations_total_sum  
        goal_donations_total['currency']   = SITE_CURRENCY
        goal_donations_total['formatted']  = '$'+filters.floatformat(goal_donations_total_sum, 2)
        goal_donations_total['percent']    = filters.floatformat((goal_donations_total_sum*100)/goal.amount, 0)+'%'
            
        goal_budget_outstanding               = {}
        goal_budget_outstanding_sum           = goal.amount - goal_other_sources_sum
        goal_budget_outstanding['amount']     = goal_budget_outstanding_sum  
        goal_budget_outstanding['currency']   = SITE_CURRENCY
        goal_budget_outstanding['formatted']  = '$'+filters.floatformat(goal_budget_outstanding_sum, 2)
            

        bundle_or_obj.data['goal_profile_URL']      = 'http://'+request.META['HTTP_HOST']+reverse('project.views.goal_view', kwargs={'project_key':goal.project.key, 'goal_key':goal.key,})+'?'+API_USER_TOKEN_PARAM_NAME+'='+user_token
        bundle_or_obj.data['goal_budget']           = goal_budget_total
        bundle_or_obj.data['goal_outstanding']      = goal_budget_outstanding
        bundle_or_obj.data['pledges']               = goal_pledges
        bundle_or_obj.data['other_sources']         = goal_other_sources
        bundle_or_obj.data['redonations']           = goal_redonations
        bundle_or_obj.data['donations_total']       = goal_donations_total
        
        return bundle_or_obj




