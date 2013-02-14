import math

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.db.models import Count, Sum
from django.utils.datetime_safe import datetime
from django.utils.timezone import utc, now

from bitfund.core.settings.project import MAX_EXPENSES_ON_PROJECT_PAGE, SITE_CURRENCY_CODE, SITE_CURRENCY_SIGN
from bitfund.project.models import *
from bitfund.project.forms import *
from bitfund.pledger.models import *

def view(request, project_key):
    project = get_object_or_404(Project, key=project_key)

    template_data = {'project': project,
                     'request': request,
                     'today': datetime.utcnow().replace(tzinfo=utc).today(),
    }

    #GENERAL PROJECT INFO
    template_data['project_categories'] = project.categories.all()
    if project.maintainer_id == request.user.id :
        template_data['project_edit_access'] = True
    else :
        template_data['project_edit_access'] = False


    #GENERAL BUDGET DATA    
    project_needs               = ProjectNeed.objects.filter(project=project.id).filter(is_public=True).order_by('sort_order')
    project_needs_count         = project_needs.count()
    project_needs_total         = (project_needs.aggregate(Sum('amount'))['amount__sum']) or 0

    project_goals               = (ProjectGoal.objects.filter(project=project.id)
                                                      .filter(is_public=True)
                                                      .filter(date_ending__gt=now())
                                                      .filter(date_ending__lt=datetime(now().year, now().month+1, 1, tzinfo=now().tzinfo))
                                                      .filter(date_starting__lt=now())
                                                      .order_by('sort_order')
                                                      )
    project_goals_count         = project_goals.count()

    needs_list = []
    for need in project_needs :
        needs_list.append(('need_'+str(need.id), need.title))

    template_data['needsgoals_form']                  = ProjectNeedsGoalsListForm(project_needsgoals_choices=needs_list) 
    template_data['project_needs_count']              = project_needs_count 
    template_data['project_goals_count']              = project_goals_count
    template_data['project_needs_total']              = project_needs_total
    template_data['project_needs_to_show_initially']  = MAX_EXPENSES_ON_PROJECT_PAGE 
    template_data['project_moar_needsgoals_count']    = max((project_needs_count-MAX_EXPENSES_ON_PROJECT_PAGE),0)
    

    #CURRENT USER DONATIONS
    """
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
    """

    #ALL USERS DONATIONS
    pledges_needs_total_sum, pledges_goals_total_sum           = project.getTotalMonthlyPledges()
    template_data['donations_total_sum']      = pledges_needs_total_sum
    template_data['donations_total_pledgers'] = project.getTotalMonthlyBackers()


    #REDONATIONS
    redonations_needs_total_sum, redonations_goals_total_sum  = project.getTotalMonthlyRedonations()
    template_data['redonations_needs_total_sum']  = redonations_needs_total_sum
    template_data['redonations_goals_total_sum']  = redonations_goals_total_sum

    #OTHER SOURCES
    other_sources_needs_total_sum, other_sources_goals_total_sum  = project.getTotalMonthlyOtherSources()
    other_sources_total_sum = other_sources_needs_total_sum + other_sources_goals_total_sum
    template_data['other_sources_total_sum']  = other_sources_total_sum
    other_sources_per_needgoal_amount         = int(round(other_sources_total_sum/(project_goals_count+project_needs_count))) #this needs to be replaced with direct budget assignment


    #DONUT CHART RADIANTS
    template_data['pledges_radiant'] = min(360, round(
        360 * (redonations_needs_total_sum / template_data['project_needs_total'])))
    template_data['redonations_radiant'] = min(360, round(
        360 * (redonations_needs_total_sum / template_data['project_needs_total'])))
    template_data['other_sources_radiant'] = min(360, round(
        360 * (other_sources_total_sum / template_data['project_needs_total'])))

    template_data['total_gained_percent'] = int(round(
        ((redonations_needs_total_sum + other_sources_total_sum) * 100) / template_data['project_needs_total']))

    if not (template_data['pledges_radiant']  or template_data['redonations_radiant'] or template_data['other_sources_radiant']) :
        template_data['pledges_radiant'] = 2
        template_data['redonations_radiant'] = 1
        template_data['other_sources_radiant'] = 1


    #GOALS DETAILS LIST
    project_goals = (ProjectGoal.objects
                     .filter(project=project)
                     .filter(is_public=True)
                     .filter(date_ending__gt=now())
                     .filter(date_starting__lt=now())
                     .order_by('sort_order')
    )
    template_data['project_goals'] = []

    for goal in project_goals:
        donations_amount             = (DonationTransactionGoals.objects.filter(goal=goal)
                                        .aggregate(Sum('amount'))['amount__sum']) or 0
        donations_radiant            = min(360, round(360 * (donations_amount/goal.amount)))
        other_sources_radiant        = min(360, round(360 * (other_sources_per_needgoal_amount/goal.amount)))
        total_percent                = int(math.ceil(((donations_amount+other_sources_per_needgoal_amount) * 100) / goal.amount))
        
        if not (donations_radiant or other_sources_radiant) :
            donations_radiant     = 2
            other_sources_radiant = 1
        
        template_data['project_goals'].append({'id'                     : goal.id,
                                               'key'                    : goal.key,
                                               'title'                  : goal.title,
                                               'brief'                  : goal.brief,
                                               'video_url'              : goal.video_url,
                                               'image'                  : goal.image,
                                               'amount'                 : goal.amount,
                                               'other_sources'          : other_sources_per_needgoal_amount,
                                               'date_ending'            : goal.date_ending,
                                               'days_to_end'            : (goal.date_ending - now()).days,
                                               'donations_amount'       : donations_amount,
                                               'donations_radiant'      : donations_radiant,
                                               'other_sources_radiant'  : other_sources_radiant,
                                               'total_percent'          : total_percent,
                                                    })
    #LINKED PROJECTS
    template_data['linked_projects'] = {}
    projects_i_depend_on_count, projects_depending_on_me_count = project.getLinkedProjectsCount()
    if projects_i_depend_on_count :
        template_data['linked_projects']['i_depend_on_transfer_percent'] = project.getRedonationsPercent()

    template_data['linked_projects']['i_depend_on_count'] = projects_i_depend_on_count
    template_data['linked_projects']['depending_on_me_count'] = projects_depending_on_me_count




    return render_to_response('project/view.djhtm', template_data, context_instance=RequestContext(request))

