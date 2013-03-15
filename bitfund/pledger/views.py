from django.contrib.auth.models import User
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from bitfund.core.settings.project import SITE_CURRENCY_SIGN
from bitfund.pledger.template_helpers import _prepare_user_public_template_data, _prepare_user_pledges_monthly_history_data


def user_profile_overview(request, username=None, external_service=None, external_username=None):
    template_data = {'request': request,
                     'today': now().today(),
                     'site_currency_sign': SITE_CURRENCY_SIGN,
                     }

    if username is not None :
        user = get_object_or_404(User, username=username)

    elif external_service is not None and external_username is not None:
        user = None
        #@TODO identify user by external system ID and external username
    elif request.user.is_authenticated():
        user = request.user

    if user.id != request.user.id :
        user.public = _prepare_user_public_template_data(request, user)
        template_data['user'] = user

        return render_to_response('pledger/profile/public.djhtm', template_data, context_instance=RequestContext(request))
    else :
        request.user.public = _prepare_user_public_template_data(request, request.user)
        request.user.pledges_history = _prepare_user_pledges_monthly_history_data(request, request.user)
        template_data['request'] = request

        return render_to_response('pledger/profile/own_overview.djhtm', template_data, context_instance=RequestContext(request))


@login_required
def attach_card(request):
    return render_to_response('default.djhtm', {}, context_instance=RequestContext(request))
