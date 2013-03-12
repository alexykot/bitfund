import datetime
import math

from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.core.urlresolvers import reverse 
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.utils.datetime_safe import datetime
from django.utils.timezone import utc, now
from bitfund.core.settings.project import SITE_CURRENCY_SIGN
from bitfund.project.decorators import redirect_not_active, disallow_not_public_unless_maintainer, user_is_project_maintainer

from bitfund.project.models import *
from bitfund.project.forms import *
from bitfund.pledger.models import *
from bitfund.project.template_helpers import _prepare_goal_item_template_data


@redirect_not_active
@disallow_not_public_unless_maintainer
def goal_view(request, project_key, goal_key, action=None):
    project = get_object_or_404(Project, key=project_key)
    goal = get_object_or_404(ProjectGoal, key=goal_key)

    template_data = {'project' : project,
                     'request' : request,
                     'site_currency_sign': SITE_CURRENCY_SIGN,
                     'today'   : datetime.utcnow().replace(tzinfo=utc).today(),
                     }

    if project.maintainer_id == request.user.id :
        template_data['project_edit_access'] = True
    else :
        template_data['project_edit_access'] = False

    if request.method == 'POST' :
        pledge_form = PledgeProjectGoalForm(request.POST)
        if pledge_form.is_valid() :
            if action=='pledge':
                pledge_amount = pledge_form.cleaned_data['pledge_amount']

                existing_transactions_list = (DonationTransaction.objects
                                        .filter(accepting_project_id=project.id)
                                        .filter(accepting_goal_id=goal.id)
                                        .filter(pledger_user_id=request.user.id)
                                        .exclude(transaction_status=DONATION_TRANSACTION_STATUSES_CHOICES.cancelled)
                                        .exclude(transaction_status=DONATION_TRANSACTION_STATUSES_CHOICES.rejected)
                )

                if existing_transactions_list.count() > 0 :
                    for existing_transaction in existing_transactions_list :
                        existing_transaction.cancel()

                pledge_transaction = DonationTransaction()
                pledge_transaction.populatePledgeTransaction(project=project, user=request.user, pledge_amount=pledge_amount, goal=goal)
                pledge_transaction.save()
            elif action=='drop':
                existing_transactions_list = (DonationTransaction.objects
                                              .filter(accepting_project_id=project.id)
                                              .filter(accepting_goal_id=goal.id)
                                              .filter(pledger_user_id=request.user.id)
                                              .exclude(transaction_status=DONATION_TRANSACTION_STATUSES_CHOICES.cancelled)
                                              .exclude(transaction_status=DONATION_TRANSACTION_STATUSES_CHOICES.rejected)
                )

                if existing_transactions_list.count() > 0 :
                    for existing_transaction in existing_transactions_list :
                        existing_transaction.cancel()

            return redirect('bitfund.project.views.goal_view', project_key=project.key, goal_key=goal.key)
        else :
            template_data['goal'] = _prepare_goal_item_template_data(request, project, goal, pledge_form)

            return render_to_response('project/goals/goal.djhtm', template_data, context_instance=RequestContext(request))


    template_data['goal'] = _prepare_goal_item_template_data(request, project, goal)

    return render_to_response('project/goals/goal.djhtm', template_data, context_instance=RequestContext(request))


@login_required
@user_is_project_maintainer
def goal_toggle(request, project_key, goal_key):
    project = get_object_or_404(Project, key=project_key)
    goal = get_object_or_404(ProjectGoal, key=goal_key)

    if request.method == 'POST' :
        goal.is_public = not goal.is_public
        goal.save()

    return redirect('bitfund.project.views.goal_view', project_key=project.key, goal_key=goal_key)