def chart_image(request, project_key, need_key=None, goal_key=None):
    return render_to_response('default.djhtm', {}, context_instance=RequestContext(request))

def linked_projects(request, project_key, need_key=None, goal_key=None):
    project = get_object_or_404(Project, key=project_key)

    template_data = {'project': project,
                     'request': request,
                     'today': datetime.utcnow().replace(tzinfo=utc).today(),
                     'site_currency_sign': SITE_CURRENCY_SIGN,
                     }

    projects_depending_on_me = (Project_Dependencies.objects
                                .filter(dependee_project=project.id)
                                .order_by('sort_order')
                                .prefetch_related('depender_project')
    )
    template_data['projects_depending_on_me'] = []
    template_data['projects_depending_on_me_count'] = projects_depending_on_me.count()
    #template_data['projects_depending_on_me'] = projects_depending_on_me
    for project_depending_on_me in projects_depending_on_me:
        template_data['projects_depending_on_me'].append({'id': project_depending_on_me.depender_project.id,
                                                          'key': project_depending_on_me.depender_project.key,
                                                          'title': project_depending_on_me.depender_project.title,
                                                          'logo': project_depending_on_me.depender_project.logo,
                                                          'amount_sum': project_depending_on_me.redonation_amount,
                                                          'amount_percent': project_depending_on_me.redonation_percent,
                                                          })

    projects_i_depend_on = (Project_Dependencies.objects
                            .filter(depender_project=project.id)
                            .order_by('sort_order')
                            .prefetch_related('dependee_project')
    )
    template_data['projects_i_depend_on'] = []
    template_data['projects_i_depend_on_count'] = projects_i_depend_on.count()
    for project_i_depend_on in projects_i_depend_on:
        template_data['projects_i_depend_on'].append({'id': project_i_depend_on.dependee_project.id,
                                                     'key': project_i_depend_on.dependee_project.key,
                                                     'title': project_i_depend_on.dependee_project.title,
                                                     'logo': project_i_depend_on.dependee_project.logo,
                                                     'amount_sum': project_i_depend_on.redonation_amount,
                                                     'amount_percent': project_i_depend_on.redonation_percent,
                                                     })


    return render_to_response('project/linked_projects.djhtm', template_data, context_instance=RequestContext(request))
