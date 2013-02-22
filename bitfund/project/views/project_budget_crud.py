import math
from django.http import HttpResponseBadRequest

from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.utils.datetime_safe import datetime
from django.contrib.auth.decorators import login_required

from bitfund.core.settings.project import (SITE_CURRENCY_SIGN,
                                           BITFUND_OWN_PROJECT_ID,
                                           SESSION_PARAM_RETURN_TO_PROJECT,
                                           )
from bitfund.core.decorators import ajax_required
from bitfund.project.models import *
from bitfund.project.lists import DONATION_TYPES_CHOICES
from bitfund.project.forms import *
from bitfund.project.decorators import user_is_project_maintainer, user_is_not_project_maintainer
from bitfund.project.template_helpers import _prepare_need_item_template_data
from bitfund.pledger.models import DonationTransaction, DonationSubscription, DonationSubscriptionNeeds


@user_is_not_project_maintainer
def crud_pledge_need(request, project_key, need_id, action=None):
    if not request.user.is_authenticated :
        if request.is_ajax() :
            return HttpResponseBadRequest()
        else :
            return redirect('bitfund.core.login')

    project = get_object_or_404(Project, key=project_key)
    need = get_object_or_404(ProjectNeed, id=need_id)

    template_data = {'project': project,
                     'request': request,
                     'today': datetime.utcnow().replace(tzinfo=utc).today(),
                     'site_currency_sign': SITE_CURRENCY_SIGN,
                     }

    if request.method == 'POST' :
        if action == 'pledge' :
            pledge_need_form = PledgeProjectNeedForm(request.POST, prefix='need-'+str(need.id))
            if pledge_need_form.is_valid() :
                cleaned_pledge_type = pledge_need_form.cleaned_data['pledge_type']
                cleaned_pledge_amount = pledge_need_form.cleaned_data['pledge_amount']

                if cleaned_pledge_type == DONATION_TYPES_CHOICES.onetime :
                    transaction = DonationTransaction()
                    transaction.populatePledgeTransaction(project=project, user=request.user, need=need,
                                                          pledge_amount=cleaned_pledge_amount)
                    transaction.save()
                else :
                    existing_subscription_project = (DonationSubscription.objects
                                                     .filter(user=request.user, project=project)
                                                     .select_related())

                    if existing_subscription_project.count() == 1 :
                        existing_subscription_project = existing_subscription_project[0]
                        existing_subscription_project_need = (DonationSubscriptionNeeds.objects
                                                              .filter(donation_subscription=existing_subscription_project,
                                                                      need=need))
                        if existing_subscription_project_need.count() == 1 :
                            existing_subscription_project_need = existing_subscription_project_need[0]
                            existing_subscription_project_need.amount = cleaned_pledge_amount
                            existing_subscription_project_need.save()
                        else :
                            pledge_subscription_need = DonationSubscriptionNeeds()
                            pledge_subscription_need.donation_subscription = existing_subscription_project
                            pledge_subscription_need.need = need
                            pledge_subscription_need.amount = cleaned_pledge_amount
                            pledge_subscription_need.save()

                    else :
                        pledge_subscription = DonationSubscription()
                        pledge_subscription.user = request.user
                        pledge_subscription.project = project
                        pledge_subscription.save()

                        pledge_subscription_need = DonationSubscriptionNeeds()
                        pledge_subscription_need.donation_subscription = pledge_subscription
                        pledge_subscription_need.need = need
                        pledge_subscription_need.amount = cleaned_pledge_amount
                        pledge_subscription_need.save()

                    return redirect('bitfund.project.views.crud_pledge_need', project_key=project.key, need_id=need.id)
            else :
                template_data['need'] = _prepare_need_item_template_data(request, project, need, pledge_need_form)

            if not request.is_ajax() :
                #@TODO card presence check (along with the payment integration itself)
                if not request.user.is_card_attached :
                    request.session[SESSION_PARAM_RETURN_TO_PROJECT] = project.key
                    return redirect('bitfund.pledger.attach_card')
                else :
                    return redirect('bitfund.project.budget', project_key=project.key)

        elif action == 'drop_subscription' :
            existing_subscription_project = (DonationSubscription.objects
                                             .filter(user=request.user, project=project)
                                             .select_related())

            if existing_subscription_project.count() == 1 :
                existing_subscription_project = existing_subscription_project[0]
                existing_subscription_project_need = (DonationSubscriptionNeeds.objects
                                                      .filter(donation_subscription=existing_subscription_project,
                                                              need=need))
                if existing_subscription_project_need.count() == 1 :
                    existing_subscription_project_need = existing_subscription_project_need[0]
                    existing_subscription_project_need.delete()

                other_subscriptions_count = (DonationSubscriptionNeeds.objects
                                             .filter(donation_subscription=existing_subscription_project)
                                             .count())
                if other_subscriptions_count == 0 :
                    existing_subscription_project.delete()

            return redirect('bitfund.project.views.crud_pledge_need', project_key=project.key, need_id=need.id)

    if 'need' not in template_data:
        template_data['need'] = _prepare_need_item_template_data(request, project, need)

    return render_to_response('project/budget/ajax-pledge_need_form.djhtm', template_data, context_instance=RequestContext(request))

