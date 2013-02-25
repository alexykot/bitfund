import datetime

from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse 
from django.shortcuts import render_to_response, get_object_or_404 
from django.template import RequestContext
from django.forms.formsets import formset_factory
from django.utils.datetime_safe import datetime
from django.utils.timezone import utc, now 

#from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import authenticate
from django.contrib.auth import login as django_user_login
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login

from bitfund.core.settings.project import DEFAULT_PASSWORD, DEFAULT_MONTHLY_DONATION_AMOUNT, DEFAULT_ONETIME_DONATION_AMOUNT
from bitfund.project.models import *
from bitfund.project.forms import *
from bitfund.project.decorators import *
from bitfund.pledger.models import *


@user_is_not_project_maintainer
def support(request, project_key, support_type='onetime'):
    project = get_object_or_404(Project, key=project_key)

    #PASRING PRESELECTED
    needsgoals_list = []
    project_needs      = ProjectNeed.objects.filter(project=project.id).filter(is_public=True)
    for need in project_needs :
        needsgoals_list.append(('need_'+str(need.id), need.title))

    project_goals               = (ProjectGoal.objects.filter(project=project.id)
                                                      .filter(is_public=True)
                                                      .filter(date_ending__gt=now())
                                                      .filter(date_starting__lt=now())
                                                      )
    for goal in project_goals :
        needsgoals_list.append(('goal_'+str(goal.id), goal.title))

    preselected_form = ProjectNeedsGoalsListForm(project_needsgoals_choices=needsgoals_list, data=request.GET)
    preselected_needs = []
    preselected_goals = []
    if preselected_form.is_valid() :
        have_preselected = True
        for needgoal in preselected_form.cleaned_data['needsgoals'] :
            if (needgoal.split('_')[0] == 'need') :
                preselected_needs.append(int(needgoal.split('_')[1]))
            else :
                preselected_goals.append(int(needgoal.split('_')[1]))
    else :
        have_preselected = False

    
    #FETCHING DONATIONS CART AND SUBSCRIPTIONS DATA            
    if DonationCart.objects.filter(project=project).filter(user=request.user.id).count() == 1 :
        donation_cart = DonationCart.objects.filter(project=project).filter(user=request.user.id)[0]
    else :
        donation_cart = DonationCart()
        donation_cart.project = project
        
    if request.user.is_authenticated() and DonationSubscription.objects.filter(user=request.user.id).filter(project=project).count() :
        donation_subscription = DonationSubscription.objects.filter(user=request.user.id).filter(project=project)[0]
    else :
        donation_subscription = False


    #DEFINING NEEDS FORMSET DATA
    SupportNeedsFormSet = formset_factory(SupportProjectForm, extra=0)
    initial_data_needs  = []
    project_needs       = ProjectNeed.objects.filter(project=project)
    for need in project_needs :
        if donation_cart.id :
            if DonationCartNeeds.objects.filter(donation_cart=donation_cart).filter(need=need.id).count() :
                amount = DonationCartNeeds.objects.filter(donation_cart=donation_cart).filter(need=need.id)[0].amount
            elif have_preselected and need.id in preselected_needs : 
                amount = DEFAULT_MONTHLY_DONATION_AMOUNT
            else :
                amount = '0'
        elif donation_subscription and DonationSubscriptionNeeds.objects.filter(donation_subscription=donation_subscription).filter(need=need).count() :
            amount = DonationSubscriptionNeeds.objects.filter(donation_subscription=donation_subscription).filter(need=need)[0].amount
        elif (have_preselected and need.id in preselected_needs) or not have_preselected :
            amount = DEFAULT_MONTHLY_DONATION_AMOUNT
        else :
            amount = '0'    
            
        
        initial_data_needs.append({  'amount'           : amount,
                                     'need'             : need.id,
                                     'need_title'       : need.title,
                                     'need_brief'       : need.brief,
                                     'is_monthly'       : (support_type=='monthly') 
                                       })

    #DEFINING GOALS FORMSET DATA
    SupportGoalsFormSet = formset_factory(SupportProjectForm, extra=0)
    initial_data_goals  = []
    project_goals       = (ProjectGoal.objects
                                        .filter(project=project)
                                        .filter(is_public=True)
                                        .filter(date_ending__gt=now())
                                        .filter(date_starting__lt=now())
                                        .order_by('sort_order')
                                        )
                                                                
    for goal in project_goals :
        if donation_cart.id : 
            if DonationCartGoals.objects.filter(donation_cart=donation_cart).filter(goal=goal.id).count() :
                amount = DonationCartGoals.objects.filter(donation_cart=donation_cart).filter(goal=goal.id)[0].amount
            elif have_preselected and goal.id in preselected_goals : 
                amount = DEFAULT_ONETIME_DONATION_AMOUNT
            else :
                amount = 0    
        elif (have_preselected and goal.id in preselected_goals) or not have_preselected :
            amount = DEFAULT_ONETIME_DONATION_AMOUNT
        else :
            amount = 0
        
        initial_data_goals.append({  'amount'           : amount,
                                     'goal'             : goal.id,
                                     'goal_title'       : goal.title,
                                     'goal_brief'       : goal.brief,
                                     'goal_date_ending' : goal.date_ending,
                                     
                                     })
    
    
    #VALIDATINGAND SAVING SUBMITTED PLEDGES
    if request.method == 'POST':
        formset_needs = SupportNeedsFormSet(request.POST, initial=initial_data_needs, prefix='needs') 
        formset_goals = SupportGoalsFormSet(request.POST, initial=initial_data_goals, prefix='goals')
        email_form    = NewBackerForm(request.POST, prefix='email')
        
        if formset_needs.is_valid() and formset_goals.is_valid() and ((not request.user.is_authenticated() and email_form.is_valid()) or request.user.is_authenticated()) :
            
            if not request.user.is_authenticated() :
                email = email_form.cleaned_data['user_email']
                if (User.objects.filter(username=email).count() or User.objects.filter(email=email).count()) :
                    user = User.objects.get(email=email_form.cleaned_data['user_email'])
                    if not user.groups.filter(name='strangers').count() :
                        return redirect_to_login(reverse('bitfund.project.views.support', args=(project.key, support_type,)))
                else :
                    user = User.objects.create_user(email_form.cleaned_data['user_email'], email_form.cleaned_data['user_email'], DEFAULT_PASSWORD)
                    user.save()
                    Group.objects.get(name='strangers').user_set.add(user) 
                    
                user = authenticate(username=user.username, password=DEFAULT_PASSWORD)
                django_user_login(request, user)
                
            else : 
                user = request.user
                    
            if not donation_cart.id :                
                donation_cart.user = user 
                donation_cart.save()
            
            donation_cart.needs.clear()
            donation_cart.goals.clear()

            for need_form in formset_needs :
                if need_form.cleaned_data['amount'] > 0 :
                    donation_cart_need = DonationCartNeeds()
                    donation_cart_need.donation_cart = donation_cart
                    donation_cart_need.amount        = need_form.cleaned_data['amount']
                    if (need_form.cleaned_data['is_monthly']) : 
                        donation_cart_need.donation_type = 'monthly'
                    else : 
                        donation_cart_need.donation_type = 'onetime'
                        
                    donation_cart_need.need = ProjectNeed.objects.filter(project=project).get(pk=need_form.cleaned_data['need'])
                    donation_cart_need.save()

            for goal_form in formset_goals :
                if goal_form.cleaned_data['amount'] > 0 :
                    donation_cart_goal = DonationCartGoals()
                    donation_cart_goal.donation_cart = donation_cart
                    donation_cart_goal.amount        = goal_form.cleaned_data['amount']
                    donation_cart_goal.goal          = ProjectGoal.objects.filter(project=project).get(pk=goal_form.cleaned_data['goal'])
                    donation_cart_goal.save()

            return HttpResponseRedirect(reverse('bitfund.project.views.budget', args=(project.key,)))
        else :
            return render_to_response('project/support.djhtm', {'project'        : project,
                                                                'request'        : request,
                                                                'formset_needs'  : formset_needs, 
                                                                'formset_goals'  : formset_goals,
                                                                'email_form'     : email_form,
                                                                    }, context_instance=RequestContext(request))
        
    else :
        formset_needs = SupportNeedsFormSet(initial=initial_data_needs, prefix='needs') 
        formset_goals = SupportGoalsFormSet(initial=initial_data_goals, prefix='goals')
        email_form    = NewBackerForm(prefix='email')
        
    return render_to_response('project/support.djhtm', {'project'        : project,
                                                        'request'        : request,
                                                        'formset_needs'  : formset_needs, 
                                                        'formset_goals'  : formset_goals,
                                                        'email_form'     : email_form,
                                                         
                                                                }, context_instance=RequestContext(request))
    

@user_is_not_project_maintainer
def drop_support(request, project_key):
    project = get_object_or_404(Project, key=project_key)
    
    if (request.user.is_authenticated()) :
        donation_cart_list = DonationCart.objects.filter(user=request.user.id).filter(project=project.id)
        
        for donation_cart in donation_cart_list :
            DonationCartNeeds.objects.filter(donation_cart=donation_cart).delete()
            DonationCartGoals.objects.filter(donation_cart=donation_cart).delete()
            
        donation_cart_list.delete()
        
    return HttpResponseRedirect(reverse('bitfund.project.views.budget', args=(project.key,)))


@user_is_not_project_maintainer
@login_required
def toggle_grateful(request, project_key):
    project = get_object_or_404(Project, key=project_key)

    project.toggleGratefulUser(request.user)

    return HttpResponseRedirect(reverse('bitfund.project.views.budget', args=(project.key,)))

