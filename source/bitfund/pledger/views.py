from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, HttpResponseGone
from django.core.urlresolvers import reverse 
from django.shortcuts import render_to_response 
from django.template import RequestContext
from django.forms.formsets import formset_factory
from django.contrib.auth.decorators import login_required
from django.utils import simplejson

from bitfund.project.models import *
from bitfund.pledger.models import *
from bitfund.pledger.forms import *
from bitfund.settings_project import FAKE_CHECKOUT_SYSTEM_URL

import urllib
import urllib2
import urlparse

@login_required
def donations_overview(request):
    ProjectsSupportFormSet = formset_factory(SupportProjectForm, extra=0)
    donations               = DonationCart.objects.filter(user=request.user.id).prefetch_related('project')
    
    initial_data_projects_donations  = []
    projects_total = 0
    projects_count = 0
    projects_total_needs_count = 0
    projects_total_goals_count = 0
    for donation in donations :
        projects_count                  = projects_count + 1
        project_support_total           = donation.getProjectSupportTotal()
        projects_total                  = projects_total + project_support_total
        project_support_needs_count     = donation.getProjectSupportNeedsCount()
        project_support_goals_count     = donation.getProjectSupportGoalsCount()
        projects_total_needs_count      = projects_total_needs_count + project_support_needs_count
        projects_total_goals_count      = projects_total_goals_count + project_support_goals_count
        initial_data_projects_donations.append({'donation_cart_id'              : donation.id,
                                                'support_total'                 : project_support_total,
                                                'project_id'                    : donation.project.id,
                                                'project_key'                   : donation.project.key,
                                                'project_title'                 : donation.project.title,
                                                'project_description'           : donation.project.description,
                                                'project_support_needs_count'   : project_support_needs_count,
                                                'project_support_goals_count'   : project_support_goals_count,
                                                })
    
    initial_data_projects_total  = {'support_total'                 : projects_total,
                                    }    

    
    if request.method == 'POST':
        projects_formset = ProjectsSupportFormSet(request.POST, initial=initial_data_projects_donations, prefix='projects')
        totals_form      = SupportProjectForm(request.POST, initial=initial_data_projects_total, prefix='totals')
        if projects_formset.is_valid() and totals_form.is_valid() :
            
            for form in projects_formset :
                if DonationCart.objects.get(pk=form.cleaned_data['donation_cart_id']).user.id != request.user.id :
                    return HttpResponseForbidden()
                      
                for donation_data in initial_data_projects_donations :
                    if form.cleaned_data['donation_cart_id'] == donation_data['donation_cart_id'] :
                        if form.cleaned_data['support_total'] != donation_data['support_total'] :
                            if form.cleaned_data['support_total'] > 0 :
                                DonationCart.adjustProjectDonationProportionally(form.cleaned_data['donation_cart_id'], form.cleaned_data['support_total'], donation_data['support_total'])
                            else : 
                                DonationCart.get(pk=donation_data['support_total']).delete()
                                 
                             
            if totals_form.cleaned_data['support_total'] != initial_data_projects_total['support_total'] :
                if totals_form.cleaned_data['support_total'] > 0 :
                    DonationCart.adjustTotalDonationProportionally(request.user.id, totals_form.cleaned_data['support_total'])
                else :
                    DonationCart.objects.filter(user=request.user).delete()     
                    
            
            return HttpResponseRedirect(reverse('pledger.views.donations_overview', args=()))
        else :
            return render_to_response('pledger/donations_overview.djhtm', {'request'                    : request,
                                                                           'projects_formset'           : projects_formset,
                                                                           'totals_form'                : totals_form,
                                                                           'projects_total'             : projects_total,
                                                                           'projects_count'             : projects_count,
                                                                            'projects_total_needs_count'    : projects_total_needs_count,
                                                                            'projects_total_goals_count'    : projects_total_goals_count,
                                                                            }, context_instance=RequestContext(request))
            

    else :
        projects_formset = ProjectsSupportFormSet(initial=initial_data_projects_donations, prefix='projects')
        totals_form      = SupportProjectForm(initial=initial_data_projects_total, prefix='totals')
        
        
    return render_to_response('pledger/donations_overview.djhtm', {'request'                    : request,
                                                                   'projects_formset'           : projects_formset,
                                                                   'totals_form'                : totals_form,
                                                                   'projects_total'             : projects_total,
                                                                   'projects_count'             : projects_count,
                                                                    'projects_total_needs_count'    : projects_total_needs_count,
                                                                    'projects_total_goals_count'    : projects_total_goals_count,
                                                                    }, context_instance=RequestContext(request))