@ajax_required
@login_required
@user_is_project_maintainer
def crud_linked_project(request, project_key, linked_project_key=None, action=None):
    project = get_object_or_404(Project, key=project_key)

    template_data = {'project': project,
                     'request': request,
                     'today': datetime.utcnow().replace(tzinfo=utc).today(),
                     'site_currency_sign': SITE_CURRENCY_SIGN,
                     }

    if request.method == 'POST':
        if action == 'add' :
            linked_project_add_form = AddLinkedProjectForm(project.id, request.POST)
            if linked_project_add_form.is_valid():
                project_dependency = Project_Dependencies()
                project_dependency.depender_project = project
                project_dependency.dependee_project = linked_project_add_form.cleaned_data['linked_project']
                project_dependency.redonation_amount = (linked_project_add_form.cleaned_data['redonation_amount'] or None)
                project_dependency.redonation_percent = (linked_project_add_form.cleaned_data['redonation_percent'] or None)
                project_dependency.brief = (linked_project_add_form.cleaned_data['brief'] or None)
                project_dependency.save()

                return redirect('bitfund.project.views.crud_linked_project', project_key=project_key)
            else :
                template_data['crud_linked_project_add_form'] = linked_project_add_form
        elif action == 'edit' :
            linked_project = get_object_or_404(Project, key=linked_project_key)
            template_data['linked_project'] = linked_project
            linked_project_edit_form = EditLinkedProjectForm(project.id, linked_project.id, request.POST)
            if linked_project_edit_form.is_valid():
                project_dependency = (Project_Dependencies.objects.get(dependee_project__id=linked_project.id,
                                                                              depender_project__id=project.id))
                project_dependency.redonation_amount = Decimal(
                    (linked_project_edit_form.cleaned_data['redonation_amount'] or 0))
                project_dependency.redonation_percent = Decimal(
                    (linked_project_edit_form.cleaned_data['redonation_percent'] or 0))
                project_dependency.brief = (linked_project_edit_form.cleaned_data['brief'] or None)
                project_dependency.save()

                return redirect('bitfund.project.views.crud_linked_project', project_key=project_key)
            else :
                template_data['crud_linked_project_edit_form'] = linked_project_edit_form

    elif action == 'add' :
        template_data['crud_linked_project_add_form'] = AddLinkedProjectForm(project.id)
    elif linked_project_key is not None :
        linked_project = get_object_or_404(Project, key=linked_project_key)

        if action == 'drop' :
            (Project_Dependencies.objects.filter(dependee_project__id=linked_project.id)
             .filter(depender_project__id=project.id).delete())
        elif action == 'edit':
            linked_project_dependency = (Project_Dependencies.objects.get(dependee_project__id=linked_project.id,
                                                                          depender_project__id=project.id))
            template_data['linked_project'] = linked_project
            form_data = {'linked_project': linked_project,
                         'redonation_percent' : linked_project_dependency.redonation_percent,
                         'redonation_amount' : linked_project_dependency.redonation_amount,
                         'brief' : linked_project_dependency.brief,
                         }
            template_data['crud_linked_project_edit_form'] = EditLinkedProjectForm(project.id, linked_project.id, initial=form_data)

    if project.maintainer_id == request.user.id :
        template_data['project_edit_access'] = True
    else :
        template_data['project_edit_access'] = False

    template_data['giving_to_bitfund'] = project.checkProjectLinkedToBitFund()
    template_data['refused_to_give_to_bitfund'] = project.is_refused_to_give_to_bitfund

    projects_i_depend_on = (Project_Dependencies.objects
                            .filter(depender_project=project.id)
                            .order_by('sort_order')
                            .prefetch_related('dependee_project')
    )
    template_data['projects_i_depend_on'] = []
    template_data['projects_i_depend_on_count'] = projects_i_depend_on.count()
    for project_i_depend_on in projects_i_depend_on:
        if project_i_depend_on.dependee_project.is_public :
            template_data['projects_i_depend_on'].append({'id': project_i_depend_on.dependee_project.id,
                                                          'key': project_i_depend_on.dependee_project.key,
                                                          'title': project_i_depend_on.dependee_project.title,
                                                          'logo': project_i_depend_on.dependee_project.logo,
                                                          'brief': (project_i_depend_on.brief or ''),
                                                          'amount_sum': project_i_depend_on.redonation_amount,
                                                          'amount_percent': project_i_depend_on.redonation_percent,
                                                          })

    template_data['crud_linked_project_action'] = action

    return render_to_response('project/linked_projects/i_depend_on_projects_list.djhtm', template_data, context_instance=RequestContext(request))


