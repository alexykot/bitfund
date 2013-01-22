from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse 
from django.shortcuts import render_to_response, get_object_or_404 
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum

from datetime import date

from project.models import *
from pledger.models import *
from project.forms import *
from project.decorators import *
from bitfund.settings_custom import MAX_NEEDS_N_GOALS_ON_PROJECT_PAGE, MAX_USERS_ON_PROJECT_PAGE


def view(request, project_key):
    project = get_object_or_404(Project, key=project_key)

    template_data = {'project' : project,
                     'request' : request,
                     'today'   : date.today(),
                     }
    
    template_data['project_users'] = ProjectUserRole.objects.select_related().filter(project=project).order_by('sort_order')[:MAX_USERS_ON_PROJECT_PAGE]
    
    #template_data['maintainer_profile']         = Profile.objects.get(user_id=project.maintainer_id)
     
    project_needs       = ProjectNeed.objects.filter(project=project.id)
    project_needs_count = project_needs.count()
    project_goals       = ProjectGoal.objects.filter(project=project.id)
    project_goals_count = project_goals.count()
    template_data['project_needs']              = project_needs
    template_data['project_goals']              = project_goals
    template_data['project_needs_count']        = project_needs_count 
    template_data['project_goals_count']        = project_goals_count
    if project_needs_count :
        project_needs_total                     = project_needs.aggregate(Sum('amount'))['amount__sum']
    else :
        project_needs_total                     = 0
    if project_goals_count :
        project_goals_total                     = project_goals.aggregate(Sum('amount'))['amount__sum']
    else :
        project_goals_total                     = 0
    template_data['project_needsngoals_total']  = project_needs_total+project_goals_total
    
    needsngoals_list = []
    index = 0
    for need in project_needs:
        if (index >= MAX_NEEDS_N_GOALS_ON_PROJECT_PAGE) :
            break 
        needsngoals_list.append({'title' : need.title})
        index = index+1 
    
    for goal in project_goals:
        if (index >= MAX_NEEDS_N_GOALS_ON_PROJECT_PAGE) :
            break 
        needsngoals_list.append({'title' : goal.title})
        index = index+1 
    
    template_data['needsngoals_list'] = needsngoals_list
    if project_needs_count+project_goals_count > MAX_NEEDS_N_GOALS_ON_PROJECT_PAGE :
        template_data['project_needs_count_to_show'] = project_needs_count+project_goals_count
    
    
    if (request.user.is_authenticated) :
        donation_cart    = DonationCart.objects.filter(user=request.user.id).filter(project=project.id)  
        if donation_cart.count() :
            donation_cart = donation_cart[0]
            template_data['donation_cart']             = donation_cart
            template_data['donation_cart_needs_onetime_count'] = DonationCartNeeds.objects.filter(donation_cart=donation_cart).filter(donation_type='onetime').count()
            template_data['donation_cart_needs_onetime_sum']   = DonationCartNeeds.objects.filter(donation_cart=donation_cart).filter(donation_type='onetime').aggregate(Sum('amount'))['amount__sum']
            template_data['donation_cart_needs_monthly_count'] = DonationCartNeeds.objects.filter(donation_cart=donation_cart).filter(donation_type='monthly').count()
            template_data['donation_cart_needs_monthly_sum']   = DonationCartNeeds.objects.filter(donation_cart=donation_cart).filter(donation_type='monthly').aggregate(Sum('amount'))['amount__sum']
            template_data['donation_cart_goals_count'] = DonationCartGoals.objects.filter(donation_cart=donation_cart).count()
            template_data['donation_cart_goals_sum']   = DonationCartGoals.objects.filter(donation_cart=donation_cart).aggregate(Sum('amount'))['amount__sum']
            
        donation_history = DonationHistory.objects.filter(user=request.user.id).filter(project=project.id)
        if donation_history.count() :
            donation_history_newest = donation_history.order_by('-datetime_sent')[0]
            template_data['donation_history_newest']        = donation_history_newest
            template_data['donation_history_newest_needsngoals_count'] = donation_history_newest.needs.all().count() + donation_history_newest.goals.all().count()   
            template_data['donation_history_newest_needsngoals_sum']   = donation_history_newest.needs.all().aggregate(Sum('amount'))['amount__sum'] + donation_history_newest.goals.all().aggregate(Sum('amount'))['amount__sum']   
            

        donation_subscription = DonationSubscription.objects.filter(user=request.user.id).filter(project=project.id).filter(active=True)
        if donation_subscription.count() :
            template_data['donation_subscription']             = donation_subscription[0] 
            template_data['donation_subscription_needs_count'] = donation_subscription.needs.all().count()
            template_data['donation_subscription_needs_sum']   = donation_subscription.needs.all().aggregate(Sum('amount'))['amount__sum']

    
    template_data['donations_total_pledgers']  = (DonationHistory.objects
                                                                 .filter(project=project)
                                                                 .filter(datetime_sent__gte=date(date.today().year, date.today().month, 1))
                                                                 .aggregate(Count('user', distinct=True))['user__count'])    
    donation_histories = (DonationHistory.objects
                                         .filter(project=project)
                                         .filter(datetime_sent__gte=date(date.today().year, date.today().month, 1))
                                         .select_related('donationhistoryneeds'))    

    donationhistory_total_sum = 0

    donationhistoryneeds_sum = (DonationHistoryNeeds.objects
                                                    .filter(donation_history__in=donation_histories)
                                                    .aggregate(Sum('amount'))['amount__sum'])
    if donationhistoryneeds_sum :
        donationhistory_total_sum = donationhistory_total_sum + donationhistoryneeds_sum        
    
    donationhistorygoals_sum = (DonationHistoryGoals.objects
                                                    .filter(donation_history__in=donation_histories)
                                                    .aggregate(Sum('amount'))['amount__sum'])
    if donationhistorygoals_sum :
        donationhistory_total_sum = donationhistory_total_sum + donationhistorygoals_sum        
      
    other_sources_amount = 0
    if project.other_sources :
        other_sources_amount = project.other_sources       

    template_data['donations_total_sum']  = donationhistory_total_sum

    template_data['donationhistory_radiant']  = round(360*(donationhistory_total_sum / template_data['project_needsngoals_total']))
    template_data['other_sources_radiant']    = round(360*(other_sources_amount / template_data['project_needsngoals_total']))
    template_data['total_gained_percent']     = int(round(((donationhistory_total_sum+other_sources_amount)*100) / template_data['project_needsngoals_total'])) 

    if not (template_data['donationhistory_radiant'] and template_data['other_sources_radiant']) :
        template_data['donationhistory_radiant'] = 2
        template_data['other_sources_radiant']   = 1
    

    
    
    
    return render_to_response('project/view.djhtm', template_data, context_instance=RequestContext(request))