@login_required
def donations_update(request):
    if request.method == 'POST':

        ProjectsSupportFormSet = formset_factory(SupportProjectForm, extra=0)
        donations               = DonationCart.objects.filter(user=request.user.id).prefetch_related('project')
        
        initial_data_projects_donations  = []
        projects_total = 0
        projects_count = 0
        projects_total_needs_count = 0
        projects_total_goals_count = 0
        for donation in donations :
            projects_count                  = projects_count + 1
            project_support_total           = donation.getProjectSupportTotal()
            projects_total                  = projects_total + project_support_total
            project_support_needs_count     = donation.getProjectSupportNeedsCount()
            project_support_goals_count     = donation.getProjectSupportGoalsCount()
            projects_total_needs_count      = projects_total_needs_count + project_support_needs_count
            projects_total_goals_count      = projects_total_goals_count + project_support_goals_count
            initial_data_projects_donations.append({'donation_cart_id'              : donation.id,
                                                    'support_total'                 : project_support_total,
                                                    'project_id'                    : donation.project.id,
                                                    'project_key'                   : donation.project.key,
                                                    'project_title'                 : donation.project.title,
                                                    'project_description'           : donation.project.description,
                                                    'project_support_needs_count'   : project_support_needs_count,
                                                    'project_support_goals_count'   : project_support_goals_count,
                                                    })
        
        initial_data_projects_total  = {'support_total'                 : projects_total,
                                        }    

        projects_formset = ProjectsSupportFormSet(request.POST, initial=initial_data_projects_donations, prefix='projects')
        totals_form      = SupportProjectForm(request.POST, initial=initial_data_projects_total, prefix='totals')
        if projects_formset.is_valid() and totals_form.is_valid() :
            for form in projects_formset :
                if DonationCart.objects.get(pk=form.cleaned_data['donation_cart_id']).user.id != request.user.id :
                    return HttpResponseForbidden()
                      
                for donation_data in initial_data_projects_donations :
                    if form.cleaned_data['donation_cart_id'] == donation_data['donation_cart_id'] :
                        if form.cleaned_data['support_total'] != donation_data['support_total'] :
                            if form.cleaned_data['support_total'] > 0 :
                                DonationCart.adjustProjectDonationProportionally(form.cleaned_data['donation_cart_id'], form.cleaned_data['support_total'], donation_data['support_total'])
                            else : 
                                DonationCart.get(pk=donation_data['support_total']).delete()
                                 
                             
            if totals_form.cleaned_data['support_total'] != initial_data_projects_total['support_total'] :
                if totals_form.cleaned_data['support_total'] > 0 :
                    DonationCart.adjustTotalDonationProportionally(request.user.id, totals_form.cleaned_data['support_total'])
                else :
                    DonationCart.objects.filter(user=request.user).delete()     

            data = {'error': False,
                    'donations_list': {},
                    }
                    
            donations               = DonationCart.objects.filter(user=request.user.id).prefetch_related('project')
            
            projects_total = 0
            for donation in donations :
                projects_count                  = projects_count + 1
                project_support_total           = donation.getProjectSupportTotal()   
                projects_total                  = projects_total + project_support_total
 
                data['donations_list'][donation.id] = project_support_total  
            
            data['donations_total']  = projects_total
                    
                    
            return HttpResponse(simplejson.dumps(data), content_type="application/json")
        else :
            return HttpResponse(simplejson.dumps({'error': True}), content_type="application/json")
            

    return HttpResponse(simplejson.dumps({'error': True}), content_type="application/json")

@login_required
def checkout(request):
    donations = DonationCart.objects.filter(user=request.user.id)
    amount_total = 0
    for donation in donations :
        amount_total = amount_total + donation.getProjectSupportTotal()

    checkout_url = FAKE_CHECKOUT_SYSTEM_URL+'?'+urllib.urlencode({'amount'           : amount_total, 
                                                                  'username'         : request.user.username,
                                                                  'email'            : request.user.email,
                                                                  'authority_name'   : 'bitfund',
                                                                  })
    return HttpResponseRedirect(checkout_url)


def fake_external_checkout(request):
    if request.method == 'POST':
        return HttpResponseRedirect(reverse('pledger.views.checkout_success'))
    else :    
        return render_to_response('pledger/fake_external_checkout.djhtm', {'request' : request, }, context_instance=RequestContext(request))