@ajax_required
@login_required
@user_is_project_maintainer
def crud_bitfund_link(request, project_key, action):
    project = get_object_or_404(Project, key=project_key)
    bitfund = get_object_or_404(Project, id=BITFUND_OWN_PROJECT_ID)

    template_data = {'project': project,
                     'request': request,
                     'today': datetime.utcnow().replace(tzinfo=utc).today(),
                     'site_currency_sign': SITE_CURRENCY_SIGN,
                     }

    template_data['giving_to_bitfund'] = project.checkProjectLinkedToBitFund()

    if action == 'donate' :
        initial_data = {'linked_project': bitfund}
        template_data['crud_linked_project_add_form'] = AddLinkedProjectForm(project.id, initial=initial_data)
        template_data['giving_to_bitfund'] = True
        template_data['crud_linked_project_action'] = 'add'
        project.is_refused_to_give_to_bitfund = False
        project.save()
    elif action == 'refuse' :
        project.is_refused_to_give_to_bitfund = True
        project.save()

        return redirect('bitfund.project.views.crud_linked_project', project_key=project_key)


    if project.maintainer_id == request.user.id :
        template_data['project_edit_access'] = True
    else :
        template_data['project_edit_access'] = False

    template_data['refused_to_give_to_bitfund'] = project.is_refused_to_give_to_bitfund

    projects_i_depend_on = (Project_Dependencies.objects
                            .filter(depender_project=project.id)
                            .order_by('sort_order')
                            .prefetch_related('dependee_project')
    )
    template_data['projects_i_depend_on'] = []
    template_data['projects_i_depend_on_count'] = projects_i_depend_on.count()
    for project_i_depend_on in projects_i_depend_on:
        if project_i_depend_on.dependee_project.is_public :
            template_data['projects_i_depend_on'].append({'id': project_i_depend_on.dependee_project.id,
                                                          'key': project_i_depend_on.dependee_project.key,
                                                          'title': project_i_depend_on.dependee_project.title,
                                                          'logo': project_i_depend_on.dependee_project.logo,
                                                          'brief': (project_i_depend_on.brief or ''),
                                                          'amount_sum': project_i_depend_on.redonation_amount,
                                                          'amount_percent': project_i_depend_on.redonation_percent,
                                                          })

    return render_to_response('project/linked_projects/ajax-i_depend_on_projects_list.djhtm', template_data, context_instance=RequestContext(request))
