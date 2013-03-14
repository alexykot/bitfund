from django.contrib.auth.models import User
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from bitfund.core.settings.project import SITE_CURRENCY_SIGN
from bitfund.pledger.template_helpers import _prepare_user_public_template_data

@login_required
def user_own_profile(request):

    return render_to_response('pledger/profile/own_overview.djhtm', {}, context_instance=RequestContext(request))


def user_public_profile(request, username=None, external_service=None, external_username=None):
    if username is None :
        user = None
        #@TODO identify user by external system ID and external username
    else :
        user = get_object_or_404(User, username=username)

    if user.id == request.user.id :
        return redirect('bitfund.pledger.views.user_own_profile')



    user.public = _prepare_user_public_template_data(request, user)

    template_data = {'request': request,
                     'user': user,
                     'today': now().today(),
                     'site_currency_sign': SITE_CURRENCY_SIGN,
                     }





    return render_to_response('pledger/profile/public.djhtm', template_data, context_instance=RequestContext(request))

@login_required
def attach_card(request):
    return render_to_response('default.djhtm', {}, context_instance=RequestContext(request))