@login_required
def checkout_success(request):
    donations = DonationCart.objects.filter(user=request.user.id).prefetch_related('project')
    
    request.session['recent_donations'] = {}
        
    for donation in donations :
        donation_transaction      = False
        donation_subscription = False
        project_id              = donation.project.id
        project_total_donation  = 0
        
        donation_cart_needs = DonationCartNeeds.objects.filter(donation_cart=donation).prefetch_related('need') 
        for donation_cart_need in donation_cart_needs :
            if donation_cart_need.donation_type == 'onetime' :
                if not donation_transaction :
                    donation_transaction                            = DonationTransaction()
                    donation_transaction.transaction_type           = 'pledger'
                    donation_transaction.user                       = request.user
                    donation_transaction.accepting_project          = donation.project
                    donation_transaction.accepting_project_key      = donation.project.key
                    donation_transaction.accepting_project_title    = donation.project.title
                    donation_transaction.save()
                    
                    donation_transaction.transaction_hash           = donation_transaction.generateHash()
                    donation_transaction.save()

                    donation_transaction_details                        = DonationTransactionDetails()
                    donation_transaction_details.donation_transaction   = donation_transaction
                    donation_transaction_details.username               = request.user.username
                    donation_transaction_details.email                  = request.user.email
                    donation_transaction_details.save()


                donation_transaction_need                       = DonationTransactionNeeds()
                donation_transaction_need.donation_transaction  = donation_transaction
                donation_transaction_need.need                  = donation_cart_need.need 
                donation_transaction_need.need_title            = donation_cart_need.need.title 
                donation_transaction_need.need_key              = donation_cart_need.need.key
                donation_transaction_need.amount                = donation_cart_need.amount
                donation_transaction_need.donation_type         = donation_cart_need.donation_type
                donation_transaction_need.save()
                
            elif donation_cart_need.donation_type == 'monthly' :
                if not donation_subscription :
                    donation_subscription = DonationSubscription()
                    donation_subscription.user              = request.user
                    donation_subscription.project           = donation.project
                    donation_subscription.active            = True
                    donation_subscription.save()
                    
                donation_subscription_need = DonationSubscriptionNeeds()
                donation_subscription_need.donation_subscription = donation_subscription
                donation_subscription_need.need   = donation_cart_need.need
                donation_subscription_need.amount = donation_cart_need.amount
                
            project_total_donation = project_total_donation + donation_cart_need.amount
                
            donation_cart_need.delete()
    
        donation_cart_goals = DonationCartGoals.objects.filter(donation_cart=donation).prefetch_related('goal') 
        for donation_cart_goal in donation_cart_goals :
            if not donation_transaction :
                donation_transaction = DonationTransaction()
                donation_transaction.user                   = request.user
                donation_transaction.username               = request.user.username
                donation_transaction.email                  = request.user.email
                donation_transaction.project                = donation.project
                donation_transaction.project_key            = donation.project.key
                donation_transaction.project_title          = donation.project.title
                donation_transaction.save()
            
            donation_transaction_goal = DonationTransactionGoals()
            donation_transaction_goal.donation_transaction    = donation_transaction
            donation_transaction_goal.goal                = donation_cart_goal.goal 
            donation_transaction_goal.goal_title          = donation_cart_goal.goal.title 
            donation_transaction_goal.goal_key            = donation_cart_goal.goal.key
            donation_transaction_goal.amount              = donation_cart_goal.amount
            donation_transaction_goal.goal_date_ending    = donation_cart_goal.goal.date_ending
            donation_transaction_goal.save()
            
            project_total_donation = project_total_donation + donation_cart_goal.amount
            
            donation_cart_goal.delete()
        
        request.session['recent_donations'][project_id] = project_total_donation    
        
        donation.delete()
    
    return HttpResponseRedirect(reverse('pledger.views.donations_success'))


@login_required
def donations_success(request):
    
    if not request.session['recent_donations']:
        return HttpResponseRedirect(reverse('bitfund.views.index'))
    
    
    recent_donations = {}
    index = 0
    for recent_donation_project_id in request.session['recent_donations']:
        index = index + 1
        recent_donations[index] = {'project_title':    Project.objects.get(pk=recent_donation_project_id).title,
                                   'donation_amount':  request.session['recent_donations'][recent_donation_project_id],
                                                        }
        
        
    
    return render_to_response('pledger/donations_success.djhtm', {'request' : request, 
                                                                  'recent':  recent_donations,
                                                                  'projects_count':index, 
                                                                  }, context_instance=RequestContext(request))
